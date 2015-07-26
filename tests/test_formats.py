"""Unit tests for Formats
"""
import unittest

from pywps.inout.formats import Format, get_format, FORMATS
from lxml import etree
from pywps.app.basic import xpath_ns


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

        self.assertEquals(frmt.mime_type, 'mimetype')
        self.assertEquals(frmt.schema, 'halloworld')
        self.assertEquals(frmt.encoding, 'asdf')
        self.assertTrue(frmt.validate('the input', 1))

        describeel = frmt.describe_xml()
        self.assertEquals('Format', describeel.tag)
        mimetype = xpath_ns(describeel, '/Format/MimeType')
        encoding = xpath_ns(describeel, '/Format/Encoding')
        schema = xpath_ns(describeel, '/Format/Schema')

        self.assertTrue(mimetype)
        self.assertTrue(encoding)
        self.assertTrue(schema)

        self.assertEquals(mimetype[0].text, 'mimetype')
        self.assertEquals(encoding[0].text, 'asdf')
        self.assertEquals(schema[0].text, 'halloworld')

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



def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(FormatsTest)
    ]
    return unittest.TestSuite(suite_list)
