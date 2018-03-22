import unittest

from pywps.app.Service import _validate_file_input
from pywps.exceptions import FileURLNotSupported


class ServiceTest(unittest.TestCase):

    def test_validate_file_input(self):
        try:
            _validate_file_input(href="file:///private/space/test.txt")
        except FileURLNotSupported:
            self.assertTrue(True)
        else:
            self.assertTrue(False, 'should raise exception FileURLNotSupported')


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ServiceTest),
    ]
    return unittest.TestSuite(suite_list)
