import os
from lxml import etree
import time
from werkzeug.wrappers import Request
from pywps import WPS, OWS
from pywps.app.basic import xml_response
from pywps.exceptions import NoApplicableCode
import pywps.configuration as config
from pywps.dblog import update_response


class WPSResponse(object):

    NO_STATUS = 0
    STORE_STATUS = 1
    STORE_AND_UPDATE_STATUS = 2

    def __init__(self, process, wps_request, uuid):
        """constructor

        :param process: instance of  class:`pywps.app.Process.Process`
        :param wps_request: instance of class:`pywps.app.WPSRequest.WPSRequest`
        :param uuid: string this request uuid
        """

        self.process = process
        self.wps_request = wps_request
        self.outputs = {o.identifier: o for o in process.outputs}
        self.message = ''
        self.status = self.NO_STATUS
        self.status_percentage = 0
        self.doc = None
        self.uuid = uuid

    def update_status(self, message, status_percentage=None):
        self.message = message
        if status_percentage:
            self.status_percentage = status_percentage

            # rebuild the doc and update the status xml file
            self.doc = self._construct_doc()

        # check if storing of the status is requested
        if self.status >= self.STORE_STATUS:
            self.write_response_doc(self.doc)

        update_response(self.uuid, self)

    def write_response_doc(self, doc):
        # TODO: check if file/directory is still present, maybe deleted in mean time
        try:
            with open(self.process.status_location, 'w') as f:
                f.write(etree.tostring(doc, pretty_print=True, encoding='utf-8').decode('utf-8'))
                f.flush()
                os.fsync(f.fileno())
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
                        OWS.Exception(self.message),
                        exceptionCode='NoApplicableCode',
                        locater='None'
                    )
                )
            ),
            creationTime=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        )

    def _construct_doc(self):
        doc = WPS.ExecuteResponse()
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = 'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'
        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-US'
        doc.attrib['serviceInstance'] = '%s%s' % (
            config.get_config_value('server', 'url'),
            '/wps?service=wps&request=getcapabilities'
        )

        if self.status >= self.STORE_STATUS:
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
        #for m in self.process.metadata:
        #    process_doc.append(OWS.Metadata(m))
        if self.process.profile:
            process_doc.append(OWS.Profile(self.process.profile))
        if self.process.wsdl:
            process_doc.append(OWS.WSDL(self.process.wsdl))
        process_doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = self.process.version

        doc.append(process_doc)

        # Status XML
        # return the correct response depending on the progress of the process
        if self.status >= self.STORE_AND_UPDATE_STATUS:
            if self.status_percentage == 0:
                self.message = 'PyWPS Process %s accepted' % self.process.identifier
                status_doc = self._process_accepted()
                doc.append(status_doc)
                self.write_response_doc(doc)
                return doc
            elif 0 < self.status_percentage < 100:
                status_doc = self._process_started()
                doc.append(status_doc)
                return doc

        # check if process failed and display fail message
        if self.status_percentage == -1:
            status_doc = self._process_failed()
            doc.append(status_doc)
            return doc

        # TODO: add paused status

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

    @Request.application
    def __call__(self, request):
        doc = None
        try:
            doc = self._construct_doc()
        except HTTPException as httpexp:
            raise httpexp
        except Exception as exp:
            raise NoApplicableCode(exp)

        return xml_response(doc)
