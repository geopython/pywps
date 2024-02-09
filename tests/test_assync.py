##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from basic import TestBase
import pytest
import time
from pywps import Service, configuration
from pywps import get_ElementMakerForVersion
from pywps.tests import client_for, assert_response_accepted, assert_response_success
from processes import Sleep
from owslib.wps import WPSExecution
from urllib.parse import urlparse

VERSION = "1.0.0"

WPS, OWS = get_ElementMakerForVersion(VERSION)


class ExecuteTest(TestBase):

    def setUp(self) -> None:
        super().setUp()
        # Running processes using the MultiProcessing scheduler and a file-based database
        configuration.CONFIG.set('processing', 'mode', 'distributed')

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
        print(url)

        # OWSlib only reads from URLs, not local files. So we need to read the response manually.
        url = urlparse(url)

        # Poll the process until it completes
        total_time = 0
        sleep_time = .01
        while wps.status not in ["ProcessSucceeded", "ProcessFailed"]:
            resp = client.open(base_url='/wps', path='/status', method='GET', query_string=url.query).data
            if resp:
                wps.checkStatus(response=resp, sleepSecs=0.01)
            else:
                time.sleep(sleep_time)
                total_time += sleep_time
            if total_time > 1:
                raise TimeoutError

        assert wps.status == 'ProcessSucceeded'


def load_tests(loader=None, tests=None, pattern=None):
    import unittest
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTest),
    ]
    return unittest.TestSuite(suite_list)
