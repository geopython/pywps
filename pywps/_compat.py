""" Compatibility support for Python 2 and 3 """

import sys

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode
    from StringIO import StringIO

else:
    text_type = str
    from io import StringIO
