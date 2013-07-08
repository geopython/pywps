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


class Process:
    """ WPS process """

    def __init__(self, handler, identifier=None):
        self.identifier = identifier or handler.__name__
        self.handler = handler

    def capabilities_xml(self):
        return WPS.Process(OWS.Identifier(self.identifier))


class Service:
    """ WPS service """

    def __init__(self, processes=[]):
        self.processes = list(processes)

    @Request.application
    def __call__(self, request):
        process_elements = [p.capabilities_xml() for p in self.processes]

        doc = WPS.Capabilities(
            OWS.ServiceIdentification(
                OWS.Title('PyWPS Server')
            ),
            WPS.ProcessOfferings(*process_elements)
        )

        return Response(lxml.etree.tostring(doc, pretty_print=True))
