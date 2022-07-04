##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from .basic import StorageAbstract, register_storage_type

import base64
import io

import pywps.dblog


class DatabaseStorageByteHandler(io.BytesIO):
    def __init__(self, ds, initial_bytes=b''):
        super(DatabaseStorageByteHandler, self).__init__(initial_bytes)
        self._ds = ds

    def flush(self):
        super(DatabaseStorageByteHandler, self).flush()
        self._ds.store(self.getvalue())

    # Override close
    def close(self):
        self._ds.store(self.getvalue())
        super(DatabaseStorageByteHandler, self).close()

    def __exit__(self, *args, **kwargs):
        self._ds.store(self.getvalue())
        super(DatabaseStorageByteHandler, self).__exit__(*args, **kwargs)


class DatabaseStorageStringHandler(io.StringIO):
    def __init__(self, ds, encoding, initial_value=""):
        super(DatabaseStorageStringHandler, self).__init__(initial_value)
        self._ds = ds
        self._encoding = encoding

    def flush(self):
        super(DatabaseStorageStringHandler, self).flush()
        self._ds.store(self.getvalue().encode(self._encoding))

    # Override close
    def close(self):
        self._ds.store(self.getvalue().encode(self._encoding))
        super(DatabaseStorageStringHandler, self).close()

    def __exit__(self, *args, **kwargs):
        self._ds.store(self.getvalue().encode(self._encoding))
        super(DatabaseStorageStringHandler, self).__exit__(*args, **kwargs)


@register_storage_type
class DatabaseStorage(StorageAbstract):
    """Database storage will put data in base64 within the database
    """

    def __init__(self, **kwargs):
        self._data = b''
        super().__init__(**kwargs)

    def open(self, mode, encoding=None):
        if encoding is None:
            if mode == "w":
                return DatabaseStorageByteHandler(self)
            else:
                return DatabaseStorageByteHandler(self, self._data)
        else:
            if mode == "w":
                return DatabaseStorageStringHandler(self, encoding)
            else:
                return DatabaseStorageStringHandler(self, encoding, self._data.decode(encoding))

    def store(self, bytes):
        self._data = bytes
        pywps.dblog.update_storage_record(self)

    def dump(self):
        return self._data

    def load(self, bytes):
        self._data = bytes
