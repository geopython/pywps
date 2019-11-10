##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
import os
from abc import ABCMeta, abstractmethod

LOGGER = logging.getLogger('PYWPS')


class STORE_TYPE:
    PATH = 0
    S3 = 1
# TODO: cover with tests


class StorageAbstract(object):
    """Data storage abstract class
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def store(self, output):
        """
        :param output: of type IOHandler
        :returns: (type, store, url) where
            type - is type of STORE_TYPE - number
            store - string describing storage - file name, database connection
            url - url, where the data can be downloaded
        """
        raise NotImplementedError

    @abstractmethod
    def write(self, data, destination, data_format=None):
        """
        :param data: data to write to storage
        :param destination: identifies the destination to write to storage
                            generally a file name which can be interpreted
                            by the implemented Storage class in a manner of
                            its choosing
        :param data_format: Optional parameter of type pywps.inout.formats.FORMAT
                       describing the format of the data to write.
        :returns: url where the data can be downloaded
        """
        raise NotImplementedError

    @abstractmethod
    def url(self, destination):
        """
        :param destination: the name of the output to calculate
                            the url for
        :returns: URL where file_name can be reached
        """
        raise NotImplementedError

    @abstractmethod
    def location(self, destination):
        """
        Provides a location for the specified destination.
        This may be any path, pathlike object, db connection string, URL, etc
        and it is not guaranteed to be accessible on the local file system
        :param destination: the name of the output to calculate
                            the location for
        :returns: location where file_name can be found
        """
        raise NotImplementedError


class CachedStorage(StorageAbstract):
    def __init__(self):
        self._cache = {}

    def store(self, output):
        if output.identifier not in self._cache:
            self._cache[output.identifier] = self._do_store(output)
        return self._cache[output.identifier]

    def _do_store(self, output):
        raise NotImplementedError


class DummyStorage(StorageAbstract):
    """Dummy empty storage implementation, does nothing

    Default instance, for non-reference output request

    >>> store = DummyStorage()
    >>> assert store.store
    """

    def __init__(self):
        """
        """

    def store(self, output):
        pass
