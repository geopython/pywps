import unittest
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import lxml.etree
from pywps.app import create_process, NAMESPACES


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
        app = create_process()
        client = Client(app, WpsTestResponse)
        resp = client.get('?Request=GetCapabilities')
        assert resp.status_code == 200
        title = resp.xpath_text('/wps:Capabilities'
                                '/ows:ServiceIdentification'
                                '/ows:Title')
        assert title == 'PyWPS Server'


def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(CapabilitiesTest),
    ]
    return unittest.TestSuite(suite_list)
