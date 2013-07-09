""" Compatibility support for Python 2 and 3 """

import sys

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode

else:
    text_type = str
