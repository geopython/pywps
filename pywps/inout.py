from abc import ABCMeta, abstractmethod, abstractproperty

class SOURCE_TYPE:
    MEMORY = 0
    FILE = 1
    STREAM = 2

class IOHandler(object):
    """Basic IO class. Provides functions, to accept input data in file,
    memory object and stream object and give them out in all three types

    >>> # setting up tempory directory for testing environment
    >>> import tempfile, os
    >>> from io import RawIOBase
    >>> from path import path
    >>> from contextlib import contextmanager
    >>> from io import FileIO
    >>> import types
    >>>
    >>> @contextmanager
    ... def temp_dir():
    ...     "Create temoprary directory"
    ...     tmp = path(tempfile.mkdtemp())
    ...     try:
    ...         yield tmp
    ...     finally:
    ...         tmp.rmtree()
    >>> #
    >>> # Test starts here
    >>> #
    >>> with temp_dir() as tmp:
    ...     ioh_file = IOHandler(tempdir=tmp)
    ...     assert isinstance(ioh_file, IOHandler)
    ...
    ...     # Create test file input
    ...     fileobj = open(os.path.join(tmp, 'myfile.txt'), 'w')
    ...     fileobj.write('ASDF ASFADSF ASF ASF ASDF ASFASF')
    ...     fileobj.close()
    ...
    ...     # testing file object on input
    ...     ioh_file.set_file(fileobj.name)
    ...     assert ioh_file.source_type == SOURCE_TYPE.FILE
    ...     file = ioh_file.get_file()
    ...     stream = ioh_file.get_stream()
    ...
    ...     assert file == fileobj.name
    ...     assert isinstance(stream, RawIOBase)
    ...     # skipped assert isinstance(ioh_file.get_object(), POSH)
    ...
    ...     # testing stream object on input
    ...     ioh_stream = IOHandler(tempdir=tmp)
    ...     assert ioh_stream.tempdir == tmp
    ...     ioh_stream.set_stream(FileIO(fileobj.name,'r'))
    ...     assert ioh_stream.source_type == SOURCE_TYPE.STREAM
    ...     file = ioh_stream.get_file()
    ...     stream = ioh_stream.get_stream()
    ...
    ...     assert isinstance(file, types.StringType)
    ...     assert open(file).read() == ioh_file.get_stream().read()
    ...     assert isinstance(stream, RawIOBase)
    ...     # skipped assert isinstance(ioh_stream.get_object(), POSH)
    ...
    ...     # testing in memory object object on input
    ...     # skipped ioh_mo = IOHandler(tempdir=tmp)
    ...     # skipped ioh_mo.set_memory_object(POSH)
    ...     # skipped assert ioh_mo.source_type == SOURCE_TYPE.MEMORY
    ...     # skipped file = ioh_mo.get_file()
    ...     # skipped stream = ioh_mo.get_stream()
    ...     # skipped posh = ioh_mo.get_memory_object()
    ...     #
    ...     # skipped assert isinstance(file, types.StringType)
    ...     # skipped assert open(file).read() == ioh_file.get_stream().read()
    ...     # skipped assert isinstance(ioh_mo.get_stream(), RawIOBase)
    ...     # skipped assert isinstance(ioh_mo.get_object(), POSH)
    """

    def __init__(self, tempdir=None):
        self.source_type = None
        self.source = None
        self.tempdir = tempdir

    def set_file(self, filename):
        self.source_type = SOURCE_TYPE.FILE
        self.source = filename

    def set_memory_object(self, memory_object):
        self.source_type = SOURCE_TYPE.MEMORY

    def set_stream(self, stream):
        self.source_type = SOURCE_TYPE.STREAM
        self.source = stream

    def get_file(self):
        if self.source_type == SOURCE_TYPE.FILE:
            return self.source
        elif self.source_type == SOURCE_TYPE.STREAM:
            import tempfile
            (opening, stream_file_name) = tempfile.mkstemp(dir=self.tempdir)
            stream_file = open(stream_file_name, 'w')
            stream_file.write(self.source.read())
            stream_file.close()
            return str(stream_file_name)


    def get_memory_object(self):
        raise Exception("setmemory_object not implemented, Soeren promissed to implement at WPS Workshop on 23rd of January 2014")

    def get_stream(self):
        if self.source_type == SOURCE_TYPE.FILE:
            from io import FileIO
            return FileIO(self.source, mode='r', closefd=True)
        elif self.source_type == SOURCE_TYPE.STREAM:
            return self.source

    # Properties
    file = property(fget=get_file, fset=set_file)
    memory_object = property(fget=get_memory_object, fset=set_memory_object)
    stream = property(fget=get_stream, fset=set_stream)

class ComplexInput(IOHandler):
    """Complex input abstract class

    >>> ci = ComplexInput()
    >>> ci.set_validator(1)
    >>> ci.get_validator()
    1
    """

    def set_validator(self, validator):
        self._validator = validator

    def get_validator(self):
        return self._validator

    validator = property(fget=get_validator, fset=set_validator)

    def get_file(self):
        filename = IOHandler.get_file(self)
        if self.validator:
            self.validator.validate_file(filename)
        return filename


class ComplexOutput(IOHandler):
    """Complex output abstract class

    >>> co = ComplexOutput()
    >>> co.set_storage(1)
    >>> co.get_storage()
    1
    """

    def set_storage(self, storage):
        """Set output storage
        """
        self._storage = storage

    def get_storage(self):
        """Get output storage
        """
        return self._storage

    storage = property(fget=get_storage, fset=set_storage)

class ValidatorAbstract(object):
    """Data validator abstract class
    """

    __metaclass__ = ABCMeta


    def set_input(self):
        """Perform input validation
        """
        pass

    @abstractmethod
    def validate(self):
        """Perform input validation
        """
        pass

class StorageAbstract(object):
    """Data storage abstract class
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def store(self):
        """Store the data
        """
        pass

    def store(self):
        """Store the data
        """
        pass

class DummyStorage(StorageAbstract):
    """Dummy empty storage implementation, does nothing

    Default instance, for non-reference output request
    """

    def __init__(self, config):
        """
        :param config: storage configuration object
        """

    def store(self):
        pass

class FileStorage(StorageAbstract):
    """File storage implementation, stores data to file system
    """

    def __init__(self, config):
        """
        :param config: storage configuration object
        """

    def store(self):
        pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
