##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
import logging

LOGGER = logging.getLogger("PYWPS")

import logging
import time
from werkzeug.wrappers import Request
from pywps import get_ElementMakerForVersion
from pywps.app.basic import get_response_type, get_json_indent, get_default_response_mimetype
import pywps.configuration as config
from werkzeug.wrappers import Response
from pywps.dblog import store_status, update_status_record
from pywps.inout.array_encode import ArrayEncoder
from pywps.response.status import WPS_STATUS
from pywps.inout.formats import FORMATS
from pywps.inout.outputs import ComplexOutput
from pywps.response.execute import StatusResponse
from pywps.exceptions import (StorageNotSupported, OperationNotSupported,
                              ServerBusy, NoApplicableCode,
                              InvalidParameterValue)

import urllib.parse as urlparse
from urllib.parse import urlencode

LOGGER = logging.getLogger("PYWPS")

WPS, OWS = get_ElementMakerForVersion("1.0.0")


# WPSExecuteResponse is crafted as an interface for the user. The user can
# provide outputs within Process._handler using
# WPSExecuteResponse.outputs['identifier']. The structure also provide output
# metadata such as the requested mimetype for ComplexOutput
#
# This structure is not expect to be serialized. The json property is used as
# input for the execute template and should stay like this.
class WPSExecuteResponse(object):

    def __init__(self, process, wps_request, uuid, **kwargs):
        """constructor

        :param pywps.app.WPSRequest.WPSRequest wps_request:
        :param pywps.app.Process.Process process:
        :param uuid: string this request uuid
        """
        self.uuid = uuid
        self.wps_request = wps_request
        self.process = process
        self.outputs = {o.identifier: o for o in self.process.outputs}
        self.store_status_file = False

        self.setup_outputs_from_wps_request(process, wps_request)

    def setup_outputs_from_wps_request(self, process, wps_request):
        # set as_reference to True for all the outputs specified as reference
        # if the output is not required to be raw
        if not wps_request.raw:
            for wps_outpt in wps_request.outputs:

                is_reference = wps_request.outputs[wps_outpt].get('asReference', 'false')
                mimetype = wps_request.outputs[wps_outpt].get('mimetype', '')
                if not isinstance(mimetype, str):
                    mimetype = ''

                if is_reference.lower() == 'true':
                    if process.store_supported == 'false':
                        raise StorageNotSupported(
                            'The storage of data is not supported for this process.')

                    is_reference = True
                else:
                    is_reference = False

                for outpt in self.outputs.values():
                    if outpt.identifier == wps_outpt:
                        outpt.as_reference = is_reference
                        if isinstance(outpt, ComplexOutput) and mimetype:
                            data_format = [f for f in outpt.supported_formats if f.mime_type == mimetype]
                            if len(data_format) == 0:
                                raise InvalidParameterValue(
                                    f"MimeType {mimetype} not valid")
                            outpt.data_format = data_format[0]

    def _update_stored_status(self, status, message, status_percentage):
        """
        Update status report of currently running process instance

        :param str message: Message you need to share with the client
        :param int status_percentage: Percent done (number betwen <0-100>)
        :param pywps.response.status.WPS_STATUS status: process status - user should usually
            ommit this parameter
        """
        self.message = message
        self.status = status
        self.status_percentage = status_percentage
        store_status(self.uuid, self.status, self.message, self.status_percentage)

    # override WPSResponse._update_status
    def _update_status(self, status, message, status_percentage, clean=True):
        """
        Updates status report of currently running process instance:

        * Updates the status document.
        * Updates the status file (if requested).
        * Cleans the working directory when process has finished.

        This method is *only* called by pywps internally.
        """
        self._update_stored_status(status, message, status_percentage)
        update_status_record(self.uuid, self.as_json_for_execute_template())

        if self.status == WPS_STATUS.SUCCEEDED and \
                getattr(self.wps_request, 'preprocess_response', None):
            self.outputs = self.wps_request.preprocess_response(self.outputs,
                                                                request=self.wps_request,
                                                                http_request=self.wps_request.http_request)
            # Avoid multiple apply of preprocess_response
            self.wps_request.preprocess_response = None

        LOGGER.debug("_update_status: status={}, clean={}".format(status, clean))
        self._update_status_doc()
        if self.store_status_file:
            self._update_status_file()
        if clean:
            if self.status == WPS_STATUS.SUCCEEDED or self.status == WPS_STATUS.FAILED:
                LOGGER.debug("clean workdir: status={}".format(status))
                self.process.clean()

    def update_status(self, message, status_percentage=None):
        """
        Update status report of currently running process instance.

        This method is *only* called by the user provided process.
        The status is handled internally in pywps.

        :param str message: Message you need to share with the client
        :param int status_percentage: Percent done (number betwen <0-100>)
        """
        if status_percentage is None:
            status_percentage = self.status_percentage
        self._update_status(self.status, message, status_percentage, False)

    def _update_status_doc(self):
        try:
            # rebuild the doc
            self.doc = StatusResponse(self.wps_request.version, self.uuid,
                                      get_default_response_mimetype()).get_data(as_text=True)
            self.content_type = get_default_response_mimetype()
        except Exception as e:
            raise NoApplicableCode('Building Response Document failed with : {}'.format(e))

    def _update_status_file(self):
        # TODO: check if file/directory is still present, maybe deleted in mean time
        try:
            # update the status xml file
            self.process.status_store.write(
                self.doc,
                self.process.status_filename,
                data_format=FORMATS.XML)
        except Exception as e:
            raise NoApplicableCode('Writing Response Document failed with : {}'.format(e))

    def _process_accepted(self):
        percent = int(self.status_percentage)
        if percent > 99:
            percent = 99
        return {
            "status": "accepted",
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime()),
            "percent_done": str(percent),
            "message": self.message
        }

    def _process_started(self):
        data = self._process_accepted()
        data.update({
            "status": "started",
        })
        return data

    def _process_paused(self):
        data = self._process_accepted()
        data.update({
            "status": "paused",
        })
        return data

    def _process_succeeded(self):
        data = self._process_accepted()
        data.update({
            "status": "succeeded",
            "percent_done": "100"
        })
        return data

    def _process_failed(self):
        data = self._process_accepted()
        data.update({
            "status": "failed",
            "code": "NoApplicableCode",
            "locator": "None",
        })
        return data

    def _get_serviceinstance(self):

        url = config.get_config_value("server", "url")
        params = {'request': 'GetCapabilities', 'service': 'WPS'}

        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)

        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts).replace("&", "&amp;")

    # Kept as guard to avoid misleading implementation
    @property
    def json(self):
        raise NotImplementedError("Use WPSExecuteResponse.as_json_for_execute_template instead")

    # Used only to render the status outputs.
    def as_json_for_execute_template(self):
        data = {
            "language": self.wps_request.language,
            "service_instance": self._get_serviceinstance(),
            "process": self.process.json
        }

        if self.store_status_file:
            if self.process.status_location:
                data["status_location"] = self.process.status_url

        if self.status == WPS_STATUS.ACCEPTED:
            self.message = 'PyWPS Process {} accepted'.format(self.process.identifier)
            data["status"] = self._process_accepted()
        elif self.status == WPS_STATUS.STARTED:
            data["status"] = self._process_started()
        elif self.status == WPS_STATUS.FAILED:
            # check if process failed and display fail message
            data["status"] = self._process_failed()
        elif self.status == WPS_STATUS.PAUSED:
            # TODO: handle paused status
            data["status"] = self._process_paused()
        elif self.status == WPS_STATUS.SUCCEEDED:
            data["status"] = self._process_succeeded()
            # Process outputs XML
            data["outputs"] = [self.outputs[o].json for o in self.outputs]
        # lineage: add optional lineage when process has finished
        if self.status in [WPS_STATUS.SUCCEEDED, WPS_STATUS.FAILED]:
            # DataInputs and DataOutputs definition XML if lineage=true
            if self.wps_request.lineage == 'true':
                data["lineage"] = True
                try:
                    # TODO: stored process has ``pywps.inout.basic.LiteralInput``
                    # instead of a ``pywps.inout.inputs.LiteralInput``.
                    data["input_definitions"] = [self.wps_request.inputs[i][0].json for i in self.wps_request.inputs]
                except Exception as e:
                    LOGGER.error("Failed to update lineage for input parameter. {}".format(e))

                data["output_definitions"] = [self.outputs[o].json for o in self.outputs]
        return data
