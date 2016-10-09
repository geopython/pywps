##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


from collections import namedtuple

_ALLOWEDVALUETYPE = namedtuple('ALLOWEDVALUETYPE', 'VALUE, RANGE')
_RANGELCLOSURETYPE = namedtuple('RANGECLOSURETYPE', 'OPEN, CLOSED,'
                                'OPENCLOSED, CLOSEDOPEN')

ALLOWEDVALUETYPE = _ALLOWEDVALUETYPE('value', 'range')
RANGECLOSURETYPE = _RANGELCLOSURETYPE(
    'open',
    'closed',
    'open-closed',
    'closed-open'
)
