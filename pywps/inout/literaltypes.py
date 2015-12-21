"""Literaltypes are used for LiteralInputs, to make sure, input data are OK
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from pywps._compat import urlparse
import time
from pywps.exceptions import InvalidParameterValue
from pywps.validator.allowed_value import RANGECLOSURETYPE
from pywps._compat import PY2

LITERAL_DATA_TYPES = ('float', 'boolean', 'integer', 'string',
                      'positiveInteger', 'anyURI', 'time', 'scale', 'angle',
                      'nonNegativeInteger')

# currently we are supporting just ^^^ data types, feel free to add support for
# more
# 'measure', 'angleList',
# 'angle', 'integerList',
# 'positiveIntegerList',
# 'lengthOrAngle', 'gridLength',
# 'measureList', 'lengthList', 
# 'gridLengthList', 'scaleList', 'timeList',
# 'nonNegativeInteger', 'length'


class AnyValue(object):
    """Any value for literal input
    """
    pass

class AllowedValue(AnyValue):
    """Allowed value parameters
    """

    def __init__(self, allowed_type=None, value=None, minval=None,
                 maxval=None, spacing=None,
                 range_closure=RANGECLOSURETYPE.OPEN):

        AnyValue.__init__(self)

        self.allowed_type = allowed_type
        self.value = value
        self.minval = minval
        self.maxval = maxval
        self.spacing = spacing
        self.range_closure = range_closure


def get_converter(convertor):
    def decorator_selector(data_type, data):
        convert = None
        if data_type in LITERAL_DATA_TYPES:
            if data_type == 'string':
                convert = convert_string
            elif data_type == 'integer':
                convert = convert_integer
            elif data_type == 'float':
                convert = convert_float
            elif data_type == 'boolean':
                convert = convert_boolean
            elif data_type == 'positiveInteger':
                convert = convert_positiveInteger
            elif data_type == 'anyURI':
                convert = convert_anyURI
            elif data_type == 'time':
                convert = convert_time
            elif data_type == 'scale':
                convert = convert_scale
            elif data_type == 'angle':
                convert = convert_angle
            elif data_type == 'nonNegativeInteger':
                convert = convert_positiveInteger
            else:
                raise InvalidParameterValue(
                    "Invalid data_type value of LiteralInput " +
                    "set to '{}'".format(data_type))
        try:
            return convert(data)
        except ValueError:
            raise InvalidParameterValue(
                "Could not convert value '{}' to format '{}'".format(
                    data, data_type))


    return decorator_selector


@get_converter
def convert(data_type, data):
    """Convert data to target value
    """

    return data_type, data


def convert_boolean(inpt):
    """Return boolean value from input boolean input

    >>> convert_boolean('1')
    True
    >>> convert_boolean('-1')
    True
    >>> convert_boolean('FaLsE')
    False
    >>> convert_boolean('FaLsEx')
    True
    >>> convert_boolean(0)
    False
    """

    val = False
    if str(inpt).lower() in ['false', 'f']:
        val = False
    else:
        try:
            val = int(inpt)
            if val == 0:
                val = False
            else:
                val = True
        except:
            val = True
    return val

def convert_float(inpt):
    """Return float value from inpt

    >>> convert_float('1')
    1.0
    """

    return float(inpt)

def convert_integer(inpt):
    """Return integer value from input inpt

    >>> convert_integer('1.0')
    1
    """

    return int(float(inpt))

def convert_string(inpt):
    """Return string value from input lit_input

    >>> convert_string(1)
    '1'
    """

    if PY2:
        return str(inpt).decode()
    else:
        return str(inpt)

def convert_positiveInteger(inpt):
    """Return value of input"""

    inpt = convert_integer(inpt)
    if inpt < 0:
        raise InvalidParameterValue(
            'The value "{}" is not of type positiveInteger'.format(inpt))
    else:
        return inpt

def convert_anyURI(inpt):
    """Return value of input
    
    :rtype: url components 
    """
    inpt = convert_string(inpt)
    components = urlparse.urlparse(inpt)

    if components[0] and components[1]:
        return components
    else:
        raise InvalidParameterValue(
            'The value "{}" does not seem to be of type anyURI'.format(inpt))

def convert_time(inpt):
    """Return value of input
    time formating assumed according to ISO standard

    http://www.w3.org/TR/NOTE-datetime

    :rtype: time object
    """
    time_format = '%Y-%m-%dT%H:%M:%S%z'
    inpt = time.strptime(convert_string(inpt), time_format)
    return inpt

def convert_scale(inpt):
    """Return value of input"""

    return convert_float(inpt)

def convert_angle(inpt):
    """Return value of input

    return degrees
    """

    inpt = convert_float(inpt)
    return inpt%360
