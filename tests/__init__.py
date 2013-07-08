import sys
import unittest

import parse
import extent
from tests import test_capabilities

def load_tests():
    return unittest.TestSuite([
        parse.load_tests(),
        extent.load_tests(),
        test_capabilities.load_tests(),
    ])

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(load_tests())
    if not result.wasSuccessful():
        sys.exit(1)
