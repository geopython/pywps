import unittest
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import lxml.etree
from pywps.app import Service, NAMESPACES


class WpsTestResponse(BaseResponse):

    def __init__(self, *args):
        super(WpsTestResponse, self).__init__(*args)
        self.xml = lxml.etree.fromstring(self.get_data())

    def xpath(self, path):
        return self.xml.xpath(path, namespaces=NAMESPACES)

    def xpath_text(self, path):
        return ' '.join(e.text for e in self.xpath(path))


class CapabilitiesTest(unittest.TestCase):

    def test_returns_valid_response(self):
        service = Service()
        client = Client(service, WpsTestResponse)
        resp = client.get('?Request=GetCapabilities')
        assert resp.status_code == 200
        title = resp.xpath_text('/wps:Capabilities'
                                '/ows:ServiceIdentification'
                                '/ows:Title')
        assert title == 'PyWPS Server'

    def test_returns_process_names(self):
        def pr1(): pass
        def pr2(): pass
        service = Service(processes=[pr1, pr2])
        client = Client(service, WpsTestResponse)
        resp = client.get('?Request=GetCapabilities')
        assert resp.status_code == 200
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
