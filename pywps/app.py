"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""

from werkzeug.wrappers import Request, Response
import lxml.etree
from lxml.builder import ElementMaker


NAMESPACES = {
  'wps': "http://www.opengis.net/wps/1.0.0",
  'ows': "http://www.opengis.net/ows/1.1",
}

WPS = ElementMaker(namespace=NAMESPACES['wps'], nsmap=NAMESPACES)
OWS = ElementMaker(namespace=NAMESPACES['ows'], nsmap=NAMESPACES)


def xml_response(doc):
    return Response(lxml.etree.tostring(doc, pretty_print=True),
                    content_type='text/xml')


class WPSRequest:

    def __init__(self, http_request):
        self.http_request = http_request


class WPSResponse:

    def __init__(self, outputs=None):
        self.outputs = outputs or {}

    @Request.application
    def __call__(self, request):
        output_elements = []
        for key, value in self.outputs.items():
            output_elements.append(WPS.Output(
                OWS.Identifier(key),
                OWS.Data(WPS.LiteralData(value))
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

    @Request.application
    def __call__(self, http_request):
        return self.handler(WPSRequest(http_request))


class Service:
    """ WPS service """

    def __init__(self, processes=[]):
        self.processes = list(processes)

    def get_capabilities(self):
        process_elements = [p.capabilities_xml() for p in self.processes]

        doc = WPS.Capabilities(
            OWS.ServiceIdentification(
                OWS.Title('PyWPS Server')
            ),
            WPS.ProcessOfferings(*process_elements)
        )

        return xml_response(doc)

    def execute(self, identifier, request):
        for process in self.processes:
            if process.identifier == identifier:
                return Response.from_app(process, request.environ)

    @Request.application
    def __call__(self, request):
        if request.method == 'GET':
            request_type = request.args['Request']

            if request_type == 'GetCapabilities':
                return self.get_capabilities()

            elif request_type == 'Execute':
                identifier = request.args['identifier']
                return self.execute(identifier, request)

        elif request.method == 'POST':
            doc = lxml.etree.fromstring(request.get_data())
            if doc.tag == WPS.Execute().tag:
                identifier = doc.xpath('/wps:Execute/ows:Identifier',
                                       namespaces=NAMESPACES)[0].text
                return self.execute(identifier, request)
