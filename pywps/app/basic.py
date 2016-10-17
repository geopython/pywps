##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


import logging
import lxml
from werkzeug.wrappers import Response
from pywps import __version__, NAMESPACES

LOGGER = logging.getLogger('PYWPS')


def xpath_ns(el, path):
    return el.xpath(path, namespaces=NAMESPACES)


def xml_response(doc):
    """XML response serializer"""

    LOGGER.debug('Serializing XML response')
    pywps_version_comment = '<!-- PyWPS %s -->\n' % __version__
    xml = lxml.etree.tostring(doc, pretty_print=True)
    response = Response(pywps_version_comment.encode('utf8') + xml,
                        content_type='text/xml')
    response.status_percentage = 100
    return response
