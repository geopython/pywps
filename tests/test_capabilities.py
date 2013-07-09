import unittest
import lxml.etree
from pywps.app import Process, Service, WPS
from tests.common import client_for


class BadRequestTest(unittest.TestCase):

    def test_bad_http_verb(self):
        client = client_for(Service())
        resp = client.put('')
        assert resp.status_code == 405  # method not allowed

    def test_bad_request_type_with_get(self):
        client = client_for(Service())
        resp = client.get('?Request=foo')
        assert resp.status_code == 400

    def test_bad_request_type_with_post(self):
        client = client_for(Service())
        request_doc = WPS.Foo()
        resp = client.post_xml('', doc=request_doc)
        assert resp.status_code == 400


class CapabilitiesTest(unittest.TestCase):

    def test_get_request(self):
        def pr1(): pass
        def pr2(): pass
        client = client_for(Service(processes=[Process(pr1), Process(pr2)]))
        resp = client.get('?Request=GetCapabilities')
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'text/xml'
        title = resp.xpath_text('/wps:Capabilities'
                                '/ows:ServiceIdentification'
                                '/ows:Title')
        assert title == 'PyWPS Server'
        names = resp.xpath_text('/wps:Capabilities'
                                '/wps:ProcessOfferings'
                                '/wps:Process'
                                '/ows:Identifier')
        assert names == 'pr1 pr2'


def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(BadRequestTest),
        loader.loadTestsFromTestCase(CapabilitiesTest),
    ]
    return unittest.TestSuite(suite_list)
