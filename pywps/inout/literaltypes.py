##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Literaltypes are used for LiteralInputs, to make sure, input data are OK
"""

from pywps._compat import urlparse
import time
from dateutil.parser import parse as date_parser
import datetime
from pywps.exceptions import InvalidParameterValue
from pywps.validator.allowed_value import RANGECLOSURETYPE
from pywps.validator.allowed_value import ALLOWEDVALUETYPE
from pywps._compat import PY2
from pywps import get_ElementMakerForVersion

import logging
LOGGER = logging.getLogger('PYWPS')

LITERAL_DATA_TYPES = ('float', 'boolean', 'integer', 'string',
                      'positiveInteger', 'anyURI', 'time', 'date', 'dateTime',
                      'scale', 'angle',
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

    @property
    def json(self):
        return {'type': 'anyvalue'}


class NoValue(object):
    """No value allowed
    NOTE: not really implemented
    """

    @property
    def json(self):
        return {'type': 'novalue'}


class ValuesReference(object):
    """Any value for literal input
    NOTE: not really implemented
    """

    @property
    def json(self):
        return {'type': 'valuesreference'}


class AllowedValue(AnyValue):
    """Allowed value parameters
    the values are evaluated in literal validator functions

    :param pywps.validator.allowed_value.ALLOWEDVALUETYPE allowed_type: VALUE or RANGE
    :param value: single value
    :param minval: minimal value in case of Range
    :param maxval: maximal value in case of Range
    :param spacing: spacing in case of Range
    :param pywps.input.literaltypes.RANGECLOSURETYPE range_closure:
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

    @property
    def json(self):
        value = self.value
        if hasattr(value, 'json'):
            value = value.json
        return {
            'type': 'allowedvalue',
            'allowed_type': self.allowed_type,
            'value': value,
            'minval': self.minval,
            'maxval': self.maxval,
            'spacing': self.spacing,
            'range_closure': self.range_closure
        }


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
            elif data_type == 'date':
                convert = convert_date
            elif data_type == 'dateTime':
                convert = convert_datetime
            elif data_type == 'scale':
                convert = convert_scale
            elif data_type == 'angle':
                convert = convert_angle
            elif data_type == 'nonNegativeInteger':
                convert = convert_positiveInteger
            else:
                raise InvalidParameterValue(
                    "Invalid data_type value of LiteralInput "
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
        except Exception:
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
    time formating assumed according to ISO standard:

    https://www.w3.org/TR/xmlschema-2/#time

    Examples: 12:00:00

    :rtype: datetime.time object
    """
    if not isinstance(inpt, datetime.time):
        inpt = convert_datetime(inpt).time()
    return inpt


def convert_date(inpt):
    """Return value of input
    date formating assumed according to ISO standard:

    https://www.w3.org/TR/xmlschema-2/#date

    Examples: 2016-09-20

    :rtype: datetime.date object
    """
    if not isinstance(inpt, datetime.date):
        inpt = convert_datetime(inpt).date()
    return inpt


def convert_datetime(inpt):
    """Return value of input
    dateTime formating assumed according to ISO standard:

    * http://www.w3.org/TR/NOTE-datetime
    * https://www.w3.org/TR/xmlschema-2/#dateTime

    Examples: 2016-09-20T12:00:00, 2012-12-31T06:30:00Z,
              2017-01-01T18:00:00+01:00

    :rtype: datetime.datetime object
    """
    # TODO: %z directive works only with python 3
    # time_format = '%Y-%m-%dT%H:%M:%S%z'
    # time_format = '%Y-%m-%dT%H:%M:%S%Z'
    # inpt = time.strptime(convert_string(inpt), time_format)
    if not isinstance(inpt, datetime.datetime):
        inpt = convert_string(inpt)
        inpt = date_parser(inpt)
    return inpt


def convert_scale(inpt):
    """Return value of input"""

    return convert_float(inpt)


def convert_angle(inpt):
    """Return value of input

    return degrees
    """

    inpt = convert_float(inpt)
    return inpt % 360


def make_allowedvalues(allowed_values):
    """convert given value list to AllowedValue objects

    :return: list of pywps.inout.literaltypes.AllowedValue
    """

    new_allowedvalues = []

    for value in allowed_values:

        if isinstance(value, AllowedValue):
            new_allowedvalues.append(value)

        elif type(value) == tuple or type(value) == list:
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
    elif value is None:
        is_av = True
    elif isinstance(value, AnyValue):
        is_av = True
    elif str(value).lower() == 'anyvalue':
        is_av = True

    return is_av
