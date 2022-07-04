##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from .basic import StorageAbstract, register_storage_type

import pywps.configuration
from pywps.exceptions import StorageNotSupported, NoApplicableCode
import os
import pywps.dblog


@register_storage_type
class FileStorage(StorageAbstract):
    """Store data into file in the directory 'server' 'outputpath'
    """

    def __init__(self, **kwargs):
        self._path = None
        super().__init__(**kwargs)

        if self._path is None:
            outputpath = pywps.configuration.get_config_value('server', 'outputpath', None)
            if outputpath is None:
                raise NoApplicableCode("Configuration [server] outputpath is missing", code=500)
            self._path = os.path.join(outputpath, str(self.uuid))

    def open(self, mode, encoding=None):
        if encoding is None:
            if mode == "w":
                pywps.dblog.update_storage_record(self)
                return open(self._path, "wb")
            else:
                return open(self._path, "rb")
        else:
            if mode == "w":
                pywps.dblog.update_storage_record(self)
                return open(self._path, "w", encoding=encoding)
            else:
                return open(self._path, "r", encoding=encoding)

    def dump(self):
        return self._path.encode("utf-8")

    def load(self, bytes):
        self._path = bytes.decode("utf-8")
