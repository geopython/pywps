"""Unit tests for IOs
"""
##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
import datetime
from pywps.inout.literaltypes import (
    convert_integer,
    convert_float,
    convert_string,
    convert_boolean,
    convert_time,
    convert_date,
    convert_datetime,
    convert_anyURI,
    ValuesReference,
    InvalidParameterValue,
)


class ValuesReferenceTest(unittest.TestCase):
    """ValuesReference test cases"""

    def setUp(self):
        self.reference = "https://en.wikipedia.org/w/api.php?action=opensearch&search=scotland&format=json"

    def test_json(self):
        val_ref = ValuesReference(
            reference=self.reference)
        new_val_ref = ValuesReference.from_json(val_ref.json)
        self.assertEqual(new_val_ref.reference, self.reference)


class ConvertorTest(unittest.TestCase):
    """IOHandler test cases"""

    def test_integer(self):
        """Test integer convertor"""
        self.assertEqual(convert_integer('1.0'), 1)
        self.assertEqual(convert_integer(1), 1)
        self.assertEqual(convert_integer(str(1)), 1)
        with self.assertRaises(ValueError):
            convert_integer('a')

    def test_float(self):
        """Test float convertor"""
        self.assertEqual(convert_float('1.0'), 1.0)
        self.assertEqual(convert_float(1), 1.0)
        self.assertEqual(convert_float(str(1.0)), 1.0)
        with self.assertRaises(ValueError):
            convert_float('a')

    def test_string(self):
        """Test string convertor"""
        self.assertEqual(convert_string('1.0'), '1.0')
        self.assertEqual(convert_string(1), '1')
        self.assertEqual(convert_string('a'), 'a')
        self.assertEqual(convert_string(str('1.0')), '1.0')

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
        self.assertFalse(convert_boolean(str(False)))
        self.assertTrue(convert_boolean(str(True)))

    def test_time(self):
        """Test time convertor"""
        self.assertEqual(convert_time("12:00:00"),
                         datetime.time(12, 0, 0))
        self.assertEqual(convert_time(str(datetime.time(12, 0, 0))),
                         datetime.time(12, 0, 0))
        self.assertTrue(isinstance(
            convert_time(datetime.time(14)),
            datetime.time))

    def test_date(self):
        """Test date convertor"""
        self.assertEqual(convert_date("2011-07-21"),
                         datetime.date(2011, 7, 21))
        self.assertEqual(convert_date(str(datetime.date(2011, 7, 21))),
                         datetime.date(2011, 7, 21))
        self.assertTrue(isinstance(
            convert_date(datetime.date(2012, 12, 31)),
            datetime.date))

    def test_datetime(self):
        """Test datetime convertor"""
        self.assertEqual(convert_datetime("2016-09-22T12:00:00"),
                         datetime.datetime(2016, 9, 22, 12))
        self.assertEqual(convert_datetime(str(datetime.datetime(2016, 9, 22, 12))),
                         datetime.datetime(2016, 9, 22, 12))
        self.assertTrue(isinstance(
            convert_datetime("2016-09-22T12:00:00Z"),
            datetime.datetime))
        self.assertTrue(isinstance(
            convert_datetime("2016-09-22T12:00:00+01:00"),
            datetime.datetime))
        self.assertTrue(isinstance(
            convert_datetime(datetime.datetime(2016, 9, 22, 6)),
            datetime.datetime))

    def test_anyuri(self):
        """Test URI convertor"""
        self.assertEqual(convert_anyURI("http://username:password@hostname.dom:port/deep/path/;params?query#fragment"),
                         ('http', 'username:password@hostname.dom:port', '/deep/path/', 'params', 'query', 'fragment')
                        )
        self.assertEqual(convert_anyURI("file:///very/very/very/deep/path"),
                         ('file', '', '/very/very/very/deep/path', '', '', '')
                        )
        with self.assertRaises(InvalidParameterValue):
            convert_anyURI("ftp:///deep/path/;params?query#fragment")

def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ConvertorTest),
        loader.loadTestsFromTestCase(ValuesReferenceTest),
    ]
    return unittest.TestSuite(suite_list)
