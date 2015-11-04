"""Unit tests for IOs
"""
import unittest
from pywps.inout.literaltypes import *

class ConvertorTest(unittest.TestCase):
    """IOHandler test cases"""

    def test_integer(self):
        """Test integer convertor"""
        self.assertEqual(convert_integer('1.0'), 1)
        self.assertEqual(convert_integer(1), 1)
        with self.assertRaises(ValueError):
            convert_integer('a')

    def test_float(self):
        """Test float convertor"""
        self.assertEqual(convert_float('1.0'), 1.0)
        self.assertEqual(convert_float(1), 1.0)
        with self.assertRaises(ValueError):
            convert_float('a')

    def test_string(self):
        """Test string convertor"""
        self.assertEqual(convert_string('1.0'), '1.0')
        self.assertEqual(convert_string(1), '1')
        self.assertEqual(convert_string('a'), 'a')

    def test_boolean(self):
        """Test boolean convertor"""
        self.assertTrue(convert_boolean('1.0'))
        self.assertTrue(convert_boolean(1))
        self.assertTrue(convert_boolean('a'))
        self.assertFalse(convert_boolean('f'))
        self.assertFalse(convert_boolean('falSe'))
        self.assertFalse(convert_boolean(False))
        self.assertFalse(convert_boolean(0))
        self.assertTrue(convert_boolean(-1))


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ConvertorTest)
    ]
    return unittest.TestSuite(suite_list)
