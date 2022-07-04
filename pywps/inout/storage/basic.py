##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
import uuid

import pywps.configuration
import pywps.dblog

# Allow to store, create and convert storage
_storage_type_registry = {}


# register the given class as storage
def register_storage_type(cls):
    global _storage_type_registry
    _storage_type_registry[cls.__name__] = cls
    return cls


# Return a fresh storage of given typename or the default one
def new_storage(type=None):
    global _storage_type_registry
    if type is None:
        type = pywps.configuration.get_config_value('server', 'storagetype', "DatabaseStorage")
    return _storage_type_registry[type]()


# Return a Storage that handle the given uuid or None if not found.
def get_storage_instance(uuid):
    global _storage_type_registry
    store_instance_record = pywps.dblog.get_storage_record(uuid)
    if store_instance_record:
        return _storage_type_registry[store_instance_record.type](
            uuid=store_instance_record.uuid,
            pretty_filename=store_instance_record.pretty_filename,
            mimetype=store_instance_record.mimetype,
            data=store_instance_record.data
        )
    return None


class StorageAbstract(object):
    """Data storage abstract class
    """

    def __init__(self, **kwargs):

        if "uuid" in kwargs:
            self._uuid = uuid.UUID(kwargs["uuid"])
            self._pretty_filename = kwargs.get("pretty_filename", None)
            self._mimetype = kwargs.get("mimetype", None)
            self.load(kwargs.get("data", b''))
        else:
            # Given uuid to the store
            self._uuid = uuid.uuid1()

            # Will be set only when export is made
            self._pretty_filename = None
            self._mimetype = None

    def open(self, mode="r", encoding=None):
        """
        Return file object like handler
        """
        raise NotImplementedError

    def export(self, pretty_filename, mimetype):
        """
        Export this file to be available from web
        """
        self._pretty_filename = pretty_filename
        self._mimetype = mimetype

        pywps.dblog.update_storage_record(self)
        return self.url

    def unexport(self):
        self.export(None, None)

    @property
    def uuid(self):
        return self._uuid

    @property
    def pretty_filename(self):
        return self._pretty_filename

    @property
    def mimetype(self):
        return self._mimetype

    @property
    def url(self):
        """Build and return the exported url"""
        base_url = pywps.configuration.get_config_value('server', 'url').rstrip('/')
        return f"{base_url}/files?uuid={self.uuid}"

    def dump(self):
        """Dump data into bytes array"""
        raise NotImplementedError

    def load(self, bytes):
        """Load bytes array"""
        raise NotImplementedError
