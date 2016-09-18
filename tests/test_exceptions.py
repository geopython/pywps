###############################################################################
#
# Copyright (C) 2014-2016 PyWPS Development Team, represented by
# PyWPS Project Steering Committee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
###############################################################################

import unittest
from pywps import Process, Service, WPS, OWS
from pywps.app.basic import xpath_ns
from tests.common import assert_pywps_version, client_for
import lxml.etree


class ExceptionsTest(unittest.TestCase):

    def setUp(self):
        self.client = client_for(Service(processes=[]))

    def test_invalid_parameter_value(self):
        resp = self.client.get('?service=wms')
        exception_el = resp.xpath('/ows:ExceptionReport/ows:Exception')[0]
        assert exception_el.attrib['exceptionCode'] == 'InvalidParameterValue'
        assert resp.status_code == 400
        assert resp.headers['Content-Type'] == 'text/xml'
        assert_pywps_version(resp)

    def test_missing_parameter_value(self):
        resp = self.client.get()
        exception_el = resp.xpath('/ows:ExceptionReport/ows:Exception')[0]
        assert exception_el.attrib['exceptionCode'] == 'MissingParameterValue'
        assert resp.status_code == 400
        assert resp.headers['Content-Type'] == 'text/xml'

    def test_missing_request(self):
        resp = self.client.get("?service=wps")
        exception_el = resp.xpath('/ows:ExceptionReport/ows:Exception/ows:ExceptionText')[0]
        # should mention something about a request
        assert 'request' in exception_el.text
        assert resp.headers['Content-Type'] == 'text/xml'

    def test_bad_request(self):
        resp = self.client.get("?service=wps&request=xyz")
        exception_el = resp.xpath('/ows:ExceptionReport/ows:Exception')[0]
        assert exception_el.attrib['exceptionCode'] == 'OperationNotSupported'
        assert resp.headers['Content-Type'] == 'text/xml'

def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExceptionsTest),
    ]
    return unittest.TestSuite(suite_list)
