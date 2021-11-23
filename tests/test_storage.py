##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
import pytest

from pywps.inout.storage.builder import StorageBuilder
from pywps.inout.storage.file import FileStorage
from pywps.inout.storage.s3 import S3Storage

from pywps import configuration

from pathlib import Path
import unittest
import tempfile


@pytest.fixture
def fake_output(tmp_path):
    class FakeOutput(object):
        """Fake output object for testing."""
        def __init__(self):
            self.identifier = "fake_output"
            self.file = self._get_file()
            self.uuid = None

        def _get_file(self):
            fn = tmp_path / 'file.tiff'
            fn.touch()
            return str(fn.absolute())

    return FakeOutput()


class TestStorageBuilder():

    def test_default_storage(self):
        storage = StorageBuilder.buildStorage()
        assert isinstance(storage, FileStorage)

    def test_s3_storage(self):
        configuration.CONFIG.set('server', 'storagetype', 's3')
        storage = StorageBuilder.buildStorage()
        assert isinstance(storage, S3Storage)

    def test_recursive_directory_creation(self, fake_output):
        """Test that outputpath is created."""
        configuration.CONFIG.set('server', 'storagetype', 'file')
        outputpath = Path(tempfile.gettempdir()) / "a" / "b" / "c"
        configuration.CONFIG.set('server', 'outputpath', str(outputpath))
        storage = StorageBuilder.buildStorage()

        storage.store(fake_output)
        assert outputpath.exists()
