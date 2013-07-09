import unittest
from pywps.app import Process, Service
from tests.common import client_for


class CapabilitiesTest(unittest.TestCase):

    def test_returns_valid_response(self):
        client = client_for(Service())
        resp = client.get('?Request=GetCapabilities')
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'text/xml'
        title = resp.xpath_text('/wps:Capabilities'
                                '/ows:ServiceIdentification'
                                '/ows:Title')
        assert title == 'PyWPS Server'

    def test_returns_process_names(self):
        def pr1(): pass
        def pr2(): pass
        client = client_for(Service(processes=[Process(pr1), Process(pr2)]))
        resp = client.get('?Request=GetCapabilities')
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'text/xml'
        names = resp.xpath_text('/wps:Capabilities'
                                '/wps:ProcessOfferings'
                                '/wps:Process'
                                '/ows:Identifier')
        assert names == 'pr1 pr2'


def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(CapabilitiesTest),
    ]
    return unittest.TestSuite(suite_list)
