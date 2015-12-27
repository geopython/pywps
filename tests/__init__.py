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
        test_dblog.load_tests()
    ])

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(load_tests())
    if not result.wasSuccessful():
        sys.exit(1)
