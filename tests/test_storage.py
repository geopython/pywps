##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
from basic import TestBase
import pytest

from pywps.inout.storage.builder import StorageBuilder
from pywps.inout.storage.file import FileStorage
from pywps.inout.storage.s3 import S3Storage

from pywps import configuration

from pathlib import Path

import os

class FakeOutput(object):
    """Fake output object for testing."""

    def __init__(self, tmp_path):
        self.identifier = "fake_output"
        fn = Path(tmp_path) / "file.tiff"
        fn.touch()
        self.file = str(fn.absolute())
        self.uuid = None


class TestDefaultStorageBuilder(TestBase):

    def test_default_storage(self):
        storage = StorageBuilder.buildStorage()
        assert isinstance(storage, FileStorage)


class TestS3StorageBuilder(TestBase):

    def setUp(self) -> None:
        super().setUp()
        configuration.CONFIG.set('server', 'storagetype', 's3')

    def test_s3_storage(self):
        storage = StorageBuilder.buildStorage()
        assert isinstance(storage, S3Storage)


class TestFileStorageBuilder(TestBase):

    def setUp(self) -> None:
        super().setUp()
        configuration.CONFIG.set('server', 'storagetype', 'file')
        self.opath = os.path.join(self.tmpdir.name, "a", "b", "c")
        configuration.CONFIG.set('server', 'outputpath', self.opath)

    def test_recursive_directory_creation(self):
        """Test that outputpath is created."""
        storage = StorageBuilder.buildStorage()
        fn = FakeOutput(self.tmpdir.name)
        storage.store(fn)
        assert os.path.exists(self.opath)
