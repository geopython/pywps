from collections import namedtuple

_WPS_STATUS = namedtuple('WPSStatus', ['UNKNOWN', 'ACCEPTED', 'STARTED', 'PAUSED', 'SUCCEEDED', 'FAILED'])
WPS_STATUS = _WPS_STATUS(0, 1, 2, 3, 4, 5)
