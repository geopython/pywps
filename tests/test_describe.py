import unittest
from collections import namedtuple
from pywps.app import Process, Service, xpath_ns, WPS, OWS, LiteralInput
from tests.common import client_for

ProcessDescription = namedtuple('ProcessDescription', ['identifier', 'inputs'])


def get_describe_result(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    result = []
    for desc_el in resp.xpath('/wps:ProcessDescriptions/ProcessDescription'):
        [identifier_el] = xpath_ns(desc_el, './ows:Identifier')
        inputs = []
        for input_el in xpath_ns(desc_el, './DataInputs/Input'):
            [input_identifier_el] = xpath_ns(input_el, './ows:Identifier')
            inputs.append((input_identifier_el.text,))
        result.append(ProcessDescription(identifier_el.text, inputs))
    return result


class DescribeProcessTest(unittest.TestCase):

    def setUp(self):
        def hello(request): pass
        def ping(request): pass
        processes = [Process(hello), Process(ping)]
        self.client = client_for(Service(processes=processes))

    def test_get_request_zero_args(self):
        resp = self.client.get('?Request=DescribeProcess')
        assert [pr.identifier for pr in get_describe_result(resp)] == []

    def test_post_request_zero_args(self):
        request_doc = WPS.DescribeProcess()
        resp = self.client.post_xml(doc=request_doc)
        assert [pr.identifier for pr in get_describe_result(resp)] == []

    def test_get_one_arg(self):
        resp = self.client.get('?Request=DescribeProcess&identifier=hello')
        assert [pr.identifier for pr in get_describe_result(resp)] == ['hello']

    def test_post_one_arg(self):
        request_doc = WPS.DescribeProcess(OWS.Identifier('hello'))
        resp = self.client.post_xml(doc=request_doc)
        assert [pr.identifier for pr in get_describe_result(resp)] == ['hello']

    def test_get_two_args(self):
        resp = self.client.get('?Request=DescribeProcess'
                               '&identifier=hello'
                               '&identifier=ping')
        result = get_describe_result(resp)
        assert [pr.identifier for pr in result] == ['hello', 'ping']

    def test_post_two_args(self):
        request_doc = WPS.DescribeProcess(
            OWS.Identifier('hello'),
            OWS.Identifier('ping'))
        resp = self.client.post_xml(doc=request_doc)
        result = get_describe_result(resp)
        assert [pr.identifier for pr in result] == ['hello', 'ping']


class DescribeProcessInputTest(unittest.TestCase):

    def test_one_literal_input(self):
        def hello(request): pass
        hello_process = Process(hello, inputs=[LiteralInput('the_name')])
        client = client_for(Service(processes=[hello_process]))
        resp = client.get('?Request=DescribeProcess&identifier=hello')
        [result] = get_describe_result(resp)
        assert result.inputs == [('the_name',)]


def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DescribeProcessTest),
        loader.loadTestsFromTestCase(DescribeProcessInputTest),
    ]
    return unittest.TestSuite(suite_list)
