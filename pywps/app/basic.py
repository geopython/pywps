##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
"""
XML tools
"""

import re
import logging
from typing import Optional, Tuple

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
    return default_mimetype


def get_json_indent():
    json_ident = int(config.get_config_value('server', 'json_indent'))
    return json_ident if json_ident >= 0 else None


def select_response_mimetype(accept_mimetypes, default_mimetype) -> str:
    """
    This function determinate if the response should be JSON or XML based on
    the accepted mimetypes of the request and the default mimetype provided,
    which will be used in case both are equally accepted.

    :param accept_mimetypes: determinate which mimetypes are accepted
    :param default_mimetype: "text/xml", "application/json"
    :return: The selected mimetype
    """
    accept_json = \
        accept_mimetypes.accept_json or \
        accept_mimetypes.best is None or \
        'json' in accept_mimetypes.best.lower()
    accept_xhtml = \
        accept_mimetypes.accept_xhtml or \
        accept_mimetypes.best is None or \
        'xml' in accept_mimetypes.best.lower()
    if not default_mimetype:
        default_mimetype = get_default_response_mimetype()
    json_is_default = 'json' in default_mimetype or '*' in default_mimetype
    json_response = (accept_json and (not accept_xhtml or json_is_default)) or \
                    (json_is_default and accept_json == accept_xhtml)
    mimetype = 'application/json' if json_response else 'text/xml' if accept_xhtml else ''
    return mimetype


def parse_http_url(http_request) -> dict:
    """
    This function parses the request URL and extracts the following:
        default operation, process identifier, output_ids, default mimetype
        info that cannot be terminated from the URL will be None (default)

        The url is expected to be in the following format, all the levels are optional.
        [base_url]/[identifier]/[output_ids]

    :param http_request: the request URL
    :return: dict with the extracted info listed:
        base_url - [wps|processes|jobs|api/api_level]
        default_mimetype - determinate by the base_url part:
            XML - if the base url == 'wps',
            JSON - if the base URL in ['api'|'jobs'|'processes']
        operation - also determinate by the base_url part:
            ['api'|'jobs'] -> 'execute'
            processes -> 'describeprocess' or 'getcapabilities'
                'describeprocess' if identifier is present as the next item, 'getcapabilities' otherwise
        api - api level, only expected if base_url=='api'
        identifier - the process identifier
        output_ids - if exist then it selects raw output with the name output_ids
    """

    d = {}

    if http_request is None:
        return d

    p = re.compile("^/(wps|api|processes|jobs)(/.+)?$")
    m = p.match(http_request.path)

    if m is None:
        return d

    base_url = m.group(1)
    if m.group(2) is not None:
        args = re.findall("/([^/]+)", m.groups(2))
    else:
        args = []

    d['base_url'] = base_url

    if base_url == 'wps':
        d['default_mimetype'] = 'application/xml'
        return d

    if base_url == 'api':
        d['operation'] = 'execute'
        d['default_mimetype'] = 'application/json'
        d.update(dict(zip(['api', 'identifier', 'output_ids'], args)))
        return d

    if base_url == 'jobs':
        d['operation'] = 'execute'
        d['default_mimetype'] = 'application/json'
        d.update(dict(zip(['identifier', 'output_ids'], args)))
        return d

    if base_url == 'processes':
        d['operation'] = 'describeprocess' if len(args) == 0 else 'getcapabilities'
        d['default_mimetype'] = 'json'
        d.update(dict(zip(['identifier', 'output_ids'], args)))
        return d

    return dict()
