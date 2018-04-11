##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
from collections import namedtuple
from pywps import Process, Service, LiteralInput, ComplexInput, BoundingBoxInput
from pywps import LiteralOutput, ComplexOutput, BoundingBoxOutput
from pywps import E, get_ElementMakerForVersion, OGCTYPE, Format, NAMESPACES, OGCUNIT
from pywps.inout.literaltypes import LITERAL_DATA_TYPES
from pywps.app.basic import get_xpath_ns
from pywps.app.Common import Metadata
from pywps.inout.formats import Format
from pywps.inout.literaltypes import AllowedValue
from pywps.validator.allowed_value import ALLOWEDVALUETYPE
from pywps.exceptions import InvalidParameterValue
from pywps.exceptions import MissingParameterValue

from pywps.tests import assert_pywps_version, client_for
from pywps.tests import assert_process_exception

ProcessDescription = namedtuple('ProcessDescription', ['identifier', 'inputs', 'metadata'])

WPS, OWS = get_ElementMakerForVersion("1.0.0")


def get_data_type(el):
    if el.text in LITERAL_DATA_TYPES:
        return el.text
    raise RuntimeError("Can't parse data type")

xpath_ns = get_xpath_ns("1.0.0")


def get_describe_result(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    result = []
    for desc_el in resp.xpath('/wps:ProcessDescriptions/ProcessDescription'):
        [identifier_el] = xpath_ns(desc_el, './ows:Identifier')
        inputs = []
        metadata = []
        for metadata_el in xpath_ns(desc_el, './ows:Metadata'):
            metadata.append(metadata_el.attrib['{http://www.w3.org/1999/xlink}title'])
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
        result.append(ProcessDescription(identifier_el.text, inputs, metadata))
    return result


class DescribeProcessTest(unittest.TestCase):

    def setUp(self):
        def hello(request):
            pass

        def ping(request):
            pass
        processes = [
            Process(hello, 'hello', 'Process Hello', metadata=[
                Metadata('hello metadata', 'http://example.org/hello',
                         role='http://www.opengis.net/spec/wps/2.0/def/process/description/documentation')]),
            Process(ping, 'ping', 'Process Ping', metadata=[Metadata('ping metadata', 'http://example.org/ping')]),
        ]
        self.client = client_for(Service(processes=processes))

    def test_get_request_all_args(self):
        resp = self.client.get('?Request=DescribeProcess&service=wps&version=1.0.0&identifier=all')
        identifiers = [desc.identifier for desc in get_describe_result(resp)]
        metadata = [desc.metadata for desc in get_describe_result(resp)]

        assert 'ping' in identifiers
        assert 'hello' in identifiers
        assert_pywps_version(resp)
        assert 'hello metadata' in [item for sublist in metadata for item in sublist]

    def test_get_request_zero_args(self):
        resp = self.client.get('?Request=DescribeProcess&version=1.0.0&service=wps')
        assert resp.status_code == 400

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

    def test_post_two_args(self):
        request_doc = WPS.DescribeProcess(
            OWS.Identifier('hello'),
            OWS.Identifier('ping'),
            version='1.0.0'
        )
        resp = self.client.post_xml(doc=request_doc)
        result = get_describe_result(resp)
        #print(b"\n".join(resp.response).decode("utf-8"))
        assert [pr.identifier for pr in result] == ['hello', 'ping']


class DescribeProcessInputTest(unittest.TestCase):

    def describe_process(self, process):
        client = client_for(Service(processes=[process]))
        resp = client.get('?service=wps&version=1.0.0&Request=DescribeProcess&identifier=%s'
                          % process.identifier)
        [result] = get_describe_result(resp)
        return result

    def test_one_literal_string_input(self):
        def hello(request):
            pass
        hello_process = Process(
            hello,
            'hello',
            'Process Hello',
            inputs=[LiteralInput('the_name', 'Input name')],
            metadata=[
                Metadata('process metadata 1', 'http://example.org/1'),
                Metadata('process metadata 2', 'http://example.org/2')]
        )
        result = self.describe_process(hello_process)
        assert result.inputs == [('the_name', 'literal', 'integer')]
        assert result.metadata == ['process metadata 1', 'process metadata 2']

    def test_one_literal_integer_input(self):
        def hello(request):
            pass
        hello_process = Process(hello, 'hello',
                                'Process Hello',
                                inputs=[LiteralInput('the_number',
                                                     'Input number',
                                                     data_type='positiveInteger')])
        result = self.describe_process(hello_process)
        assert result.inputs == [('the_number', 'literal', 'positiveInteger')]


class InputDescriptionTest(unittest.TestCase):

    def test_literal_integer_input(self):
        literal = LiteralInput('foo', 'Literal foo', data_type='positiveInteger', keywords=['kw1', 'kw2'], uoms=['metre'])
        data = literal.json
        assert data["identifier"] == "foo"
        assert data["data_type"] == "positiveInteger"

    def test_literal_allowed_values_input(self):
        """Test all around allowed_values
        """
        literal = LiteralInput(
            'foo',
            'Foo',
            data_type='integer',
            uoms=['metre'],
            allowed_values=(
                1, 2, (5, 10), (12, 4, 24),
                AllowedValue(
                    allowed_type=ALLOWEDVALUETYPE.RANGE,
                    minval=30,
                    maxval=33,
                    range_closure='closed-open')
            )
        )
        data = literal.json
        assert len(data["allowed_values"]) == 5
        assert data["allowed_values"][0]["value"] == 1
        assert data["allowed_values"][0]["range_closure"] == "closed"

    def test_complex_input_identifier(self):
        complex_in = ComplexInput('foo', 'Complex foo', keywords=['kw1', 'kw2'], supported_formats=[Format('bar/baz')])
        data = complex_in.json
        assert data["identifier"] == "foo"
        assert len(data["keywords"]) == 2

    def test_complex_input_default_and_supported(self):
        complex_in = ComplexInput(
            'foo',
            'Complex foo',
            supported_formats=[
                Format('a/b'),
                Format('c/d')
            ]
        )
        data = complex_in.json
        assert len(data["supported_formats"]) == 2
        assert data["data_format"]["mime_type"] == "a/b"

    def test_bbox_input(self):
        bbox = BoundingBoxInput('bbox', 'BBox foo', keywords=['kw1', 'kw2'],
                                crss=["EPSG:4326", "EPSG:3035"])
        data = bbox.json
        assert data["identifier"] == "bbox"
        assert len(data["keywords"]) == 2
        assert len(data["crss"]) == 2
        assert data["crss"][0] == "EPSG:4326"
        assert data["dimensions"] == 2

class OutputDescriptionTest(unittest.TestCase):

    def test_literal_output(self):
        literal = LiteralOutput('literal', 'Literal foo', abstract='Description', keywords=['kw1', 'kw2'], uoms=['metre'])
        doc = literal.describe_xml()
        [output] = xpath_ns(doc, '/Output')
        [identifier] = xpath_ns(doc, '/Output/ows:Identifier')
        [abstract] = xpath_ns(doc, '/Output/ows:Abstract')
        [keywords] = xpath_ns(doc, '/Output/ows:Keywords')
        kws = xpath_ns(keywords, './ows:Keyword')
        [data_type] = xpath_ns(doc, '/Output/LiteralOutput/ows:DataType')
        [uoms] = xpath_ns(doc, '/Output/LiteralOutput/UOMs')
        [default_uom] = xpath_ns(uoms, './Default/ows:UOM')
        supported_uoms = xpath_ns(uoms, './Supported/ows:UOM')

        assert output is not None
        assert identifier.text == 'literal'
        assert abstract.text == 'Description'
        assert keywords is not None
        assert len(kws) == 2
        assert data_type.attrib['{%s}reference' % NAMESPACES['ows']] == OGCTYPE['string']
        assert uoms is not None
        assert default_uom.text == 'metre'
        assert default_uom.attrib['{%s}reference' % NAMESPACES['ows']] == OGCUNIT['metre']
        assert len(supported_uoms) == 1

    def test_complex_output(self):
        complexo = ComplexOutput('complex', 'Complex foo', [Format('GML')], keywords=['kw1', 'kw2'])
        doc = complexo.describe_xml()
        [outpt] = xpath_ns(doc, '/Output')
        [default] = xpath_ns(doc, '/Output/ComplexOutput/Default/Format/MimeType')
        supported = xpath_ns(doc,
                             '/Output/ComplexOutput/Supported/Format/MimeType')

        assert default.text == 'application/gml+xml'
        assert len(supported) == 1
        [keywords] = xpath_ns(doc, '/Output/ows:Keywords')
        kws = xpath_ns(keywords, './ows:Keyword')
        assert keywords is not None
        assert len(kws) == 2

    def test_bbox_output(self):
        bbox = BoundingBoxOutput('bbox', 'BBox foo', keywords=['kw1', 'kw2'],
                                 crss=["EPSG:4326"])
        doc = bbox.describe_xml()
        [outpt] = xpath_ns(doc, '/Output')
        [default_crs] = xpath_ns(doc, './BoundingBoxOutput/Default/CRS')
        supported = xpath_ns(doc, './BoundingBoxOutput/Supported/CRS')
        assert default_crs.text == 'EPSG:4326'
        assert len(supported) == 1
        [keywords] = xpath_ns(doc, '/Output/ows:Keywords')
        kws = xpath_ns(keywords, './ows:Keyword')
        assert keywords is not None
        assert len(kws) == 2


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DescribeProcessTest),
        loader.loadTestsFromTestCase(DescribeProcessInputTest),
        loader.loadTestsFromTestCase(InputDescriptionTest),
    ]
    return unittest.TestSuite(suite_list)
