##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Unit tests for processing
"""

import unittest

from pywps import configuration
import pywps.processing
from pywps.processing.basic import MultiProcessing
from pywps import Process
from pywps.app import WPSRequest
from pywps.app import WPSResponse
from pywps import LiteralOutput


class ProcessingTest(unittest.TestCase):
    """Processing test cases"""

    def setUp(self):
        def handler(request, response):
            response.outputs['output'].data = '42'
            return response

        self.uuid = 1234
        self.dummy_process = Process(
            handler=handler,
            identifier='dummy',
            title='Dummy Process',
            outputs=[LiteralOutput('output', 'Output', data_type='string')])
        self.wps_request = WPSRequest()
        self.wps_response = WPSResponse(self.dummy_process, self.wps_request, self.uuid)

    def test_default_mode(self):
        """Test pywps.formats.Format class
        """
        self.assertEqual(configuration.get_config_value('processing', 'mode'),
                         'default')
        process = pywps.processing.Process(
            process=self.dummy_process,
            wps_request=self.wps_request,
            wps_response=self.wps_response)
        # process.start()
        self.assertTrue(isinstance(process, MultiProcessing))


def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ProcessingTest)
    ]
    return unittest.TestSuite(suite_list)
