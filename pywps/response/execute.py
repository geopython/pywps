##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import json
import logging
import time
import urllib.parse as urlparse
from urllib.parse import urlencode

from werkzeug.wrappers import Request, Response

import pywps.configuration as config
from pywps import get_ElementMakerForVersion
from pywps.app.basic import (
    get_default_response_mimetype,
    get_json_indent,
    get_response_type,
)
from pywps.exceptions import NoApplicableCode
from pywps.inout.array_encode import ArrayEncoder
from pywps.inout.formats import FORMATS
from pywps.response.status import WPS_STATUS

from .basic import WPSResponse

LOGGER = logging.getLogger("PYWPS")

WPS, OWS = get_ElementMakerForVersion("1.0.0")


class ExecuteRawResponse(WPSResponse):

    def __init__(self, wps_execute_response):
        """constructor

        :param pywps.app.WPSRequest.WPSRequest wps_request:
        :param pywps.app.Process.Process process:
        :param uuid: string this request uuid
        """

        super(ExecuteRawResponse, self).__init__(wps_execute_response.wps_request, wps_execute_response.uuid)

        self.wps_execute_response = wps_execute_response

    # Fallback to self.wps_execute_response attribute
    def __getattr__(self, item):
        return getattr(self.wps_execute_response, item)

    @Request.application
    def __call__(self, request):
        accept_json_response, accepted_mimetype = get_response_type(
            self.wps_request.http_request.accept_mimetypes, self.wps_request.default_mimetype)
        if self.status == WPS_STATUS.FAILED:
            return NoApplicableCode(self.message)
        else:
            wps_output_identifier = next(iter(self.wps_request.outputs))  # get the first key only
            wps_output_value = self.outputs[wps_output_identifier]
            response = wps_output_value.data
            if response is None:
                return NoApplicableCode("Expected output was not generated")
            suffix = ''
            # if isinstance(wps_output_value, ComplexOutput):
            data_format = None
            if hasattr(wps_output_value, 'output_format'):
                # this is set in the response, thus should be more precise
                data_format = wps_output_value.output_format
            elif hasattr(wps_output_value, 'data_format'):
                # this is set in the process' response _handler function, thus could have a few supported formats
                data_format = wps_output_value.data_format
            if data_format is not None:
                mimetype = data_format.mime_type
                if data_format.extension is not None:
                    suffix = data_format.extension
            else:
                # like LitearlOutput
                mimetype = self.wps_request.outputs[wps_output_identifier].get('mimetype', None)
            if not isinstance(response, (str, bytes, bytearray)):
                if not mimetype:
                    mimetype = accepted_mimetype
                json_response = mimetype and 'json' in mimetype
                if json_response:
                    mimetype = 'application/json'
                    suffix = '.json'
                    response = json.dumps(response, cls=ArrayEncoder, indent=get_json_indent())
                else:
                    response = str(response)
            if not mimetype:
                mimetype = None
            return Response(response, mimetype=mimetype,
                            headers={'Content-Disposition': 'attachment; filename="{}"'
                                     .format(wps_output_identifier + suffix)})


class ExecuteResponse(WPSResponse):

    def __init__(self, wps_execute_response):
        """constructor

        :param pywps.app.WPSRequest.WPSRequest wps_request:
        :param pywps.app.Process.Process process:
        :param uuid: string this request uuid
        """

        super(ExecuteResponse, self).__init__(wps_execute_response.wps_request, wps_execute_response.uuid)

        self.wps_execute_response = wps_execute_response

    # Fallback to self.wps_execute_response attribute
    def __getattr__(self, item):
        return getattr(self.wps_execute_response, item)

    @staticmethod
    def _render_json_response(jdoc):
        response = dict()
        response['status'] = jdoc['status']
        out = jdoc['process']['outputs']
        d = {}
        for val in out:
            id = val.get('identifier')
            if id is None:
                continue
            type = val.get('type')
            key = 'bbox' if type == 'bbox' else 'data'
            if key in val:
                d[id] = val[key]
        response['outputs'] = d
        return response

    def _construct_doc(self):
        doc = self.wps_execute_response.as_json_for_execute_template()
        try:
            json_response, mimetype = get_response_type(
                self.wps_request.http_request.accept_mimetypes, self.wps_request.default_mimetype)
        except Exception:
            mimetype = get_default_response_mimetype()
            json_response = 'json' in mimetype
        if json_response:
            doc = json.dumps(self._render_json_response(doc), cls=ArrayEncoder, indent=get_json_indent())
        else:
            template = self.template_env.get_template(self.version + '/execute/main.xml')
            doc = template.render(**doc)
        return doc, mimetype

    @Request.application
    def __call__(self, request):
        accept_json_response, accepted_mimetype = get_response_type(
            self.wps_request.http_request.accept_mimetypes, self.wps_request.default_mimetype)
        doc, mimetypes = self._construct_doc()
        if not doc:
            return NoApplicableCode("Output was not generated")
        return Response(doc, mimetype=accepted_mimetype)
