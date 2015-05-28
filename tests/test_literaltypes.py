"""Unit tests for IOs
"""
import unittest
from pywps.inout.literaltypes import *

class ConvertorTest(unittest.TestCase):
    """IOHandler test cases"""

    def test_integer(self):
        """Test integer convertor"""
        self.assertEquals(convert_integer('1.0'), 1)
        self.assertEquals(convert_integer(1), 1)
        with self.assertRaises(ValueError):
            convert_integer('a')

    def test_float(self):
        """Test float convertor"""
        self.assertEquals(convert_float('1.0'), 1.0)
        self.assertEquals(convert_float(1), 1.0)
        with self.assertRaises(ValueError):
            convert_float('a')

    def test_string(self):
        """Test string convertor"""
        self.assertEquals(convert_string('1.0'), '1.0')
        self.assertEquals(convert_string(1), '1')
        self.assertEquals(convert_string('a'), 'a')

    def test_boolean(self):
        """Test boolean convertor"""
        self.assertEquals(convert_boolean('1.0'), True)
        self.assertEquals(convert_boolean(1), True)
        self.assertEquals(convert_boolean('a'), True)
        self.assertEquals(convert_boolean('f'), False)
        self.assertEquals(convert_boolean('falSe'), False)
        self.assertEquals(convert_boolean(False), False)
        self.assertEquals(convert_boolean(0), False)
        self.assertEquals(convert_boolean(-1), True)


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ConvertorTest)
    ]
    return unittest.TestSuite(suite_list)
