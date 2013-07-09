import unittest
from pywps.app import Process, Service, xpath_ns, WPS, OWS
from tests.common import client_for


class DescribeProcessTest(unittest.TestCase):

    def setUp(self):
        def hello(request): pass
        hello_process = Process(hello)
        self.client = client_for(Service(processes=[hello_process]))

    def check_describe_response(self, resp):
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'text/xml'
        [desc] = resp.xpath('/wps:ProcessDescriptions/wps:ProcessDescription')
        assert xpath_ns(desc, './ows:Identifier')[0].text == 'hello'

    def test_get_request(self):
        resp = self.client.get('?Request=DescribeProcess&identifier=hello')
        self.check_describe_response(resp)

    def test_post_request(self):
        request_doc = WPS.DescribeProcess(OWS.Identifier('hello'))
        resp = self.client.post_xml(doc=request_doc)
        self.check_describe_response(resp)


def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DescribeProcessTest),
    ]
    return unittest.TestSuite(suite_list)
