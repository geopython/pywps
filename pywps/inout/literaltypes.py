"""Literaltypes are used for LiteralInputs, to make sure, input data are OK
"""

from pywps._compat import urlparse
import time
from pywps.exceptions import InvalidParameterValue
from pywps.validator.allowed_value import RANGECLOSURETYPE
from pywps.validator.allowed_value import ALLOWEDVALUETYPE
from pywps._compat import PY2
from pywps import OWS, WPS, OGCTYPE, NAMESPACES

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

class NoValue(object):
    """No value allowed
    NOTE: not really implemented
    """
    pass

class ValuesReference(object):
    """Any value for literal input
    NOTE: not really implemented
    """
    pass

class AllowedValue(AnyValue):
    """Allowed value parameters
    the values are evaluated in literal validator functions

    :param pywps.validator.allowed_value.ALLOWEDVALUETYPE allowed_type: VALUE or RANGE
    :param value:
    """

    def __init__(self, allowed_type=ALLOWEDVALUETYPE.VALUE, value=None,
                 minval=None, maxval=None, spacing=None,
                 range_closure=RANGECLOSURETYPE.CLOSED):

        AnyValue.__init__(self)

        self.allowed_type = allowed_type
        self.value = value
        self.minval = minval
        self.maxval = maxval
        self.spacing = spacing
        self.range_closure = range_closure

    def describe_xml(self):
        """Return back Element for DescribeProcess response
        """
        doc = None
        if self.allowed_type == ALLOWEDVALUETYPE.VALUE:
            doc = OWS.Value(str(self.value))
        else:
            doc = OWS.Range()
            doc.set('{%s}rangeClosure' % NAMESPACES['ows'],  self.range_closure)
            doc.append(OWS.MinimumValue(str(self.minval)))
            doc.append(OWS.MaximumValue(str(self.maxval)))
            if self.spacing:
                doc.append(OWS.Spacing(str(self.spacing)))
        return doc


def get_converter(convertor):
    """function for decoration of convert
    """

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


def make_allowedvalues(allowed_values):
    """convert given value list to AllowedValue objects

    :return: list of pywps.inout.literaltypes.AllowedValue
    """

    new_allowedvalues = []

    for value in allowed_values:

        if isinstance(value, AllowedValue):
            new_allowedvalues.append(value)

        elif type(value) == tuple or\
           type(value) == list:
            minval = maxval = spacing = None
            if len(value) == 2:
                minval = value[0]
                maxval = value[1]
            else:
                minval = value[0]
                spacing = value[1]
                maxval = value[2]
            new_allowedvalues.append(
                AllowedValue(allowed_type=ALLOWEDVALUETYPE.RANGE,
                             minval=minval, maxval=maxval,
                             spacing=spacing)
            )

        else:
            new_allowedvalues.append(AllowedValue(value=value))

    return new_allowedvalues


def is_anyvalue(value):
    """Check for any value object of given value
    """

    is_av = False

    if value == AnyValue:
        is_av = True
    elif value == None:
        is_av = True
    elif isinstance(value, AnyValue):
        is_av = True
    elif str(value).lower() == 'anyvalue':
        is_av = True

    return is_av
