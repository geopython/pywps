from io import StringIO
import unittest
import lxml.etree
from pywps import Service, Process, WPSResponse, LiteralOutput, LiteralInput
from pywps.app import E, WPS, OWS, NAMESPACES, get_input_from_xml, xpath_ns
from pywps._compat import text_type
from tests.common import client_for


def create_ultimate_question():
    def handler(request, response):
        response.outputs['outvalue'].setvalue('42')
        return response

    return Process(identifier='ultimate_question',
                   outputs=[LiteralOutput('outvalue', 'Output Value', data_type='string')],
                   handler=handler)


def create_greeter():
    def greeter(request, response):
        name = request.inputs['name'].getvalue()
        assert type(name) is text_type
        response.outputs['message'].setvalue("Hello %s!" % name)
        return response

    return Process(handler=greeter,
                   inputs=[LiteralInput('name', data_type='string')],
                   outputs=[LiteralOutput('message', data_type='string')])


def get_output(doc):
    output = {}
    for output_el in xpath_ns(doc, '/wps:ExecuteResponse'
                                   '/wps:ProcessOutputs/wps:Output'):
        [identifier_el] = xpath_ns(output_el, './ows:Identifier')
        [value_el] = xpath_ns(output_el, './wps:Data/wps:LiteralData')
        output[identifier_el.text] = value_el.text
    return output


def assert_response_success(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    success = resp.xpath_text('/wps:ExecuteResponse'
                              '/wps:Status'
                              '/wps:ProcessSucceeded')
    assert success == "great success"


class ExecuteTest(unittest.TestCase):
    """Test for Exeucte request KVP request"""

    def test_missing_process_error(self):
        client = client_for(Service(processes=[create_ultimate_question()]))
        resp = client.get('?Request=Execute&identifier=foo')
        assert resp.status_code == 400

    def test_get_with_no_inputs(self):
        client = client_for(Service(processes=[create_ultimate_question()]))
        resp = client.get('?service=wps&version=1.0.0&Request=Execute&identifier=ultimate_question')
        assert_response_success(resp)
        assert get_output(resp.xml) == {'outvalue': '42'}

    def test_post_with_no_inputs(self):
        client = client_for(Service(processes=[create_ultimate_question()]))
        request_doc = WPS.Execute(
            OWS.Identifier('ultimate_question'),
            version='1.0.0'
        )
        resp = client.post_xml(doc=request_doc)
        assert_response_success(resp)
        assert get_output(resp.xml) == {'outvalue': '42'}

    def test_post_with_string_input(self):
        client = client_for(Service(processes=[create_greeter()]))
        request_doc = WPS.Execute(
            OWS.Identifier('greeter'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('name'),
                    WPS.Data(WPS.LiteralData('foo'))
                )
            ),
            version='1.0.0'
        )
        resp = client.post_xml(doc=request_doc)
        assert_response_success(resp)
        assert get_output(resp.xml) == {'message': "Hello foo!"}

class ExecuteXmlParserTest(unittest.TestCase):
    """Tests for Execute request XML Parser
    """

    def test_empty(self):
        request_doc = WPS.Execute(OWS.Identifier('foo'))
        assert get_input_from_xml(request_doc) == {}

    def test_one_string(self):
        request_doc = WPS.Execute(
            OWS.Identifier('foo'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('name'),
                    WPS.Data(WPS.LiteralData('foo')))))
        rv = get_input_from_xml(request_doc)
        assert 'name' in rv
        assert rv['name']['data'] == 'foo'

    def test_two_strings(self):
        request_doc = WPS.Execute(
            OWS.Identifier('foo'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('name1'),
                    WPS.Data(WPS.LiteralData('foo'))),
                WPS.Input(
                    OWS.Identifier('name2'),
                    WPS.Data(WPS.LiteralData('bar')))))
        rv = get_input_from_xml(request_doc)
        assert rv['name1']['data'] == 'foo'
        assert rv['name2']['data'] == 'bar'

    def test_complex_input(self):
        the_data = E.TheData("hello world")
        request_doc = WPS.Execute(
            OWS.Identifier('foo'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('name'),
                    WPS.Data(
                        WPS.ComplexData(the_data, mimeType='text/foobar')))))
        rv = get_input_from_xml(request_doc)
        assert rv['name']['mime_type'] == 'text/foobar'
        rv_doc = lxml.etree.parse(StringIO(lxml.etree.tounicode(rv['name']['data']))).getroot()
        assert rv_doc.tag == 'TheData'
        assert rv_doc.text == "hello world"


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTest),
        loader.loadTestsFromTestCase(ExecuteXmlParserTest),
    ]
    return unittest.TestSuite(suite_list)
