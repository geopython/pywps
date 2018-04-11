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
from pywps.dblog import update_response

from pywps.response.status import STATUS
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

    def update_status(self, message=None, status_percentage=None, status=None,
                      clean=True):
        """
        Update status report of currently running process instance

        :param str message: Message you need to share with the client
        :param int status_percentage: Percent done (number betwen <0-100>)
        :param pywps.app.WPSResponse.STATUS status: process status - user should usually
            ommit this parameter
        """

        if message:
            self.message = message

        if status is not None:
            self.status = status

        if status_percentage is not None:
            self.status_percentage = status_percentage

        # check if storing of the status is requested
        if self.status >= STATUS.STORE_AND_UPDATE_STATUS:
            # rebuild the doc and update the status xml file
            self.doc = self._construct_doc()
            self.write_response_doc(clean)

        update_response(self.uuid, self)

    def write_response_doc(self, clean=True):
        # TODO: check if file/directory is still present, maybe deleted in mean time

        # check if storing of the status is requested
        if self.status >= STATUS.STORE_AND_UPDATE_STATUS:

            # rebuild the doc and update the status xml file
            self.doc = self._construct_doc()

            try:
                with open(self.process.status_location, 'w') as f:
                    f.write(self.doc)
                    f.flush()
                    os.fsync(f.fileno())

                if self.status >= STATUS.DONE_STATUS and clean:
                    self.process.clean()

            except IOError as e:
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

        if self.status >= STATUS.STORE_STATUS:
            if self.process.status_location:
                data["status_location"] = self.process.status_url

        if self.status == STATUS.STORE_AND_UPDATE_STATUS:
            if self.status_percentage == 0:
                self.message = 'PyWPS Process %s accepted' % self.process.identifier
                data["status"] = self._process_accepted()
                return data
            elif self.status_percentage > 0:
                data["percent_done"] = self.status_percentage
                data["status"] = self._process_started()
                return data

        # check if process failed and display fail message
        if self.status_percentage == -1:
            data["status"] = self._process_failed()
            return data

        # TODO: add paused status

        if self.status == STATUS.DONE_STATUS:
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

        template = self.template_env.get_template(os.path.join(self.version, 'execute', 'main.xml'))

        doc = template.render(**self.json)

        return doc

    @Request.application
    def __call__(self, request):
        doc = None
        try:
            doc = self._construct_doc()
        except HTTPException as httpexp:
            raise httpexp
        except Exception as exp:
            raise NoApplicableCode(exp)

        if self.status >= STATUS.DONE_STATUS:
            self.process.clean()

        return xml_response(doc)
