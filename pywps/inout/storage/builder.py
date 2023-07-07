##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import pywps.configuration as wpsConfig  # noqa

from .file import FileStorageBuilder
from .s3 import S3StorageBuilder

STORAGE_MAP = {
    's3': S3StorageBuilder,
    'file': FileStorageBuilder
}


class StorageBuilder:
    """
    Class to construct other storage classes using
    the server configuration to determine the appropriate type.
    Will default to using FileStorage if the specified type
    cannot be found
    """
    @staticmethod
    def buildStorage():
        """
        :returns: A StorageAbstract conforming object for storing
                  outputs that has been configured using the server
                  configuration
        """
        storage_type = wpsConfig.get_config_value('server', 'storagetype').lower()
        if storage_type not in STORAGE_MAP:
            return FileStorageBuilder().build()
        else:
            return STORAGE_MAP[storage_type]().build()
