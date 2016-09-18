###############################################################################
#
# Copyright (C) 2014-2016 PyWPS Development Team, represented by
# PyWPS Project Steering Committee
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

import sys
import unittest

from tests import test_capabilities
from tests import test_describe
from tests import test_execute
from tests import test_exceptions
from tests import test_inout
from tests import test_literaltypes
from tests import validator
from tests import test_ows
from tests import test_formats
from tests import test_dblog
from tests import test_wpsrequest
from tests.validator import test_complexvalidators
from tests.validator import test_literalvalidators

def load_tests(loader=None, tests=None, pattern=None):
    """Load tests
    """
    return unittest.TestSuite([
        test_capabilities.load_tests(),
        test_execute.load_tests(),
        test_describe.load_tests(),
        test_inout.load_tests(),
        test_exceptions.load_tests(),
        test_ows.load_tests(),
        test_literaltypes.load_tests(),
        test_complexvalidators.load_tests(),
        test_literalvalidators.load_tests(),
        test_formats.load_tests(),
        test_dblog.load_tests(),
        test_wpsrequest.load_tests()
    ])

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(load_tests())
    if not result.wasSuccessful():
        sys.exit(1)
