##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Unit tests for dblog
"""

import unittest

from pywps import configuration
from pywps.dblog import log_request
from pywps.dblog import ProcessInstance

from types import SimpleNamespace as ns

fake_request = ns(
    version = '1.0.0',
    operation = 'execute',
    identifier = 'dummy_identifier'
)

class DBLogTest(unittest.TestCase):
    """DBGLog test cases"""

    def setUp(self):

        self.database = configuration.get_config_value('logging', 'database')

    def test_log_request(self):
        log_request("0bf3cd00-0102-11ed-8421-e4b97ac7e02e", fake_request)
        log_request("0bf3cd00-0102-11ed-8421-e4b97ac7e03e", fake_request)
        log_request("0bf3cd00-0102-11ed-8421-e4b97ac7e04e", fake_request)


def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DBLogTest)
    ]
    return unittest.TestSuite(suite_list)
