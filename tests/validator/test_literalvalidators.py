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
        pass

def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ValidateTest)
    ]
    return unittest.TestSuite(suite_list)
