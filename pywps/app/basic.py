##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
"""
XML tools
"""

import logging
from werkzeug.wrappers import Response
import pywps.configuration as config

LOGGER = logging.getLogger('PYWPS')


def get_xpath_ns(version):
    """Get xpath namespace for specified WPS version
    currently 1.0.0 or 2.0.0 are supported
    """

    def xpath_ns(ele, path):
        """Function, which will return xpath namespace for given
        element and xpath
        """
        if version == "1.0.0":
            from pywps import namespaces100
            nsp = namespaces100
        elif version == "2.0.0":
            from pywps import namespaces200
            nsp = namespaces200
        return ele.xpath(path, namespaces=nsp)

    return xpath_ns


def make_response(doc, content_type):
    """response serializer"""
    if not content_type:
        content_type = get_default_response_mimetype()
    response = Response(doc, content_type=content_type)
    response.status_percentage = 100
    return response


def get_default_response_mimetype():
    default_mimetype = config.get_config_value('server', 'default_mimetype')
    if not default_mimetype:
        default_mimetype = 'text/xml'
        # default_mimetype = 'application/json'
    return default_mimetype


def get_json_indent():
    json_ident = int(config.get_config_value('server', 'json_indent', 2))
    return json_ident if json_ident >= 0 else None


def get_response_type(accept_mimetypes):
    json_is_default = 'json' in get_default_response_mimetype()
    json_response = (
            (accept_mimetypes.accept_json and (not accept_mimetypes.accept_xhtml or json_is_default)) or
            (json_is_default and accept_mimetypes.accept_json == accept_mimetypes.accept_xhtml)
    )
    content_type = 'application/json' if json_response else 'text/xml'
    return json_response, content_type
