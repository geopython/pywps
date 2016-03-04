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

import logging

from pywps.validator.mode import MODE
from pywps.validator.allowed_value import ALLOWEDVALUETYPE, RANGECLOSURETYPE


LOGGER = logging.getLogger(__name__)

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

        LOGGER.debug('validating allowed values: %s in %s', data, data_input.allowed_values)
        for value in data_input.allowed_values:

            if value.allowed_type == ALLOWEDVALUETYPE.VALUE:
                passed = _validate_value(value, data)

            elif value.allowed_type == ALLOWEDVALUETYPE.RANGE:
                passed = _validate_range(value, data)

            if passed is True:
                break

    LOGGER.debug('validation result: %r', passed)
    return passed


def _validate_value(value, data):
    """Validate data against given value directly

    :param value: list or tupple with allowed data
    :param data: the data itself (string or number)
    """

    passed = False
    if data == value.value:
        passed = True

    return passed


def _validate_range(interval, data):
    """Validate data against given range
    """

    passed = False

    LOGGER.debug('validating range: %s in %r', data, interval)
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

    LOGGER.debug('validation result: %r', passed)
    return passed
