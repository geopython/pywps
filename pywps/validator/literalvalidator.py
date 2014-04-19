from pywps.validator import ValidatorAbstract
from pywps.validator import MODE


class AllowedValueType:
    """Allowed values type
    """
    VALUE = 0
    RANGE = 1


class RangeClosureType:
    """Range closure type
    """
    OPEN = 0
    CLOSED = 1
    OPENCLOSED = 2
    CLOSEDOPEN = 3


class AllowedValue:
    """Allowed value parameters
    """

    allowed_type = None
    value = None
    minval = None
    maxval = None
    spacing = None
    range_closure = RangeClosureType.OPEN


class BasicValidator(ValidatorAbstract):
    """AllowedValue validator

    >>> from pywps.validator import MODE
    >>> class FakeInput:
    ...     source_type = 'data'
    ...     data = 1
    >>> fake_input = FakeInput()
    >>> validator = BasicValidator()
    >>> validator.validate(fake_input, MODE.NONE)
    """

    def validate(self, data_input, level=MODE.VERYSTRICT):
        """Validate allowed values input
        """

        # TODO this is where I ended
        if level == MODE.NONE:
            return True
        else:
            return False


def validate_anyvalue(data_input, mode):
    """Just placeholder, anyvalue is always valid
    """
    return True


def validate_allowed_values(data_input, mode):

    passed = False
    if mode == MODE.NONE:
        passed = True
    else:
        data = data_input.data

        for value in data_input.allowed_values:

            if value.allowed_type == AllowedValueType.VALUE:
                passed = _validate_value(value, data)

            elif value.allowed_type == AllowedValueType.RANGE:
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
            if interval.range_closure == RangeClosureType.OPEN:
                passed = (interval.minval <= data <= interval.maxval)
            elif interval.range_closure == RangeClosureType.CLOSED:
                passed = (interval.minval < data < interval.maxval)
            elif interval.range_closure == RangeClosureType.OPENCLOSED:
                passed = (interval.minval <= data < interval.maxval)
            elif interval.range_closure == RangeClosureType.CLOSEDOPEN:
                passed = (interval.minval < data <= interval.maxval)
    else:
        passed = False

    return passed


if __name__ == "__main__":
    import doctest
    doctest.testmod()
