##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
from pathlib import Path

from pywps.inout.storage.file import FileStorageBuilder, FileStorage, _build_output_name
from pywps.inout.storage import STORE_TYPE
from pywps.inout.basic import ComplexOutput
from pywps.util import file_uri

from pywps import configuration, FORMATS

import tempfile

import unittest


class FileStorageTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def test_build_output_name(self):
        storage = FileStorageBuilder().build()
        output = ComplexOutput('testme', 'Test', supported_formats=[FORMATS.TEXT], workdir=self.tmp_dir)
        output.data = "Hello World!"
        output_name, suffix = _build_output_name(output)
        self.assertEqual(output.file, str(Path(self.tmp_dir) / 'input.txt'))
        self.assertEqual(output_name, 'input.txt')
        self.assertEqual(suffix, '.txt')

    def test_store(self):
        configuration.CONFIG.set('server', 'outputpath', self.tmp_dir)
        storage = FileStorageBuilder().build()
        output = ComplexOutput('testme', 'Test', supported_formats=[FORMATS.TEXT], workdir=self.tmp_dir)
        output.data = "Hello World!"
        store_type, store_str, url = storage.store(output)

        self.assertEqual(store_type, STORE_TYPE.PATH)
        self.assertEqual(store_str, 'input.txt')

        with open(Path(self.tmp_dir) / store_str) as f:
            self.assertEqual(f.read(), "Hello World!")

    def test_write(self):
        configuration.CONFIG.set('server', 'outputpath', self.tmp_dir)
        configuration.CONFIG.set('server', 'outputurl', file_uri(self.tmp_dir))
        storage = FileStorageBuilder().build()
        output = ComplexOutput('testme', 'Test', supported_formats=[FORMATS.TEXT], workdir=self.tmp_dir)
        output.data = "Hello World!"
        url = storage.write(output.data, 'foo.txt')

        fname = Path(self.tmp_dir) / 'foo.txt'
        self.assertEqual(url, file_uri(fname))
        with open(fname) as f:
            self.assertEqual(f.read(), "Hello World!")

    def test_url(self):
        configuration.CONFIG.set('server', 'outputpath', self.tmp_dir)
        configuration.CONFIG.set('server', 'outputurl', file_uri(self.tmp_dir))
        storage = FileStorageBuilder().build()
        output = ComplexOutput('testme', 'Test', supported_formats=[FORMATS.TEXT], workdir=self.tmp_dir)
        output.data = "Hello World!"
        output.uuid = '595129f0-1a6c-11ea-a30c-acde48001122'
        url = storage.url(output)

        fname = Path(self.tmp_dir) / '595129f0-1a6c-11ea-a30c-acde48001122' / 'input.txt'
        self.assertEqual(file_uri(fname), url)

        file_name = 'test.txt'
        url = storage.url(file_name)
        fname = Path(self.tmp_dir) / 'test.txt'
        self.assertEqual(file_uri(fname), url)

    def test_location(self):
        configuration.CONFIG.set('server', 'outputpath', self.tmp_dir)
        storage = FileStorageBuilder().build()
        file_name = 'test.txt'
        loc = storage.location(file_name)
        fname = Path(self.tmp_dir) / 'test.txt'
        self.assertEqual(str(fname), loc)


def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(FileStorageTests)
    ]
    return unittest.TestSuite(suite_list)
