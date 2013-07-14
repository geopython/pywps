import unittest
from collections import namedtuple
from pywps.app import (Process, Service, xpath_ns, WPS, OWS, LiteralInput,
                       xmlschema_2, LITERAL_DATA_TYPES)
from tests.common import client_for

ProcessDescription = namedtuple('ProcessDescription', ['identifier', 'inputs'])


def get_data_type(el):
    for datatype in LITERAL_DATA_TYPES:
        if el.attrib['reference'] == xmlschema_2 + datatype:
            assert el.text == datatype
            return el.text
    raise RuntimeError("Can't parse data type")


def get_describe_result(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    result = []
    for desc_el in resp.xpath('/wps:ProcessDescriptions/ProcessDescription'):
        [identifier_el] = xpath_ns(desc_el, './ows:Identifier')
        inputs = []
        for input_el in xpath_ns(desc_el, './DataInputs/Input'):
            [input_identifier_el] = xpath_ns(input_el, './ows:Identifier')
            literal_data_el_list = xpath_ns(input_el, './LiteralData')
            if literal_data_el_list:
                [literal_data_el] = literal_data_el_list
                [data_type_el] = xpath_ns(literal_data_el, './ows:DataType')
                data_type = get_data_type(data_type_el)
                inputs.append((input_identifier_el.text, 'literal', data_type))
            else:
                raise RuntimeError("Can't parse input description")
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

    def test_one_literal_string_input(self):
        def hello(request): pass
        hello_process = Process(hello, inputs=[LiteralInput('the_name')])
        client = client_for(Service(processes=[hello_process]))
        resp = client.get('?Request=DescribeProcess&identifier=hello')
        [result] = get_describe_result(resp)
        assert result.inputs == [('the_name', 'literal', 'string')]

    def test_one_literal_integer_input(self):
        def hello(request): pass
        hello_process = Process(hello, inputs=[
            LiteralInput('the_number', 'integer')])
        client = client_for(Service(processes=[hello_process]))
        resp = client.get('?Request=DescribeProcess&identifier=hello')
        [result] = get_describe_result(resp)
        assert result.inputs == [('the_number', 'literal', 'integer')]


def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DescribeProcessTest),
        loader.loadTestsFromTestCase(DescribeProcessInputTest),
    ]
    return unittest.TestSuite(suite_list)
