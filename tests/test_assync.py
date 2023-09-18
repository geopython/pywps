##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
import pytest
import time
from pywps import Service, configuration
from pywps import get_ElementMakerForVersion
from pywps.tests import client_for, assert_response_accepted, assert_response_success
from processes import Sleep
from owslib.wps import WPSExecution
from pathlib import Path

VERSION = "1.0.0"

WPS, OWS = get_ElementMakerForVersion(VERSION)


class ExecuteTest(unittest.TestCase):
    def setUp(self) -> None:
        # Running processes using the MultiProcessing scheduler and a file-based database
        configuration.CONFIG.set('processing', 'mode', 'distributed')
        configuration.CONFIG.set("logging", "database", "sqlite:////tmp/test-pywps-logs.sqlite3")

    def tearDown(self) -> None:
        configuration.load_configuration()

    def test_async(self):
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

        # The process should not have finished by now. If it does, it's running in sync mode.
        with pytest.raises(AssertionError):
            assert_response_success(resp)

        # Parse response to extract the status file path
        url = resp.xml.xpath("//@statusLocation")[0]

        # OWSlib only reads from URLs, not local files. So we need to read the response manually.
        p = Path(url[6:])

        # Poll the process until it completes
        total_time = 0
        sleep_time = .01
        while wps.status not in ["ProcessSucceeded", "ProcessFailed"]:
            resp = p.read_bytes()
            if resp:
                wps.checkStatus(response=resp, sleepSecs=0.01)
            else:
                time.sleep(sleep_time)
                total_time += sleep_time
            if total_time > 1:
                raise TimeoutError

        assert wps.status == 'ProcessSucceeded'


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTest),
    ]
    return unittest.TestSuite(suite_list)
