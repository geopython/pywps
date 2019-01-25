##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps.inout.storage.builder import StorageBuilder
from pywps.inout.storage.file import FileStorage
from pywps.inout.storage.s3 import S3Storage

from pywps import configuration

import unittest

class StorageBuilderTests(unittest.TestCase):

    def test_default_storage(self):
        storage = StorageBuilder.buildStorage()
        self.assertIsInstance(storage, FileStorage)


    def test_s3_storage(self):
        configuration.CONFIG.set('server', 'storagetype', 's3')
        storage = StorageBuilder.buildStorage()
        self.assertIsInstance(storage, S3Storage)

def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(StorageBuilderTests)
    ]
    return unittest.TestSuite(suite_list)