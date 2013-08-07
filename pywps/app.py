"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from werkzeug.datastructures import MultiDict
import lxml.etree
from lxml.builder import ElementMaker
from pywps._compat import text_type, StringIO


xmlschema_2 = "http://www.w3.org/TR/xmlschema-2/#"
LITERAL_DATA_TYPES = ['string', 'float', 'integer', 'boolean']

NAMESPACES = {
  'wps': "http://www.opengis.net/wps/1.0.0",
  'ows': "http://www.opengis.net/ows/1.1",
  'gml': "http://www.opengis.net/gml",
}

E = ElementMaker()
WPS = ElementMaker(namespace=NAMESPACES['wps'], nsmap=NAMESPACES)
OWS = ElementMaker(namespace=NAMESPACES['ows'], nsmap=NAMESPACES)


def xpath_ns(el, path):
    return el.xpath(path, namespaces=NAMESPACES)


def xml_response(doc):
    return Response(lxml.etree.tostring(doc, pretty_print=True),
                    content_type='text/xml')


def get_input_from_xml(doc):
    the_input = MultiDict()
    for input_el in xpath_ns(doc, '/wps:Execute/wps:DataInputs/wps:Input'):
        [identifier_el] = xpath_ns(input_el, './ows:Identifier')

        literal_data = xpath_ns(input_el, './wps:Data/wps:LiteralData')
        if literal_data:
            value_el = literal_data[0]
            the_input.update({identifier_el.text: text_type(value_el.text)})
            continue

        complex_data = xpath_ns(input_el, './wps:Data/wps:ComplexData')
        if complex_data:
            complex_data_el = complex_data[0]
            value_el = complex_data_el[0]
            tmp = StringIO(lxml.etree.tounicode(value_el))
            tmp.mime_type = complex_data_el.attrib.get('mimeType')
            the_input.update({identifier_el.text: tmp})
            continue

    return the_input


class WPSRequest(object):

    def __init__(self, http_request):
        self.http_request = http_request

        if http_request.method == 'GET':
            self.operation = http_request.args['Request']

            if self.operation == 'GetCapabilities':
                pass

            elif self.operation == 'DescribeProcess':
                self.identifiers = http_request.args.getlist('identifier')

            elif self.operation == 'Execute':
                self.identifier = http_request.args['identifier']

            else:
                raise BadRequest("Unknown request type %r" % self.operation)

        elif http_request.method == 'POST':
            doc = lxml.etree.fromstring(http_request.get_data())

            if doc.tag == WPS.GetCapabilities().tag:
                self.operation = 'GetCapabilities'

            elif doc.tag == WPS.DescribeProcess().tag:
                self.operation = 'DescribeProcess'
                self.identifiers = [identifier_el.text for identifier_el in
                                    xpath_ns(doc, './ows:Identifier')]

            elif doc.tag == WPS.Execute().tag:
                self.operation = 'Execute'
                self.identifier = xpath_ns(doc, './ows:Identifier')[0].text
                self.inputs = get_input_from_xml(doc)

            else:
                raise BadRequest("Unknown request type %r" % doc.tag)

        else:
            raise MethodNotAllowed()


class WPSResponse(object):

    def __init__(self, outputs=None):
        self.outputs = outputs or {}

    @Request.application
    def __call__(self, request):
        output_elements = []
        for key, value in self.outputs.items():
            output_elements.append(WPS.Output(
                OWS.Identifier(key),
                WPS.Data(WPS.LiteralData(value))
            ))

        doc = WPS.ExecuteResponse(
            WPS.Status(
                WPS.ProcessSucceeded("great success")
            ),
            WPS.ProcessOutputs(*output_elements)
        )
        return xml_response(doc)


class LiteralInput(object):

    def __init__(self, identifier, data_type='string'):
        self.identifier = identifier
        assert data_type in LITERAL_DATA_TYPES
        self.data_type = data_type

    def describe_xml(self):
        return E.Input(
            OWS.Identifier(self.identifier),
            E.LiteralData(
                OWS.DataType(self.data_type,
                             reference=xmlschema_2 + self.data_type)
            )
        )


class ComplexInput(object):

    def __init__(self, identifier, formats):
        self.identifier = identifier
        self.formats = formats

    def describe_xml(self):
        default_format_el = self.formats[0].describe_xml()
        supported_format_elements = [f.describe_xml() for f in self.formats]
        return E.Input(
            OWS.Identifier(self.identifier),
            E.ComplexData(
                E.Default(default_format_el),
                E.Supported(*supported_format_elements)
            )
        )


class Format(object):

    def __init__(self, mime_type):
        self.mime_type = mime_type

    def describe_xml(self):
        return E.Format(OWS.MimeType(self.mime_type))


class Process(object):
    """ WPS process """

    def __init__(self, handler, identifier=None, inputs=[]):
        self.identifier = identifier or handler.__name__
        self.handler = handler
        self.inputs = inputs

    def capabilities_xml(self):
        return WPS.Process(OWS.Identifier(self.identifier))

    def describe_xml(self):
        input_elements = [i.describe_xml() for i in self.inputs]
        return E.ProcessDescription(
            OWS.Identifier(self.identifier),
            E.DataInputs(*input_elements)
        )

    def execute(self, wps_request):
        return self.handler(wps_request)


class Service(object):
    """ WPS service """

    def __init__(self, processes=[]):
        self.processes = {p.identifier: p for p in processes}

    def get_capabilities(self):
        process_elements = [p.capabilities_xml()
                            for p in self.processes.values()]

        doc = WPS.Capabilities(
            OWS.ServiceIdentification(
                OWS.Title('PyWPS Server')
            ),
            WPS.ProcessOfferings(*process_elements)
        )

        return xml_response(doc)

    def describe(self, identifiers):
        identifier_elements = []
        for identifier in identifiers:
            try:
                process = self.processes[identifier]
            except KeyError:
                raise BadRequest("Unknown process %r" % identifier)
            else:
                identifier_elements.append(process.describe_xml())
        doc = WPS.ProcessDescriptions(*identifier_elements)
        return xml_response(doc)

    def execute(self, identifier, wps_request):
        try:
            process = self.processes[identifier]
        except KeyError:
            raise BadRequest("Unknown process %r" % identifier)
        return process.execute(wps_request)

    @Request.application
    def __call__(self, http_request):
        try:
            wps_request = WPSRequest(http_request)

            if wps_request.operation == 'GetCapabilities':
                return self.get_capabilities()

            elif wps_request.operation == 'DescribeProcess':
                return self.describe(wps_request.identifiers)

            elif wps_request.operation == 'Execute':
                return self.execute(wps_request.identifier, wps_request)

            else:
                raise RuntimeError("Unknown operation %r"
                                   % wps_request.operation)

        except HTTPException as e:
            return e
