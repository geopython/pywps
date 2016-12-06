##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


import os
from lxml import etree
import time
from werkzeug.wrappers import Request
from werkzeug.exceptions import HTTPException
from pywps import WPS, OWS
from pywps.app.basic import xml_response
from pywps.exceptions import NoApplicableCode
import pywps.configuration as config
from pywps.dblog import update_response
from collections import namedtuple

_STATUS = namedtuple('Status', 'ERROR_STATUS, NO_STATUS, STORE_STATUS,'
                     'STORE_AND_UPDATE_STATUS, DONE_STATUS')

STATUS = _STATUS(0, 10, 20, 30, 40)


class WPSResponse(object):

    def __init__(self, process, wps_request, uuid):
        """constructor

        :param pywps.app.Process.Process process:
        :param pywps.app.WPSRequest.WPSRequest wps_request:
        :param uuid: string this request uuid
        """

        self.process = process
        self.wps_request = wps_request
        self.outputs = {o.identifier: o for o in process.outputs}
        self.message = ''
        self.status = STATUS.NO_STATUS
        self.status_percentage = 0
        self.doc = None
        self.uuid = uuid

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

        if status:
            self.status = status

        if status_percentage:
            self.status_percentage = status_percentage

        # check if storing of the status is requested
        if self.status >= STATUS.STORE_AND_UPDATE_STATUS:

            # rebuild the doc and update the status xml file
            self.doc = self._construct_doc()
            self.write_response_doc(self.doc, clean)

        update_response(self.uuid, self)

    def write_response_doc(self, doc, clean=True):
        # TODO: check if file/directory is still present, maybe deleted in mean time

        try:
            with open(self.process.status_location, 'w') as f:
                f.write(etree.tostring(doc, pretty_print=True, encoding='utf-8').decode('utf-8'))
                f.flush()
                os.fsync(f.fileno())

            if self.status >= STATUS.DONE_STATUS and clean:
                self.process.clean()

        except IOError as e:
            raise NoApplicableCode('Writing Response Document failed with : %s' % e)

    def _process_accepted(self):
        return WPS.Status(
            WPS.ProcessAccepted(self.message),
            creationTime=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        )

    def _process_started(self):
        return WPS.Status(
            WPS.ProcessStarted(
                self.message,
                percentCompleted=str(self.status_percentage)
            ),
            creationTime=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        )

    def _process_paused(self):
        return WPS.Status(
            WPS.ProcessPaused(
                self.message,
                percentCompleted=str(self.status_percentage)
            ),
            creationTime=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        )

    def _process_succeeded(self):
        return WPS.Status(
            WPS.ProcessSucceeded(self.message),
            creationTime=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        )

    def _process_failed(self):
        return WPS.Status(
            WPS.ProcessFailed(
                WPS.ExceptionReport(
                    OWS.Exception(
                        OWS.ExceptionText(self.message),
                        exceptionCode='NoApplicableCode',
                        locater='None'
                    )
                )
            ),
            creationTime=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        )

    def _construct_doc(self):
        doc = WPS.ExecuteResponse()
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = \
            'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd'
        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-US'
        doc.attrib['serviceInstance'] = '%s%s' % (
            config.get_config_value('server', 'url'),
            '?service=WPS&request=GetCapabilities'
        )

        if self.status >= STATUS.STORE_STATUS:
            if self.process.status_location:
                doc.attrib['statusLocation'] = self.process.status_url

        # Process XML
        process_doc = WPS.Process(
            OWS.Identifier(self.process.identifier),
            OWS.Title(self.process.title)
        )
        if self.process.abstract:
            process_doc.append(OWS.Abstract(self.process.abstract))
        # TODO: See Table 32 Metadata in OGC 06-121r3
        # for m in self.process.metadata:
        #    process_doc.append(OWS.Metadata(m))
        if self.process.profile:
            process_doc.append(OWS.Profile(self.process.profile))
        process_doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = self.process.version

        doc.append(process_doc)

        # Status XML
        # return the correct response depending on the progress of the process
        if self.status == STATUS.STORE_AND_UPDATE_STATUS:
            if self.status_percentage == 0:
                self.message = 'PyWPS Process %s accepted' % self.process.identifier
                status_doc = self._process_accepted()
                doc.append(status_doc)
                return doc
            elif self.status_percentage > 0:
                status_doc = self._process_started()
                doc.append(status_doc)
                return doc

        # check if process failed and display fail message
        if self.status_percentage == -1:
            status_doc = self._process_failed()
            doc.append(status_doc)
            return doc

        # TODO: add paused status

        if self.status == STATUS.DONE_STATUS:
            status_doc = self._process_succeeded()
            doc.append(status_doc)

            # DataInputs and DataOutputs definition XML if lineage=true
            if self.wps_request.lineage == 'true':
                data_inputs = [self.wps_request.inputs[i][0].execute_xml() for i in self.wps_request.inputs]
                doc.append(WPS.DataInputs(*data_inputs))

                output_definitions = [self.outputs[o].execute_xml_lineage() for o in self.outputs]
                doc.append(WPS.OutputDefinitions(*output_definitions))

            # Process outputs XML
            output_elements = [self.outputs[o].execute_xml() for o in self.outputs]
            doc.append(WPS.ProcessOutputs(*output_elements))
        return doc

    def call_on_close(self, function):
        """Custom implementation of call_on_close of werkzeug
        TODO: rewrite this using werkzeug's tools
        """
        self._close_functions.push(function)

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
