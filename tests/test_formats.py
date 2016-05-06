"""Unit tests for Formats
"""
import unittest

from pywps.inout.formats import Format, get_format, FORMATS
from lxml import etree
from pywps.app.basic import xpath_ns
from pywps.validator.base import emptyvalidator


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

        describeel = frmt.describe_xml()
        self.assertEqual('Format', describeel.tag)
        mimetype = xpath_ns(describeel, '/Format/MimeType')
        encoding = xpath_ns(describeel, '/Format/Encoding')
        schema = xpath_ns(describeel, '/Format/Schema')

        self.assertTrue(mimetype)
        self.assertTrue(encoding)
        self.assertTrue(schema)

        self.assertEqual(mimetype[0].text, 'mimetype')
        self.assertEqual(encoding[0].text, 'asdf')
        self.assertEqual(schema[0].text, 'halloworld')

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

