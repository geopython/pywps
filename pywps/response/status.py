from collections import namedtuple

_STATUS = namedtuple('Status', 'ERROR_STATUS, NO_STATUS, STORE_STATUS,'
                     'STORE_AND_UPDATE_STATUS, DONE_STATUS')

STATUS = _STATUS(0, 10, 20, 30, 40)
