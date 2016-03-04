import logging
import lxml
from werkzeug.wrappers import Response
from pywps import __version__, OWS, NAMESPACES, OGCUNIT

LOGGER = logging.getLogger(__name__)

def xpath_ns(el, path):
    return el.xpath(path, namespaces=NAMESPACES)


def xml_response(doc):
    """XML response serializer"""

    LOGGER.debug('Serializing XML response')
    pywps_version_comment = '<!-- PyWPS %s -->\n' % __version__
    xml = lxml.etree.tostring(doc, pretty_print=True)
    response = Response(pywps_version_comment.encode('utf8') + xml,
                        content_type='text/xml')
    response.status_percentage = 100;
    return response
