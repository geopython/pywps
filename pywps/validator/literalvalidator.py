##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

""" Validator classes used for LiteralInputs
"""
import logging
from decimal import Decimal

from pywps.inout.literaltypes import AnyValue, NoValue, ValuesReference
from pywps.validator.mode import MODE
from pywps.validator.allowed_value import ALLOWEDVALUETYPE, RANGECLOSURETYPE


LOGGER = logging.getLogger('PYWPS')


def validate_value(data_input, mode):
    """Validate a literal value of type string, integer etc.

    TODO: not fully implemented
    """
    if mode == MODE.NONE:
        passed = True
    else:
        LOGGER.debug('validating literal value.')
        data_input.data
        # TODO: we currently rely only on the data conversion in `pywps.inout.literaltypes.convert`
        passed = True

    LOGGER.debug('validation result: {}'.format(passed))
    return passed


def validate_anyvalue(data_input, mode):
    """Just placeholder, anyvalue is always valid
    """

    return True


def validate_values_reference(data_input, mode):
    """Validate values reference

    TODO: not fully implemented
    """
    if mode == MODE.NONE:
        passed = True
    else:
        LOGGER.debug('validating values reference.')
        data_input.data
        # TODO: we don't validate if the data is within the reference values
        passed = True

    LOGGER.debug('validation result: {}'.format(passed))
    return passed


def validate_allowed_values(data_input, mode):
    """Validate allowed values
    """

    passed = False
    if mode == MODE.NONE:
        passed = True
    else:
        data = data_input.data

        LOGGER.debug('validating allowed values: {} in {}'.format(data, data_input.allowed_values))
        for value in data_input.allowed_values:

            if isinstance(value, (AnyValue, NoValue, ValuesReference)):
                # AnyValue, NoValue and ValuesReference always pass validation
                # NoValue and ValuesReference are not implemented
                passed = True

            elif value.allowed_type == ALLOWEDVALUETYPE.VALUE:
                passed = _validate_value(value, data)

            elif value.allowed_type == ALLOWEDVALUETYPE.RANGE:
                passed = _validate_range(value, data)

            if passed is True:
                break

    LOGGER.debug('validation result: {}'.format(passed))
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

    LOGGER.debug('validating range: {} in {}'.format(data, interval))
    if interval.minval <= data <= interval.maxval:

        if interval.spacing:
            spacing = abs(interval.spacing)
            diff = data - interval.minval
            passed = Decimal(str(diff)) % Decimal(str(spacing)) == 0
        else:
            passed = True

        if passed:
            if interval.range_closure == RANGECLOSURETYPE.OPEN:
                passed = (interval.minval < data < interval.maxval)
            elif interval.range_closure == RANGECLOSURETYPE.CLOSED:
                passed = (interval.minval <= data <= interval.maxval)
            elif interval.range_closure == RANGECLOSURETYPE.OPENCLOSED:
                passed = (interval.minval < data <= interval.maxval)
            elif interval.range_closure == RANGECLOSURETYPE.CLOSEDOPEN:
                passed = (interval.minval <= data < interval.maxval)
    else:
        passed = False

    LOGGER.debug('validation result: {}'.format(passed))
    return passed
