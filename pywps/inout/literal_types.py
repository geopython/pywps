from collections import namedtuple

_ALLOWEDVALUETYPE = namedtuple('ALLOWEDVALUETYPE', 'VALUE, RANGE')
_RANGELCLOSURETYPE = namedtuple('RANGECLOSURETYPE', 'OPEN, CLOSED,'
                                'OPENCLOSED, CLOSEDOPEN')

ALLOWEDVALUETYPE = _ALLOWEDVALUETYPE(0, 1)
RANGECLOSURETYPE = _RANGELCLOSURETYPE(0, 1, 2, 3)

class AnyValue(object):
    """Any value for literal input
    """
    def __init__(self, data_type=None):
        self.data_type = data_type

class AllowedValue(AnyValue):
    """Allowed value parameters
    """

    def __init__(self, data_type=None, allowed_type=None, value=None, minval=None,
                 maxval=None, spacing=None,
                 range_closure=RANGECLOSURETYPE.OPEN):

        AnyValue.__init__(self, data_type=data_type)

        self.allowed_type = allowed_type
        self.value = value
        self.minval = minval
        self.maxval = maxval
        self.spacing = spacing
        self.range_closure = range_closure
