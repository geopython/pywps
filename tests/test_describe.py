import unittest
from collections import namedtuple
from pywps import Process, Service, LiteralInput, ComplexInput
from pywps.app import E, WPS, OWS, xpath_ns, xmlschema_2, LITERAL_DATA_TYPES, Format
from tests.common import client_for

ProcessDescription = namedtuple('ProcessDescription', ['identifier', 'inputs'])


def get_data_type(el):
    if el.text in LITERAL_DATA_TYPES:
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
            input_identifier = input_identifier_el.text
            literal_data_el_list = xpath_ns(input_el, './LiteralData')
            complex_data_el_list = xpath_ns(input_el, './ComplexData')
            if literal_data_el_list:
                [literal_data_el] = literal_data_el_list
                [data_type_el] = xpath_ns(literal_data_el, './ows:DataType')
                data_type = get_data_type(data_type_el)
                inputs.append((input_identifier, 'literal', data_type))
            elif complex_data_el_list:
                [complex_data_el] = complex_data_el_list
                formats = []
                for format_el in xpath_ns(complex_data_el,
                                          './Supported/Format'):
                    [mimetype_el] = xpath_ns(format_el, './ows:MimeType')
                    formats.append({'mime_type': mimetype_el.text})
                inputs.append((input_identifier, 'complex', formats))
            else:
                raise RuntimeError("Can't parse input description")
        result.append(ProcessDescription(identifier_el.text, inputs))
    return result


class DescribeProcessTest(unittest.TestCase):

    def setUp(self):
        def hello(request): pass
        def ping(request): pass
        processes = [Process(hello, 'hello', 'Process Hello'), Process(ping, 'ping', 'Process Ping')]
        self.client = client_for(Service(processes=processes))

    def test_get_request_all_args(self):
        resp = self.client.get('?Request=DescribeProcess&service=wps&version=1.0.0&identifier=all')
        identifiers = [desc.identifier for desc in get_describe_result(resp)]
        assert 'ping' in identifiers
        assert 'hello' in identifiers

    def test_get_request_zero_args(self):
        resp = self.client.get('?Request=DescribeProcess&version=1.0.0&service=wps')
        assert resp.status_code == 400 # bad request, identifier is missing

    def test_get_request_nonexisting_process_args(self):
        resp = self.client.get('?Request=DescribeProcess&version=1.0.0&service=wps&identifier=NONEXISTINGPROCESS')
        assert resp.status_code == 400

    def test_post_request_zero_args(self):
        request_doc = WPS.DescribeProcess()
        resp = self.client.post_xml(doc=request_doc)
        assert resp.status_code == 400

    def test_get_one_arg(self):
        resp = self.client.get('?service=wps&version=1.0.0&Request=DescribeProcess&identifier=hello')
        assert [pr.identifier for pr in get_describe_result(resp)] == ['hello']

    def test_post_one_arg(self):
        request_doc = WPS.DescribeProcess(
            OWS.Identifier('hello'),
            version='1.0.0'
        )
        resp = self.client.post_xml(doc=request_doc)
        assert [pr.identifier for pr in get_describe_result(resp)] == ['hello']

    def test_get_two_args(self):
        resp = self.client.get('?Request=DescribeProcess'
                               '&service=wps'
                               '&version=1.0.0'
                               '&identifier=hello,ping')
        result = get_describe_result(resp)
        assert [pr.identifier for pr in result] == ['hello', 'ping']

    def test_post_two_args(self):
        request_doc = WPS.DescribeProcess(
            OWS.Identifier('hello'),
            OWS.Identifier('ping'),
            version='1.0.0'
        )
        resp = self.client.post_xml(doc=request_doc)
        result = get_describe_result(resp)
        assert [pr.identifier for pr in result] == ['hello', 'ping']


class DescribeProcessInputTest(unittest.TestCase):

    def describe_process(self, process):
        client = client_for(Service(processes=[process]))
        resp = client.get('?service=wps&version=1.0.0&Request=DescribeProcess&identifier=%s'
                          % process.identifier)
        [result] = get_describe_result(resp)
        return result

    def test_one_literal_string_input(self):
        def hello(request): pass
        hello_process = Process(hello, 'hello', 'Process Hello', inputs=[LiteralInput('the_name', 'Input name')])
        result = self.describe_process(hello_process)
        assert result.inputs == [('the_name', 'literal', 'string')]

    def test_one_literal_integer_input(self):
        def hello(request): pass
        hello_process = Process(hello, 'hello', 'Process Hello', inputs=[
            LiteralInput('the_number', 'Input number', data_type='integer')])
        result = self.describe_process(hello_process)
        assert result.inputs == [('the_number', 'literal', 'integer')]


class InputDescriptionTest(unittest.TestCase):

    def test_literal_integer_input(self):
        literal = LiteralInput('foo', 'Literal foo', data_type='integer')
        doc = literal.describe_xml()
        assert doc.tag == E.Input().tag
        [identifier_el] = xpath_ns(doc, './ows:Identifier')
        assert identifier_el.text == 'foo'
        [type_el] = xpath_ns(doc, './LiteralData/ows:DataType')
        assert type_el.text == 'integer'
        assert type_el.attrib['reference'] == xmlschema_2 + 'integer'

    def test_complex_input_identifier(self):
        complex = ComplexInput('foo', 'Complex foo', allowed_formats=[Format('bar/baz')])
        doc = complex.describe_xml()
        assert doc.tag == E.Input().tag
        [identifier_el] = xpath_ns(doc, './ows:Identifier')
        assert identifier_el.text == 'foo'

    def test_complex_input_default_and_supported(self):
        complex = ComplexInput('foo', 'Complex foo', allowed_formats=[Format('a/b'), Format('c/d')])
        doc = complex.describe_xml()
        [default_format] = xpath_ns(doc, './ComplexData/Default/Format')
        [default_mime_el] = xpath_ns(default_format, './MimeType')
        assert default_mime_el.text == 'a/b'
        supported_mime_types = []
        for supported_el in xpath_ns(doc, './ComplexData/Supported/Format'):
            [mime_el] = xpath_ns(supported_el, './MimeType')
            supported_mime_types.append(mime_el.text)
        assert supported_mime_types == ['a/b', 'c/d']


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DescribeProcessTest),
        loader.loadTestsFromTestCase(DescribeProcessInputTest),
        loader.loadTestsFromTestCase(InputDescriptionTest),
    ]
    return unittest.TestSuite(suite_list)
