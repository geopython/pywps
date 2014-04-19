from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = ['literalvalidator', 'complexvalidator']

class MODE(object):
    """Validation modes

    NONE: always true
    SIMPLE: mimeType check
    STRICT: can be opened using standard library (e.g. GDAL)
    VERYSTRICT: Schema passes
    """

    NONE = 0
    SIMPLE = 1
    STRICT = 2
    VERYSTRICT = 3

class ValidatorAbstract(object):
    """Data validator abstract class
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, input, level=MODE.VERYSTRICT):
        """Perform input validation
        """
        True
