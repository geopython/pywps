import unittest

import parse
import extent

def load_tests():
    return unittest.TestSuite([parse.load_tests(), extent.load_tests()])

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(load_tests())
