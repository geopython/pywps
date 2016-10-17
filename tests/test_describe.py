##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
from collections import namedtuple
from pywps import Process, Service, LiteralInput, ComplexInput, BoundingBoxInput
from pywps import LiteralOutput, ComplexOutput, BoundingBoxOutput
from pywps import E, WPS, OWS, OGCTYPE, Format, NAMESPACES, OGCUNIT
from pywps.inout.literaltypes import LITERAL_DATA_TYPES
from pywps.app.basic import xpath_ns
from pywps.app.Common import Metadata
from pywps.inout.formats import Format
from pywps.inout.literaltypes import AllowedValue
from pywps.validator.allowed_value import ALLOWEDVALUETYPE

from tests.common import assert_pywps_version, client_for

ProcessDescription = namedtuple('ProcessDescription', ['identifier', 'inputs', 'metadata'])


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
        def hello(request): pass
        def ping(request): pass
        processes = [Process(hello, 'hello', 'Process Hello'), Process(ping, 'ping', 'Process Ping')]
        self.client = client_for(Service(processes=processes))

    def test_get_request_all_args(self):
        resp = self.client.get('?Request=DescribeProcess&service=wps&version=1.0.0&identifier=all')
        identifiers = [desc.identifier for desc in get_describe_result(resp)]
        assert 'ping' in identifiers
        assert 'hello' in identifiers
        assert_pywps_version(resp)

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
        hello_process = Process(
                hello,
                'hello',
                'Process Hello',
                inputs=[LiteralInput('the_name', 'Input name')],
                metadata=[Metadata('process metadata 1', 'http://example.org/1'), Metadata('process metadata 2', 'http://example.org/2')]
        )
        result = self.describe_process(hello_process)
        assert result.inputs == [('the_name', 'literal', 'integer')]
        assert result.metadata == ['process metadata 1', 'process metadata 2']

    def test_one_literal_integer_input(self):
        def hello(request): pass
        hello_process = Process(hello, 'hello',
                                'Process Hello',
                                inputs=[LiteralInput('the_number',
                                                     'Input number',
                                                     data_type='positiveInteger')])
        result = self.describe_process(hello_process)
        assert result.inputs == [('the_number', 'literal', 'positiveInteger')]


class InputDescriptionTest(unittest.TestCase):

    def test_literal_integer_input(self):
        literal = LiteralInput('foo', 'Literal foo', data_type='positiveInteger', uoms=['metre'])
        doc = literal.describe_xml()
        self.assertEqual(doc.tag, E.Input().tag)
        [identifier_el] = xpath_ns(doc, './ows:Identifier')
        self.assertEqual(identifier_el.text, 'foo')
        [type_el] = xpath_ns(doc, './LiteralData/ows:DataType')
        self.assertEqual(type_el.text, 'positiveInteger')
        self.assertEqual(type_el.attrib['{%s}reference' % NAMESPACES['ows']],
            OGCTYPE['positiveInteger'])
        anyvalue = xpath_ns(doc, './LiteralData/ows:AnyValue')
        self.assertEqual(len(anyvalue), 1)

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
        doc = literal.describe_xml()

        allowed_values = xpath_ns(doc, './LiteralData/ows:AllowedValues')
        self.assertEqual(len(allowed_values), 1)

        allowed_value = allowed_values[0]

        values = xpath_ns(allowed_value, './ows:Value')
        ranges = xpath_ns(allowed_value, './ows:Range')

        self.assertEqual(len(values), 2)
        self.assertEqual(len(ranges), 3)

    def test_complex_input_identifier(self):
        complex_in = ComplexInput('foo', 'Complex foo', supported_formats=[Format('bar/baz')])
        doc = complex_in.describe_xml()
        self.assertEqual(doc.tag, E.Input().tag)
        [identifier_el] = xpath_ns(doc, './ows:Identifier')
        self.assertEqual(identifier_el.text, 'foo')

    def test_complex_input_default_and_supported(self):
        complex_in = ComplexInput(
            'foo',
            'Complex foo',
            supported_formats=[
                Format('a/b'),
                Format('c/d')
            ]
        )
        doc = complex_in.describe_xml()
        [default_format] = xpath_ns(doc, './ComplexData/Default/Format')
        [default_mime_el] = xpath_ns(default_format, './MimeType')
        self.assertEqual(default_mime_el.text, 'a/b')
        supported_mime_types = []
        for supported_el in xpath_ns(doc, './ComplexData/Supported/Format'):
            [mime_el] = xpath_ns(supported_el, './MimeType')
            supported_mime_types.append(mime_el.text)
        self.assertEqual(supported_mime_types, ['a/b', 'c/d'])

    def test_bbox_input(self):
        bbox = BoundingBoxInput('bbox', 'BBox foo',
                                crss=["EPSG:4326", "EPSG:3035"])
        doc = bbox.describe_xml()
        [inpt] = xpath_ns(doc, '/Input')
        [default_crs] = xpath_ns(doc, './BoundingBoxData/Default/CRS')
        supported = xpath_ns(doc, './BoundingBoxData/Supported/CRS')
        self.assertEqual(inpt.attrib['minOccurs'], '1')
        self.assertEqual(default_crs.text, 'EPSG:4326')
        self.assertEqual(len(supported), 2)

class OutputDescriptionTest(unittest.TestCase):

    def test_literal_output(self):
        literal = LiteralOutput('literal', 'Literal foo', uoms=['metre'])
        doc = literal.describe_xml()
        [output] = xpath_ns(doc, '/Output')
        [identifier] = xpath_ns(doc, '/Output/ows:Identifier')
        [data_type] = xpath_ns(doc, '/Output/LiteralOutput/ows:DataType')
        [uoms] = xpath_ns(doc, '/Output/LiteralOutput/UOMs')
        [default_uom] = xpath_ns(uoms, './Default/ows:UOM')
        supported_uoms = xpath_ns(uoms, './Supported/ows:UOM')

        assert output is not None
        assert identifier.text == 'literal'
        assert data_type.attrib['{%s}reference' % NAMESPACES['ows']] == OGCTYPE['string']
        assert uoms is not None
        assert default_uom.text == 'metre'
        assert default_uom.attrib['{%s}reference' % NAMESPACES['ows']] == OGCUNIT['metre']
        assert len(supported_uoms) == 1

    def test_complex_output(self):
        complexo = ComplexOutput('complex', 'Complex foo', [Format('GML')])
        doc = complexo.describe_xml()
        [outpt] = xpath_ns(doc, '/Output')
        [default] = xpath_ns(doc, '/Output/ComplexOutput/Default/Format/MimeType')
        supported = xpath_ns(doc,
                             '/Output/ComplexOutput/Supported/Format/MimeType')

        assert default.text == 'application/gml+xml'
        assert len(supported) == 1

    def test_bbox_output(self):
        bbox = BoundingBoxOutput('bbox', 'BBox foo',
                crss=["EPSG:4326"])
        doc = bbox.describe_xml()
        [outpt] = xpath_ns(doc, '/Output')
        [default_crs] = xpath_ns(doc, './BoundingBoxOutput/Default/CRS')
        supported = xpath_ns(doc, './BoundingBoxOutput/Supported/CRS')
        assert default_crs.text == 'EPSG:4326'
        assert len(supported) == 1


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DescribeProcessTest),
        loader.loadTestsFromTestCase(DescribeProcessInputTest),
        loader.loadTestsFromTestCase(InputDescriptionTest),
    ]
    return unittest.TestSuite(suite_list)
