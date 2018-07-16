##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
from pywps import Process, Service, get_ElementMakerForVersion
from pywps.app.basic import get_xpath_ns
from pywps.tests import assert_pywps_version, client_for
import lxml.etree

import re

VERSION="1.0.0"
WPS, OWS = get_ElementMakerForVersion(VERSION)
xpath_ns = get_xpath_ns(VERSION)

class ExceptionsTest(unittest.TestCase):

    def setUp(self):
        self.client = client_for(Service(processes=[]))

    def test_invalid_parameter_value(self):
        resp = self.client.get('?service=wms')
        exception_el = resp.xpath('/ows:ExceptionReport/ows:Exception')[0]
        assert exception_el.attrib['exceptionCode'] == 'InvalidParameterValue'
        assert resp.status_code == 400
        assert re.match('text/xml(;\s*charset=.*)?', resp.headers['Content-Type'])
        assert_pywps_version(resp)

    def test_missing_parameter_value(self):
        resp = self.client.get()
        exception_el = resp.xpath('/ows:ExceptionReport/ows:Exception')[0]
        assert exception_el.attrib['exceptionCode'] == 'MissingParameterValue'
        assert resp.status_code == 400
        assert re.match('text/xml(;\s*charset=.*)?', resp.headers['Content-Type'])

    def test_missing_request(self):
        resp = self.client.get("?service=wps")
        exception_el = resp.xpath('/ows:ExceptionReport/ows:Exception/ows:ExceptionText')[0]
        # should mention something about a request
        assert 'request' in exception_el.text
        assert re.match('text/xml(;\s*charset=.*)?', resp.headers['Content-Type'])

    def test_bad_request(self):
        resp = self.client.get("?service=wps&request=xyz")
        exception_el = resp.xpath('/ows:ExceptionReport/ows:Exception')[0]
        assert exception_el.attrib['exceptionCode'] == 'OperationNotSupported'
        assert re.match('text/xml(;\s*charset=.*)?', resp.headers['Content-Type'])

def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExceptionsTest),
    ]
    return unittest.TestSuite(suite_list)
