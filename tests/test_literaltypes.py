"""Unit tests for IOs
"""
import unittest
from pywps.literaltypes import *

class ConvertorTest(unittest.TestCase):
    """IOHandler test cases"""

    def test_integer(self):
        """Test integer convertor"""
        self.assertEquals(convert_integer('1.0'), 1)
        self.assertEquals(convert_integer(1), 1)
        with self.assertRaises(ValueError):
            convert_integer('a')


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ConvertorTest)
    ]
    return unittest.TestSuite(suite_list)
