##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
import os
from lxml import etree
import time
from werkzeug.wrappers import Request
from werkzeug.exceptions import HTTPException
from pywps import get_ElementMakerForVersion
from pywps.app.basic import xml_response
from pywps.exceptions import NoApplicableCode
import pywps.configuration as config
from werkzeug.wrappers import Response

from pywps.response.status import WPS_STATUS
from pywps.response import WPSResponse

from pywps._compat import PY2

if PY2:
    import urlparse
    from urllib import urlencode
else:
    import urllib.parse as urlparse
    from urllib.parse import urlencode

LOGGER = logging.getLogger("PYWPS")

WPS, OWS = get_ElementMakerForVersion("1.0.0")


class ExecuteResponse(WPSResponse):

    def __init__(self, wps_request, uuid, **kwargs):
        """constructor

        :param pywps.app.WPSRequest.WPSRequest wps_request:
        :param pywps.app.Process.Process process:
        :param uuid: string this request uuid
        """

        super(self.__class__, self).__init__(wps_request, uuid)

        self.process = kwargs["process"]
        self.outputs = {o.identifier: o for o in self.process.outputs}
        self.store_status_file = False

    # override WPSResponse._update_status
    def _update_status(self, status, message, status_percentage, clean=True):
        super(ExecuteResponse, self)._update_status(status, message, status_percentage)
        if self.store_status_file:
            self.update_status_file(clean)

    def update_status(self, message, status_percentage=None):
        """
        Update status report of currently running process instance

        :param str message: Message you need to share with the client
        :param int status_percentage: Percent done (number betwen <0-100>)
        """
        if status_percentage is None:
            status_percentage = self.status_percentage
        self._update_status(WPS_STATUS.ACCEPTED, message, status_percentage)

    def update_status_file(self, clean):
        # TODO: check if file/directory is still present, maybe deleted in mean time
        try:
            # rebuild the doc and update the status xml file
            self.doc = self._construct_doc()

            with open(self.process.status_location, 'w') as f:
                f.write(self.doc)
                f.flush()
                os.fsync(f.fileno())

            if (self.status == WPS_STATUS.SUCCEEDED or self.status == WPS_STATUS.FAILED) and clean:
                self.process.clean()

        except Exception as e:
            raise NoApplicableCode('Writing Response Document failed with : %s' % e)

    def _process_accepted(self):
        return {
            "status": "accepted",
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime()),
            "message": self.message
        }

    def _process_started(self):
        percent = int(self.status_percentage)
        if percent > 99:
            percent = 99
        return {
            "status": "started",
            "message": self.message,
            "percent_done": str(percent),
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        }

    def _process_paused(self):
        return {
            "status": "paused",
            "message": self.message,
            "percent_done": str(self.status_percentage),
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        }

    def _process_succeeded(self):
        return {
            "status": "succeeded",
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime()),
            "percent_done": str(self.status_percentage),
            "message": self.message
        }

    def _process_failed(self):
        return {
            "status": "failed",
            "code": "NoApplicableCode",
            "locator": "None",
            "message": self.message,
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        }

    def _get_serviceinstance(self):

        url = config.get_config_value("server", "url")
        params = {'request': 'GetCapabilities', 'service': 'WPS'}

        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)

        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts).replace("&", "&amp;")

    @property
    def json(self):
        data = {}
        data["lang"] = "en-US"
        data["service_instance"] = self._get_serviceinstance()
        data["process"] = self.process.json

        if self.store_status_file:
            if self.process.status_location:
                data["status_location"] = self.process.status_url

        if self.status == WPS_STATUS.ACCEPTED:
            self.message = 'PyWPS Process %s accepted' % self.process.identifier
            data["status"] = self._process_accepted()
            return data

        if self.status == WPS_STATUS.STARTED:
            data["percent_done"] = self.status_percentage
            data["status"] = self._process_started()
            return data

        # check if process failed and display fail message
        if self.status == WPS_STATUS.FAILED:
            data["status"] = self._process_failed()
            return data

        # TODO: add paused status

        if self.status == WPS_STATUS.SUCCEEDED:
            data["status"] = self._process_succeeded()

            # DataInputs and DataOutputs definition XML if lineage=true
            if self.wps_request.lineage == 'true':
                data["lineage"] = True
                try:
                    # TODO: stored process has ``pywps.inout.basic.LiteralInput``
                    # instead of a ``pywps.inout.inputs.LiteralInput``.
                    data["input_definitions"] = [self.wps_request.inputs[i][0].json for i in self.wps_request.inputs]
                except Exception as e:
                    LOGGER.error("Failed to update lineage for input parameter. %s", e)

                data["output_definitions"] = [self.outputs[o].json for o in self.outputs]

            # Process outputs XML
            data["outputs"] = [self.outputs[o].json for o in self.outputs]
        return data

    def _construct_doc(self):
        template = self.template_env.get_template(self.version + '/execute/main.xml')
        doc = template.render(**self.json)
        return doc

    @Request.application
    def __call__(self, request):
        if self.wps_request.raw:
            if self.status == WPS_STATUS.FAILED:
                return NoApplicableCode(self.message)
            else:
                wps_output_identifier = next(iter(self.wps_request.outputs))  # get the first key only
                wps_output_value = self.outputs[wps_output_identifier]
                if wps_output_value.source_type is None:
                    return NoApplicableCode("Expected output was not generated")
                return Response(wps_output_value.data,
                                mimetype=self.wps_request.outputs[wps_output_identifier]['mimetype'])
        else:
            doc = None
            try:
                doc = self._construct_doc()
                if self.store_status_file:
                    self.process.clean()
            # TODO: If an exception occur here we must generate a valid status file
            except HTTPException as httpexp:
                return httpexp
            except Exception as exp:
                return NoApplicableCode(exp)

            return Response(doc, mimetype='text/xml')
