from abc import ABCMeta, abstractmethod, abstractproperty

class SOURCE_TYPE:
    MEMORY = 0
    FILE = 1
    STREAM = 2

class IOHandler(object):
    """Basic IO class

    >>> import tempfile
    >>> from path import path
    >>> from contextlib import contextmanager
    >>> @contextmanager
    ... def temp_dir():
    ...  tmp = path(tempfile.mkdtemp())
    ...  try:
    ...      yield tmp
    ...  finally:
    ...      tmp.rmtree()
    >>>
    >>> # Test starts here
    >>> with temp_dir() as tmp:
    ...     ioh = IOHandler()
    ...     assert isinstance(ioh, IOHandler)

    """

    def __init__(self):
        self.source_type = None

    def set_file(self, filename):
        self.source_type = SOURCE_TYPE.FILE

    def set_memory_object(self, memory_object):
        self.source_type = SOURCE_TYPE.MEMORY

    def set_stream(self, stream):
        self.source_type = SOURCE_TYPE.STREAM

    def get_file(self):
        raise Exception("set file not implemented")

    def get_memory_object(self):
        raise Exception("setmemory_object not implemented")

    def get_stream(self):
        raise Exception("setstream not implemented")

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
