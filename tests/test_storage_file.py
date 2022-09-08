##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
import pytest

# Needed to load default configuration
from pywps import configuration
from pywps.inout.storage import new_storage, get_storage_instance
from pywps.inout.storage.file import FileStorage


class TestFileStorageBuilder():

    def test_default_storage(self):
        storage = new_storage("FileStorage")
        assert isinstance(storage, FileStorage)

    def test_store_database_storage_binary(self):
        storage = new_storage("FileStorage")

        # Write some data
        with storage.open("w") as f:
            f.write(b'somedata')

        # Read data from storage
        with storage.open("r") as f:
            data = f.read()
            assert data == b'somedata'

        # Retreive data from database
        xstorage = get_storage_instance(storage.uuid)
        assert isinstance(xstorage, FileStorage)

        # Read data from storage
        with xstorage.open("r") as f:
            data = f.read()
            assert data == b'somedata'

    def test_store_database_storage_string(self):
        storage = new_storage("FileStorage")

        # Write some data
        with storage.open("w", "utf-8") as f:
            f.write('somedata')

        # Read data from storage
        with storage.open("r", "utf-8") as f:
            data = f.read()
            assert data == 'somedata'

        # Retreive data from database
        xstorage = get_storage_instance(storage.uuid)
        assert isinstance(xstorage, FileStorage)

        # Read data from storage
        with xstorage.open("r", "utf-8") as f:
            data = f.read()
            assert data == 'somedata'
