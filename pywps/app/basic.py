import lxml
from werkzeug.wrappers import Response
from pywps import OWS, NAMESPACES, OGCUNIT


def xpath_ns(el, path):
    return el.xpath(path, namespaces=NAMESPACES)


def xml_response(doc):
    return Response(lxml.etree.tostring(doc, pretty_print=True),
                    content_type='text/xml')
