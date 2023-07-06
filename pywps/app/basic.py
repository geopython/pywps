##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
"""
XML tools
"""

import logging
from typing import Tuple

from werkzeug.wrappers import Response

import pywps.configuration as config

LOGGER = logging.getLogger('PYWPS')


def get_xpath_ns(version):
    """Get xpath namespace for specified WPS version.

    Versions 1.0.0 or 2.0.0 are supported.
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
        else:
            raise NotImplementedError(version)
        return ele.xpath(path, namespaces=nsp)

    return xpath_ns


def make_response(doc, content_type):
    """Response serializer."""
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


def get_response_type(accept_mimetypes, default_mimetype) -> Tuple[bool, str]:
    """
    This function determinate if the response should be JSON or XML based on
    the accepted mimetypes of the request and the default mimetype provided,
    which will be used in case both are equally accepted.

    :param accept_mimetypes: determinate which mimetypes are accepted
    :param default_mimetype: "text/xml", "application/json"
    :return: Tuple[bool, str] -
        bool - True: The response type is JSON, False: Otherwise - XML
        str - The output mimetype
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
    return json_response, mimetype


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
    operation = api = identifier = output_ids = default_mimetype = base_url = None
    if http_request:
        parts = str(http_request.path[1:]).split('/')
        i = 0
        if len(parts) > i:
            base_url = parts[i].lower()
            if base_url == 'wps':
                default_mimetype = 'xml'
            elif base_url in ['api', 'processes', 'jobs']:
                default_mimetype = 'json'
            i += 1
            if base_url == 'api':
                api = parts[i]
                i += 1
            if len(parts) > i:
                identifier = parts[i]
                i += 1
                if len(parts) > i:
                    output_ids = parts[i]
                    if not output_ids:
                        output_ids = None
    if base_url in ['jobs', 'api']:
        operation = 'execute'
    elif base_url == 'processes':
        operation = 'describeprocess' if identifier else 'getcapabilities'
    d = {}
    if operation:
        d['operation'] = operation
    if identifier:
        d['identifier'] = identifier
    if output_ids:
        d['output_ids'] = output_ids
    if default_mimetype:
        d['default_mimetype'] = default_mimetype
    if api:
        d['api'] = api
    if base_url:
        d['base_url'] = base_url
    return d
