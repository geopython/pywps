""" Validator classes used for LiteralInputs
"""
# Author:    Jachym Cepicky
#            
# License:
#
# Web Processing Service implementation
# Copyright (C) 2014-2015 PyWPS Development Team, represented by Jachym Cepicky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from pywps.validator.mode import MODE
from collections import namedtuple

_ALLOWEDVALUETYPE = namedtuple('ALLOWEDVALUETYPE', 'VALUE, RANGE')
_RANGELCLOSURETYPE = namedtuple('RANGECLOSURETYPE', 'OPEN, CLOSED,'
                                'OPENCLOSED, CLOSEDOPEN')

ALLOWEDVALUETYPE = _ALLOWEDVALUETYPE(0, 1)
RANGECLOSURETYPE = _RANGELCLOSURETYPE(0, 1, 2, 3)

class AllowedValue:
    """Allowed value parameters
    """

    def __init__(self, allowed_type=None, value=None, minval=None,
                 maxval=None, spacing=None,
                 range_closure=RANGECLOSURETYPE.OPEN):

        self.allowed_type = allowed_type
        self.value = value
        self.minval = minval
        self.maxval = maxval
        self.spacing = spacing
        self.range_closure = range_closure

def validate_anyvalue(data_input, mode):
    """Just placeholder, anyvalue is always valid
    """
    return True


def validate_allowed_values(data_input, mode):
    """Validate allowed values
    """

    passed = False
    if mode == MODE.NONE:
        passed = True
    else:
        data = data_input.data

        for value in data_input.allowed_values:

            if value.allowed_type == ALLOWEDVALUETYPE.VALUE:
                passed = _validate_value(value, data)

            elif value.allowed_type == ALLOWEDVALUETYPE.RANGE:
                passed = _validate_range(value, data)

            if passed is True:
                break

    return passed


def _validate_value(value, data):
    """Validate data against given value directly
    """

    return value.value == data


def _validate_range(interval, data):
    """Validate data against given range
    """

    passed = False

    if interval.minval <= data <= interval.maxval:

        if interval.spacing:
            spacing = abs(interval.spacing)
            diff = data - interval.minval
            passed = diff%spacing == 0
        else:
            passed = True

        if passed:
            if interval.range_closure == RANGECLOSURETYPE.OPEN:
                passed = (interval.minval <= data <= interval.maxval)
            elif interval.range_closure == RANGECLOSURETYPE.CLOSED:
                passed = (interval.minval < data < interval.maxval)
            elif interval.range_closure == RANGECLOSURETYPE.OPENCLOSED:
                passed = (interval.minval <= data < interval.maxval)
            elif interval.range_closure == RANGECLOSURETYPE.CLOSEDOPEN:
                passed = (interval.minval < data <= interval.maxval)
    else:
        passed = False

    return passed


if __name__ == "__main__":
    import doctest
    doctest.testmod()
