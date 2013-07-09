"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import BadRequest, MethodNotAllowed
from werkzeug.datastructures import MultiDict
import lxml.etree
from lxml.builder import ElementMaker
from pywps._compat import text_type


NAMESPACES = {
  'wps': "http://www.opengis.net/wps/1.0.0",
  'ows': "http://www.opengis.net/ows/1.1",
}

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
        [value_el] = xpath_ns(input_el, './wps:Data/wps:LiteralData')
        the_input.update({identifier_el.text: text_type(value_el.text)})
    return the_input


class WPSRequest:

    def __init__(self, http_request):
        self.http_request = http_request
        if http_request.method == 'POST':
            doc = lxml.etree.fromstring(http_request.get_data())
            self.inputs = get_input_from_xml(doc)


class WPSResponse:

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


class Process:
    """ WPS process """

    def __init__(self, handler, identifier=None):
        self.identifier = identifier or handler.__name__
        self.handler = handler

    def capabilities_xml(self):
        return WPS.Process(OWS.Identifier(self.identifier))

    def execute(self, http_request):
        return self.handler(WPSRequest(http_request))


class Service:
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

    def execute(self, identifier, request):
        try:
            process = self.processes[identifier]
        except KeyError:
            return BadRequest("Unknown process %r" % identifier)
        return process.execute(request)

    @Request.application
    def __call__(self, request):
        if request.method == 'GET':
            request_type = request.args['Request']

            if request_type == 'GetCapabilities':
                return self.get_capabilities()

            elif request_type == 'Execute':
                identifier = request.args['identifier']
                return self.execute(identifier, request)

            else:
                return BadRequest("Unknown request type %r" % request_type)

        elif request.method == 'POST':
            doc = lxml.etree.fromstring(request.get_data())
            if doc.tag == WPS.GetCapabilities().tag:
                return self.get_capabilities()

            elif doc.tag == WPS.Execute().tag:
                identifier = doc.xpath('/wps:Execute/ows:Identifier',
                                       namespaces=NAMESPACES)[0].text
                return self.execute(identifier, request)

            else:
                return BadRequest("Unknown request type %r" % doc.tag)

        else:
            return MethodNotAllowed()
