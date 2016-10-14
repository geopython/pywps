##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


import logging
import os
from abc import ABCMeta, abstractmethod
from pywps._compat import urljoin
from pywps.exceptions import NotEnoughStorage
from pywps import configuration as config

LOGGER = logging.getLogger('PYWPS')


class STORE_TYPE:
    PATH = 0
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
        pass


class DummyStorage(StorageAbstract):
    """Dummy empty storage implementation, does nothing

    Default instance, for non-reference output request

    >>> store = DummyStorage()
    >>> assert store.store
    """

    def __init__(self):
        """
        """

    def store(self, ouput):
        pass


class FileStorage(StorageAbstract):
    """File storage implementation, stores data to file system

    >>> import ConfigParser
    >>> config = ConfigParser.RawConfigParser()
    >>> config.add_section('FileStorage')
    >>> config.set('FileStorage', 'target', './')
    >>> config.add_section('server')
    >>> config.set('server', 'outputurl', 'http://foo/bar/filestorage')
    >>>
    >>> store = FileStorage()
    >>>
    >>> class FakeOutput(object):
    ...     def __init__(self):
    ...         self.file = self._get_file()
    ...     def _get_file(self):
    ...         tiff_file = open('file.tiff', 'w')
    ...         tiff_file.close()
    ...         return 'file.tiff'
    >>> fake_out = FakeOutput()
    >>> (type, path, url) = store.store(fake_out)
    >>> type == STORE_TYPE.PATH
    True
    """

    def __init__(self):
        """
        """
        self.target = config.get_config_value('server', 'outputpath')
        self.output_url = config.get_config_value('server', 'outputurl')

    def store(self, output):
        import math
        import shutil
        import tempfile

        file_name = output.file

        file_block_size = os.stat(file_name).st_blksize
        # get_free_space delivers the numer of free blocks, not the available size!
        avail_size = get_free_space(self.target) * file_block_size
        file_size = os.stat(file_name).st_size

        # calculate space used according to block size
        actual_file_size = math.ceil(file_size / float(file_block_size)) * file_block_size

        if avail_size < actual_file_size:
            raise NotEnoughStorage('Not enough space in %s to store %s' % (self.target, file_name))

        (prefix, suffix) = os.path.splitext(file_name)
        if not suffix:
            suffix = output.output_format.extension
        (file_dir, file_name) = os.path.split(prefix)
        output_name = tempfile.mkstemp(suffix=suffix, prefix=file_name,
                                       dir=self.target)[1]

        full_output_name = os.path.join(self.target, output_name)
        LOGGER.info('Storing file output to %s', full_output_name)
        shutil.copy2(output.file, full_output_name)

        just_file_name = os.path.basename(output_name)

        url = urljoin(self.output_url, just_file_name)
        LOGGER.info('File output URI: %s', url)

        return (STORE_TYPE.PATH, output_name, url)


def get_free_space(folder):
    """ Return folder/drive free space (in bytes)
    """
    import platform

    if platform.system() == 'Windows':
        import ctypes

        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        free_space = free_bytes.value
    else:
        free_space = os.statvfs(folder).f_bfree

    LOGGER.debug('Free space: %s', free_space)
    return free_space
