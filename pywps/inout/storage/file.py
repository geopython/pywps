##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
import os
from pywps._compat import urljoin
from pywps.exceptions import NotEnoughStorage
from pywps import configuration as config
from pywps.inout.basic import IOHandler

from . import CachedStorage
from .implementationbuilder import StorageImplementationBuilder
from . import STORE_TYPE

LOGGER = logging.getLogger('PYWPS')


class FileStorageBuilder(StorageImplementationBuilder):

    def build(self):
        file_path = config.get_config_value('server', 'outputpath')
        base_url = config.get_config_value('server', 'outputurl')
        return FileStorage(file_path, base_url)


def _build_output_name(output):
    (prefix, suffix) = os.path.splitext(output.file)
    if not suffix:
        suffix = output.data_format.extension
    _, file_name = os.path.split(prefix)
    output_name = file_name + suffix
    return (output_name, suffix)


class FileStorage(CachedStorage):
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

    def __init__(self, output_path, output_url):
        """
        """
        CachedStorage.__init__(self)
        self.target = output_path
        self.output_url = output_url

    def _do_store(self, output):
        import platform
        import math
        import shutil
        import tempfile
        import uuid

        file_name = output.file

        request_uuid = output.uuid or uuid.uuid1()

        # st.blksize is not available in windows, skips the validation on windows
        if platform.system() != 'Windows':
            file_block_size = os.stat(file_name).st_blksize
            # get_free_space delivers the numer of free blocks, not the available size!
            avail_size = get_free_space(self.target) * file_block_size
            file_size = os.stat(file_name).st_size

            # calculate space used according to block size
            actual_file_size = math.ceil(file_size / float(file_block_size)) * file_block_size

            if avail_size < actual_file_size:
                raise NotEnoughStorage('Not enough space in {} to store {}'.format(self.target, file_name))

        # create a target folder for each request
        target = os.path.join(self.target, str(request_uuid))
        if not os.path.exists(target):
            os.makedirs(target)

        # build output name
        output_name, suffix = _build_output_name(output)
        # build tempfile in case of duplicates
        if os.path.exists(os.path.join(target, output_name)):
            output_name = tempfile.mkstemp(suffix=suffix, prefix=file_name + '_',
                                           dir=target)[1]

        full_output_name = os.path.join(target, output_name)
        LOGGER.info('Storing file output to {}'.format(full_output_name))
        shutil.copy2(output.file, full_output_name)

        just_file_name = os.path.basename(output_name)

        url = self.url("{}/{}".format(request_uuid, just_file_name))
        LOGGER.info('File output URI: {}'.format(url))

        return (STORE_TYPE.PATH, output_name, url)

    def write(self, data, destination, data_format=None):
        """
        Write data to self.target
        """
        if not os.path.exists(os.path.dirname(self.target)):
            os.makedirs(self.target)

        full_output_name = os.path.join(self.target, destination)

        with open(full_output_name, "w") as file:
            file.write(data)

        return self.url(destination)

    def url(self, destination):
        if isinstance(destination, IOHandler):
            output_name, _ = _build_output_name(destination)
            just_file_name = os.path.basename(output_name)
            dst = "{}/{}".format(destination.uuid, just_file_name)
        else:
            dst = destination

        # make sure base url ends with '/'
        baseurl = self.output_url.rstrip('/') + '/'
        url = urljoin(baseurl, dst)
        return url

    def location(self, destination):
        return os.path.join(self.target, destination)


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

    LOGGER.debug('Free space: {}'.format(free_space))
    return free_space
