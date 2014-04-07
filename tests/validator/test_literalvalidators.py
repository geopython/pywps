"""Unit tests for literal validator
"""
import unittest
from pywps.validator.literalvalidator import *

def get_input(name, schema, mimetype):

    class FakeInput(object):
        file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'data', name)

    class data_format(object):
        file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'data', schema)

    fake_input = FakeInput()
    fake_input.stream = open(fake_input.file)
    fake_input.data_format = data_format()
    fake_input.data_format.schema = 'file://' + fake_input.data_format.file
    fake_input.data_format.mimetype = mimetype

    return fake_input


class ValidateTest(unittest.TestCase):
    """Literal validator test cases"""

    def setUp(self):
        pass


    def tearDown(self):
        pass

    def test_basic_validator(self):
        """Test basic validator"""
        gml_input = get_input('point.gml', 'point.xsd', FORMATS['GML'][0])
        validator = BasicValidator()
        self.assertTrue(validator.validate(gml_input, MODE.NONE),
                        'Basic validator validated')

    def test_gml_validator(self):
        """Test GML validator
        """
        gml_input = get_input('point.gml', 'point.xsd', FORMATS['GML'][0])
        self.assertTrue(validategml(gml_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validategml(gml_input, MODE.SIMPLE), 'SIMPLE validation')
        self.assertTrue(validategml(gml_input, MODE.STRICT), 'STRICT validation')
        self.assertTrue(validategml(gml_input, MODE.VERYSTRICT), 'VERYSTRICT validation')

    def test_geojson_validator(self):
        """Test GeoJSON validator
        """
        geojson_input = get_input('json/point.geojson', 'json/schema/geojson.json',
                                  FORMATS['GEOJSON'][0])
        self.assertTrue(validategeojson(geojson_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validategeojson(geojson_input, MODE.SIMPLE), 'SIMPLE validation')
        self.assertTrue(validategeojson(geojson_input, MODE.STRICT), 'STRICT validation')
        self.assertTrue(validategeojson(geojson_input, MODE.VERYSTRICT), 'VERYSTRICT validation')

    def test_fail_validator(self):

        fake_input = get_input('point.xsd', 'point.xsd', FORMATS['GML'][0])

        self.assertFalse(validategml(fake_input, MODE.SIMPLE), 'SIMPLE validation invalid')

def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ValidateTest)
    ]
    return unittest.TestSuite(suite_list)
