##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
import time
from pywps import Service, configuration
from pywps import get_ElementMakerForVersion
from pywps.tests import client_for, assert_response_accepted
from .processes import Sleep
from owslib.wps import WPSExecution
from pathlib import Path

VERSION = "1.0.0"

WPS, OWS = get_ElementMakerForVersion(VERSION)


class ExecuteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mode = configuration.CONFIG.get('processing', 'mode')
        configuration.CONFIG.set('processing', 'mode', 'distributed')

    def tearDown(self) -> None:
        configuration.CONFIG.set('processing', 'mode', self.mode)

    def test_assync(self):
        client = client_for(Service(processes=[Sleep()]))
        wps = WPSExecution()

        # Build an asynchronous request (requires specifying outputs and setting the mode).
        doc = wps.buildRequest('sleep',
                               inputs=[('seconds', '.01')],
                               output=[('finished', None, None)],
                               mode='async')

        resp = client.post_xml(doc=doc)
        wps.parseResponse(resp.xml)
        assert_response_accepted(resp)

        # Wait for process to complete. The test will fail otherwise, which confirms the process is asynchronous.
        time.sleep(.5)

        # Parse response to extract the status file path
        url = resp.xml.xpath("//@statusLocation")[0]

        # OWSlib only reads from URLs, not local files. So we need to read the response manually.
        p = Path(url[6:])
        wps.checkStatus(response=p.read_bytes(), sleepSecs=0)
        assert wps.status == 'ProcessSucceeded'


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTest),
    ]
    return unittest.TestSuite(suite_list)
