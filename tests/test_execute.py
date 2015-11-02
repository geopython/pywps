import unittest
import lxml.etree
from pywps import Service, Process, LiteralOutput, LiteralInput,\
    BoundingBoxOutput, BoundingBoxInput, Format, ComplexInput, ComplexOutput
from pywps.validator.base import emptyvalidator
from pywps.validator.complexvalidator import validategml
from pywps.exceptions import InvalidParameterValue
from pywps import get_inputs_from_xml, get_output_from_xml
from pywps import E, WPS, OWS
from pywps.app.basic import xpath_ns
from pywps._compat import text_type
from tests.common import client_for, assert_response_success

from pywps._compat import PY2
from pywps._compat import StringIO
if PY2:
    from owslib.ows import BoundingBox


def create_ultimate_question():
    def handler(request, response):
        response.outputs['outvalue'].data = '42'
        return response

    return Process(handler=handler,
                   identifier='ultimate_question',
                   title='Ultimate Question',
                   outputs=[LiteralOutput('outvalue', 'Output Value', data_type='string')])


def create_greeter():
    def greeter(request, response):
        name = request.inputs['name'][0].data
        assert type(name) is text_type
        response.outputs['message'].data = "Hello %s!" % name
        return response

    return Process(handler=greeter,
                   identifier='greeter',
                   title='Greeter',
                   inputs=[LiteralInput('name', 'Input name', data_type='string')],
                   outputs=[LiteralOutput('message', 'Output message', data_type='string')])

def create_bbox_process():
    def bbox_process(request, response):
        coords = request.inputs['mybbox'][0].data
        assert type(coords) == type([])
        assert len(coords) == 4
        assert coords[0] == '15'
        response.outputs['outbbox'].data = coords
        return response

    return Process(handler=bbox_process,
                   identifier='my_bbox_process',
                   title='Bbox process',
                   inputs=[BoundingBoxInput('mybbox', 'Input name', ["EPSG:4326"])],
                   outputs=[BoundingBoxOutput('outbbox', 'Output message', ["EPSG:4326"])])

def create_complex_proces():
    def complex_proces(request, response):
        response.outputs['complex'].data = request.inputs['complex'][0].data
        return response

    frmt = Format(mime_type='application/gml') # this is unknown mimetype

    return Process(handler=complex_proces,
            identifier='my_complex_process',
            title='Complex process',
            inputs=[
                ComplexInput(
                    'complex',
                    'Complex input',
                    supported_formats=[frmt])
            ],
            outputs=[
                ComplexOutput(
                    'complex',
                    'Complex output',
                    supported_formats=[frmt])
             ])


def get_output(doc):
    output = {}
    for output_el in xpath_ns(doc, '/wps:ExecuteResponse'
                                   '/wps:ProcessOutputs/wps:Output'):
        [identifier_el] = xpath_ns(output_el, './ows:Identifier')
        [value_el] = xpath_ns(output_el, './wps:Data/wps:LiteralData')
        output[identifier_el.text] = value_el.text
    return output


class ExecuteTest(unittest.TestCase):
    """Test for Exeucte request KVP request"""

    def test_input_parser(self):
        """Test input parsing
        """
        my_process = create_complex_proces()
        service = Service(processes=[my_process])
        self.assertEqual(len(service.processes.keys()), 1)
        self.assertTrue(service.processes['my_complex_process'])

        class FakeRequest():
            identifier = 'complex_process'
            service='wps'
            version='1.0.0'
            inputs = {'complex': [{
                    'identifier': 'complex',
                    'mimeType': 'text/gml',
                    'data': 'the data'
                }]}
        request = FakeRequest();

        try:
            service.execute('my_complex_process', request)
        except InvalidParameterValue as e:
            self.assertEqual(e.locator, 'mimeType')

        request.inputs['complex'][0]['mimeType'] = 'application/gml'
        parsed_inputs = service.create_complex_inputs(my_process.inputs[0],
                                                      request.inputs['complex'])

        # TODO parse outputs and their validators too

        self.assertEqual(parsed_inputs[0].data_format.validate, emptyvalidator)

        request.inputs['complex'][0]['mimeType'] = 'application/xml+gml'
        try:
            parsed_inputs = service.create_complex_inputs(my_process.inputs[0],
                                                      request.inputs['complex'])
        except InvalidParameterValue as e:
            self.assertEqual(e.locator, 'mimeType')

        try:
            my_process.inputs[0].data_format = Format(mime_type='application/xml+gml')
        except InvalidParameterValue as e:
            self.assertEqual(e.locator, 'mimeType')

        frmt = Format(mime_type='application/xml+gml', validate=validategml)
        self.assertEqual(frmt.validate, validategml)

        my_process.inputs[0].supported_formats = [frmt]
        my_process.inputs[0].data_format = Format(mime_type='application/xml+gml')
        parsed_inputs = service.create_complex_inputs(my_process.inputs[0],
                                              request.inputs['complex'])

        self.assertEqual(parsed_inputs[0].data_format.validate, validategml)


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

    def test_bbox(self):
        if not PY2:
            self.skipTest('OWSlib not python 3 compatible')
        client = client_for(Service(processes=[create_bbox_process()]))
        request_doc = WPS.Execute(
            OWS.Identifier('my_bbox_process'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('mybbox'),
                    WPS.Data(WPS.BoundingBoxData(
                        OWS.LowerCorner('15 50'),
                        OWS.UpperCorner('16 51'),
                        ))
                )
            ),
            version='1.0.0'
        )
        resp = client.post_xml(doc=request_doc)
        assert_response_success(resp)

        [output] = xpath_ns(resp.xml, '/wps:ExecuteResponse'
                                   '/wps:ProcessOutputs/Output')
        self.assertEqual('outbbox', xpath_ns(output,
            './ows:Identifier')[0].text)
        self.assertEqual('15 50', xpath_ns(output,
            './ows:BoundingBox/ows:LowerCorner')[0].text)

class ExecuteXmlParserTest(unittest.TestCase):
    """Tests for Execute request XML Parser
    """

    def test_empty(self):
        request_doc = WPS.Execute(OWS.Identifier('foo'))
        assert get_inputs_from_xml(request_doc) == {}

    def test_one_string(self):
        request_doc = WPS.Execute(
            OWS.Identifier('foo'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('name'),
                    WPS.Data(WPS.LiteralData('foo'))),
                WPS.Input(
                    OWS.Identifier('name'),
                    WPS.Data(WPS.LiteralData('bar')))
                ))
        rv = get_inputs_from_xml(request_doc)
        assert 'name' in rv
        assert len(rv['name']) == 2
        assert rv['name'][0]['data'] == 'foo'
        assert rv['name'][1]['data'] == 'bar'

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
        rv = get_inputs_from_xml(request_doc)
        assert rv['name1'][0]['data'] == 'foo'
        assert rv['name2'][0]['data'] == 'bar'

    def test_complex_input(self):
        the_data = E.TheData("hello world")
        request_doc = WPS.Execute(
            OWS.Identifier('foo'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('name'),
                    WPS.Data(
                        WPS.ComplexData(the_data, mimeType='text/foobar')))))
        rv = get_inputs_from_xml(request_doc)
        assert rv['name'][0]['mimeType'] == 'text/foobar'
        rv_doc = lxml.etree.parse(StringIO(rv['name'][0]['data'])).getroot()
        assert rv_doc.tag == 'TheData'
        assert rv_doc.text == "hello world"

    def test_bbox_input(self):
        if not PY2:
            self.skipTest('OWSlib not python 3 compatible')
        request_doc = WPS.Execute(
            OWS.Identifier('request'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('bbox'),
                    WPS.Data(
                        WPS.BoundingBoxData(
                            OWS.LowerCorner('40 50'),
                            OWS.UpperCorner('60 70'))))))
        rv = get_inputs_from_xml(request_doc)
        bbox = rv['bbox'][0]
        assert isinstance(bbox, BoundingBox)
        assert bbox.minx == '40'
        assert bbox.miny == '50'
        assert bbox.maxx == '60'
        assert bbox.maxy == '70'

def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTest),
        loader.loadTestsFromTestCase(ExecuteXmlParserTest),
    ]
    return unittest.TestSuite(suite_list)
