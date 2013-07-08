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


class Service:
    """ WPS service """

    @Request.application
    def __call__(self, request):
        doc = WPS.Capabilities(
            OWS.ServiceIdentification(
                OWS.Title('PyWPS Server')
            )
        )
        return Response(lxml.etree.tostring(doc, pretty_print=True))


def create_service():
    return Service()
