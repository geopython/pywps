###############################################################################
#
# Author:    Alex Morega (?)
#            
# License:
#
# Web Processing Service implementation
# Copyright (C) 2015 PyWPS Development Team, represented by Jachym Cepicky
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
#
###############################################################################

import logging
import sys

LOGGER = logging.getLogger('PYWPS')
PY2 = sys.version_info[0] == 2

if PY2:
    LOGGER.debug('Python 2.x')
    text_type = unicode
    from StringIO import StringIO
    from flufl.enum import Enum
    from urlparse import urlparse
    from urlparse import urljoin
    from urllib2 import urlopen

else:
    LOGGER.debug('Python 3.x')
    text_type = str
    from io import StringIO
    from enum import Enum
    from urllib.parse import urlparse
    from urllib.parse import urljoin
    from urllib.request import urlopen
