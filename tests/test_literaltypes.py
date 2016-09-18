"""Unit tests for IOs
"""

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
