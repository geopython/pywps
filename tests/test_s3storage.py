##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps.inout.storage.s3 import S3StorageBuilder, S3Storage
from pywps.inout.storage import STORE_TYPE
from pywps.inout.basic import ComplexOutput

from pywps import configuration, FORMATS
from pywps._compat import urlparse, PY2

import tempfile
import os

import unittest
if PY2:
    from mock import patch
else:
    from unittest.mock import patch

class S3StorageTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()


    @patch('pywps.inout.storage.s3.S3Storage.uploadData')
    def test_store(self, uploadData):
        configuration.CONFIG.set('s3', 'bucket', 'notrealbucket')
        configuration.CONFIG.set('s3', 'prefix', 'wps')
        storage = S3StorageBuilder().build()
        output = ComplexOutput('testme', 'Test', supported_formats=[FORMATS.TEXT], workdir=self.tmp_dir)
        output.data = "Hello World!"

        store_type, filename, url = storage.store(output)

        called_args = uploadData.call_args[0]

        self.assertEqual(store_type, STORE_TYPE.S3)
        self.assertEqual(filename, 'wps/input.txt')

        self.assertEqual(uploadData.call_count, 1)
        self.assertEqual(called_args[1], 'wps/input.txt')
        self.assertEqual(called_args[2], {'ContentType': 'text/plain'})

    @patch('pywps.inout.storage.s3.S3Storage.uploadData')
    def test_write(self, uploadData):
        configuration.CONFIG.set('s3', 'bucket', 'notrealbucket')
        configuration.CONFIG.set('s3', 'prefix', 'wps')
        storage = S3StorageBuilder().build()

        url = storage.write('Bar Baz', 'out.txt', data_format=FORMATS.TEXT)

        called_args = uploadData.call_args[0]

        self.assertEqual(uploadData.call_count, 1)
        self.assertEqual(called_args[0], 'Bar Baz')
        self.assertEqual(called_args[1], 'wps/out.txt')
        self.assertEqual(called_args[2], {'ContentType': 'text/plain'})


def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(S3StorageTests)
    ]
    return unittest.TestSuite(suite_list)