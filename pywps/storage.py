from abc import ABCMeta, abstractmethod, abstractproperty
import os

class STORE_TYPE:
    PATH = 0
# TODO: cover with tests
class StorageAbstract(object):
    """Data storage abstract class
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def store(self):
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

    def __init__(self, config=None):
        """
        :param config: storage configuration object
        """
        self.config = config

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
    >>> store = FileStorage(config = config)
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

    def __init__(self, config):
        """
        :param config: storage configuration object
        """
        self.target = config.get_config_value('server', 'outputPath')
        self.outputurl = config.get_config_value('wps', 'serveraddress') + config.get_config_value('server', 'outputUrl')

    def store(self, output):
        import shutil, tempfile
        from urlparse import urljoin
        file_name = output.file
        (prefix, suffix) = os.path.splitext(file_name)
        if not suffix:
            suffix = output.output_format.get_extension()
        (file_dir, file_name) = os.path.split(prefix)
        output_name = tempfile.mkstemp(suffix=suffix, prefix=file_name,
                                       dir=self.target)[1]

        shutil.copy2(output.file, os.path.join(self.target, output_name))

        just_file_name = os.path.basename(output_name)
        url = urljoin(self.outputurl, just_file_name)

        return (STORE_TYPE.PATH, output_name, url)
