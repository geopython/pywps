"""Unit tests for Formats
"""
##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest

from pywps.inout.formats import Format, get_format, FORMATS
from lxml import etree
from pywps.app.basic import get_xpath_ns
from pywps.validator.base import emptyvalidator

xpath_ns = get_xpath_ns("1.0.0")


class FormatsTest(unittest.TestCase):
    """Formats test cases"""

    def setUp(self):

        def validate(self, inpt, level=None):
            """fake validate method
            """
            return True

        self.validate = validate

    def tearDown(self):
        pass

    def test_format_class(self):
        """Test pywps.formats.Format class
        """
        frmt = Format('mimetype', schema='halloworld', encoding='asdf',
                      validate=self.validate)

        self.assertEqual(frmt.mime_type, 'mimetype')
        self.assertEqual(frmt.schema, 'halloworld')
        self.assertEqual(frmt.encoding, 'asdf')
        self.assertTrue(frmt.validate('the input', 1))

        describeel = frmt.json

        self.assertEqual(describeel["mime_type"], 'mimetype')
        self.assertEqual(describeel["encoding"], 'asdf')
        self.assertEqual(describeel["schema"], 'halloworld')

        frmt2 = get_format('GML')

        self.assertFalse(frmt.same_as(frmt2))

    def test_getformat(self):
        """test for pypws.inout.formats.get_format function
        """

        frmt = get_format('GML', self.validate)
        self.assertTrue(frmt.mime_type, FORMATS.GML.mime_type)
        self.assertTrue(frmt.validate('ahoj', 1))

        frmt2 = get_format('GML')

        self.assertTrue(frmt.same_as(frmt2))

    def test_format_equal_types(self):
        """Test that equality check returns the expected bool and doesn't raise
        when types mismatch.
        """
        frmt = get_format('GML')
        self.assertTrue(isinstance(frmt, Format))
        try:
            res = frmt.same_as("GML")  # not a Format type
        except AssertionError:
            self.fail("Comparing a format to another type should not raise")
        except Exception:
            self.fail("Unexpected error, test failed for unknown reason")
        self.assertFalse(res, "Equality check with other type should be False")

        frmt_other = get_format('GML')
        self.assertTrue(frmt == frmt_other, "Same formats should return True")

    def test_json_out(self):
        """Test json export
        """

        frmt = get_format('GML')
        outjson = frmt.json
        self.assertEqual(outjson['schema'], '')
        self.assertEqual(outjson['extension'], '.gml')
        self.assertEqual(outjson['mime_type'], 'application/gml+xml')
        self.assertEqual(outjson['encoding'], '')

    def test_json_in(self):
        """Test json import
        """

        injson = {}
        injson['schema'] = 'elcepelce'
        injson['extension'] = '.gml'
        injson['mime_type'] = 'application/gml+xml'
        injson['encoding'] = 'utf-8'

        frmt = Format(injson['mime_type'])
        frmt.json = injson

        self.assertEqual(injson['schema'], frmt.schema)
        self.assertEqual(injson['extension'], frmt.extension)
        self.assertEqual(injson['mime_type'], frmt.mime_type)
        self.assertEqual(injson['encoding'], frmt.encoding)




def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(FormatsTest)
    ]
    return unittest.TestSuite(suite_list)

