import unittest
from pywps.app import Process, Service, xpath_ns, WPS, OWS
from tests.common import client_for


def get_describe_result(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    result = []
    for desc_el in resp.xpath('/wps:ProcessDescriptions'
                              '/wps:ProcessDescription'):
        [identifier_el] = xpath_ns(desc_el, './ows:Identifier')
        result.append((identifier_el.text,))
    return result

class DescribeProcessTest(unittest.TestCase):

    def setUp(self):
        def hello(request): pass
        hello_process = Process(hello)
        self.client = client_for(Service(processes=[hello_process]))

    def test_get_request(self):
        resp = self.client.get('?Request=DescribeProcess&identifier=hello')
        assert [ident for (ident,) in get_describe_result(resp)] == ['hello']

    def test_post_request(self):
        request_doc = WPS.DescribeProcess(OWS.Identifier('hello'))
        resp = self.client.post_xml(doc=request_doc)
        assert [ident for (ident,) in get_describe_result(resp)] == ['hello']


def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DescribeProcessTest),
    ]
    return unittest.TestSuite(suite_list)
