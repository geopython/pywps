###############################################################################
#
# Copyright (C) 2014-2016 PyWPS Development Team, represented by
# PyWPS Project Steering Committee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
###############################################################################

import logging
import os
import sys
import traceback

from pywps import WPS, OWS, E
from pywps.app.WPSResponse import WPSResponse
import pywps.configuration as config
from pywps.exceptions import StorageNotSupported, OperationNotSupported

LOGGER = logging.getLogger(__name__)

class Process(object):
    """
    :param handler: A callable that gets invoked for each incoming
                    request. It should accept a single
                    :class:`~WPSRequest` argument and return a
                    :class:`~WPSResponse` object.
    :param identifier: Name of this process.
    :param inputs: List of inputs accepted by this process. They
                   should be :class:`~LiteralInput` and :class:`~ComplexInput`
                   and :class:`~BoundingBoxInput`
                   objects.
    :param outputs: List of outputs returned by this process. They
                   should be :class:`~LiteralOutput` and :class:`~ComplexOutput`
                   and :class:`~BoundingBoxOutput`
                   objects.
    """

    def __init__(self, handler, identifier, title, abstract='', profile=[], metadata=[], inputs=[],
                 outputs=[], version='None', store_supported=False, status_supported=False):
        self.identifier = identifier
        self.handler = handler
        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.profile = profile
        self.version = version
        self.inputs = inputs
        self.outputs = outputs
        self.uuid = None
        self.status_location = ''
        self.status_url = ''
        self.workdir = None

        if store_supported:
            self.store_supported = 'true'
        else:
            self.store_supported = 'false'

        if status_supported:
            self.status_supported = 'true'
        else:
            self.status_supported = 'false'

    def capabilities_xml(self):
        doc = WPS.Process(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        # TODO: See Table 32 Metadata in OGC 06-121r3
        #for m in self.metadata:
        #    doc.append(OWS.Metadata(m))
        if self.profile:
            doc.append(OWS.Profile(self.profile))
        if self.version != 'None':
            doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = self.version
        else:
            doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = 'undefined'

        return doc

    def describe_xml(self):
        input_elements = [i.describe_xml() for i in self.inputs]
        output_elements = [i.describe_xml() for i in self.outputs]

        doc = E.ProcessDescription(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = self.version

        if self.store_supported == 'true':
            doc.attrib['storeSupported'] = self.store_supported

        if self.status_supported == 'true':
            doc.attrib['statusSupported'] = self.status_supported

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata({'{http://www.w3.org/1999/xlink}title': m}))

        for p in self.profile:
            doc.append(WPS.Profile(p))

        if input_elements:
            doc.append(E.DataInputs(*input_elements))

        doc.append(E.ProcessOutputs(*output_elements))

        return doc

    def execute(self, wps_request, uuid):
        import multiprocessing
        self.uuid = uuid
        async = False
        wps_response = WPSResponse(self, wps_request, self.uuid)

        LOGGER.debug('Check if status storage and updating are supported by this process')
        if wps_request.store_execute == 'true':
            if self.store_supported != 'true':
                raise StorageNotSupported('Process does not support the storing of the execute response')

            file_path = config.get_config_value('server', 'outputpath')
            file_url = '%s%s' % (
                config.get_config_value('server', 'url'),
                config.get_config_value('server', 'outputurl')
            )

            self.status_location = os.path.join(file_path, str(self.uuid)) + '.xml'
            self.status_url = os.path.join(file_url, str(self.uuid)) + '.xml'

            if wps_request.status == 'true':
                if self.status_supported != 'true':
                    raise OperationNotSupported('Process does not support the updating of status')

                wps_response.status = WPSResponse.STORE_AND_UPDATE_STATUS
                async = True
            else:
                wps_response.status = WPSResponse.STORE_STATUS

        LOGGER.debug('Check if updating of status is not required then no need to spawn a process')
        if async:
            process = multiprocessing.Process(target=self._run_process, args=(wps_request, wps_response))
            process.start()
        else:
            wps_response = self._run_process(wps_request, wps_response)

        return wps_response

    def _run_process(self, wps_request, wps_response):
        try:
            wps_response = self.handler(wps_request, wps_response)

            # if status not yet set to 100% then do it after execution was successful
            if wps_response.status_percentage != 100:
                LOGGER.debug('Updating process status to 100% if everything went correctly')
                wps_response.update_status('PyWPS Process finished', 100)
        except Exception as e:
            traceback.print_exc()
            LOGGER.debug('Retrieving file and line number where exception occurred')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            found = False
            while not found:
                # search for the _handler method
                m_name = exc_tb.tb_frame.f_code.co_name
                if m_name == '_handler':
                    found = True
                else:
                    if exc_tb.tb_next is not None:
                        exc_tb = exc_tb.tb_next
                    else:
                        # if not found then take the first
                        exc_tb = sys.exc_info()[2]
                        break
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            method_name = exc_tb.tb_frame.f_code.co_name

            # update the process status to display process failed
            msg = 'Process error: %s.%s Line %i %s' % (fname, method_name, exc_tb.tb_lineno, e)
            LOGGER.error(msg)
            wps_response.update_status(msg, -1)

        return wps_response

    def set_workdir(self, workdir):
        """Set working dir for all inputs and outputs

        this is the directory, where all the data are being stored to
        """

        self.workdir = workdir
        for inpt in self.inputs:
            inpt.workdir = workdir

        for outpt in self.outputs:
            outpt.workdir = workdir
