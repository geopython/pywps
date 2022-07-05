##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
import tempfile
from typing import Sequence, Optional, Dict

from .basic import select_response_mimetype

from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request, Response
from urllib.parse import urlparse

from pywps.response.status import StatusResponse

import pywps
from pywps.app.WPSRequest import WPSRequest
from pywps.app.Process import Process
import pywps.configuration as config

from pywps.inout.inputs import ComplexInput, LiteralInput, BoundingBoxInput
from pywps.dblog import log_request, store_status
from pywps.inout.storage import get_storage_instance
from pywps.response.status import WPS_STATUS
from pywps.response.execute import ExecuteResponse
from pywps.response.describe import DescribeResponse
from pywps.response.capabilities import CapabilitiesResponse
from pywps import dblog
from pywps.exceptions import (StorageNotSupported, OperationNotSupported, MissingParameterValue, FileURLNotSupported,
                              ServerBusy, NoApplicableCode,
                              InvalidParameterValue)
from pywps.app.exceptions import ProcessError
import json

from collections import deque, OrderedDict
import os
import re
import sys
import copy
import shutil
import traceback

LOGGER = logging.getLogger("PYWPS")


# Handle one request
class ServiceInstance(object):
    def __init__(self, service, process):
        self.service = service
        self.process = process

    def _run_process(self, wps_request, wps_response):
        self.service._run_process(self.process, wps_request, wps_response)


class Service(object):

    """ The top-level object that represents a WPS service. It's a WSGI
    application.

    :param processes: A list of :class:`~Process` objects that are
                      provided by this service.

    :param cfgfiles: A list of configuration files
    """

    def __init__(self, processes: Sequence = [], cfgfiles=None, preprocessors: Optional[Dict] = None):
        # ordered dict of processes
        self.processes = OrderedDict((p.identifier, p) for p in processes)
        self.preprocessors = preprocessors or dict()

        if cfgfiles:
            config.load_configuration(cfgfiles)

        # Maximum running processes
        self.maxparallel = int(config.get_config_value('server', 'parallelprocesses'))

        # Maximum queued processes
        self.maxprocesses = int(config.get_config_value('server', 'maxprocesses'))

        if config.get_config_value('logging', 'file') and config.get_config_value('logging', 'level'):
            LOGGER.setLevel(getattr(logging, config.get_config_value('logging', 'level')))
            if not LOGGER.handlers:  # hasHandlers in Python 3.x
                fh = logging.FileHandler(config.get_config_value('logging', 'file'))
                fh.setFormatter(logging.Formatter(config.get_config_value('logging', 'format')))
                LOGGER.addHandler(fh)
        else:  # NullHandler | StreamHandler
            if not LOGGER.handlers:
                LOGGER.addHandler(logging.NullHandler())

    def get_capabilities(self, wps_request, uuid):
        return CapabilitiesResponse(wps_request, uuid, version=wps_request.version, processes=self.processes)

    def describe(self, wps_request, uuid, identifiers):
        return DescribeResponse(wps_request, uuid, processes=self.processes, identifiers=identifiers)

    # Return more or less accurate counts, if no concurrency
    def _get_accurate_process_counts(self):
        running, stored = dblog.get_process_counts()
        if self.maxparallel != -1 and running >= self.maxparallel:
            # Try to check for crashed process
            dblog.cleanup_crashed_process()
            running, stored = dblog.get_process_counts()
        return running, stored

    def _try_run_stored_processes(self):
        while self.launch_next_process():
            pass

    def execute(self, wps_request: WPSRequest):
        """Parse and perform Execute WPS request call

        :param identifier: process identifier string
        :param wps_request: pywps.WPSRequest structure with parsed inputs, still in memory
        :param uuid: string identifier of the request
        """

        LOGGER.debug('Check if the requested process exist')
        process = self.processes.get(wps_request.identifier, None)
        if process is None:
            raise InvalidParameterValue("Unknown process '{}'".format(wps_request.identifier), 'Identifier')

        LOGGER.debug('Check if status storage and updating are supported by this process')
        wps_request.is_async = process.is_async(wps_request)

        running, stored = self._get_accurate_process_counts()
        LOGGER.debug("Running processes: {} of {} allowed running processes".format(running, self.maxparallel))
        LOGGER.debug("Stored processes: {} of {} allowed stored process".format(stored, self.maxprocesses))

        if wps_request.is_async:
            if running < self.maxparallel or self.maxparallel == -1:
                # Run immediately
                process, wps_request, wps_response = self.prepare_process_for_execution(process, wps_request, True)
                wps_response._update_status(WPS_STATUS.ACCEPTED, "PyWPS Request accepted", 0)
                LOGGER.debug("Accepted request {}".format(process.uuid))
                self._run_async(process, wps_request, wps_response)
                return wps_response

            # try to store for later usage
            else:
                if stored >= self.maxprocesses and self.maxprocesses != -1:
                    raise ServerBusy('Maximum number of processes in queue reached. Please try later.')
                LOGGER.debug("Store process in job queue, uuid={}".format(process.uuid))
                process, wps_request, wps_response = self.prepare_process_for_execution(process, wps_request, True)
                dblog.store_process(wps_request)
                wps_response._update_status(WPS_STATUS.ACCEPTED, 'PyWPS Process stored in job queue', 0)
                return wps_response
        else:
            if running >= self.maxparallel and self.maxparallel != -1:
                raise ServerBusy('Maximum number of parallel running processes reached. Please try later.')

            process, wps_request, wps_response = self.prepare_process_for_execution(process, wps_request, True)
            wps_response._update_status(WPS_STATUS.ACCEPTED, "PyWPS Request accepted", 0)
            wps_response = process.run_process(wps_request, wps_response)
            return wps_response

    def prepare_process_for_execution(self, process: Process, wps_request: WPSRequest, fetch_inputs=False):
        """Prepare the process identified by ``identifier`` for execution.
        """
        self._set_grass()
        process = process.new_instance(wps_request)
        if fetch_inputs:
            wps_request = Service._parse_request_inputs(process, wps_request)
        wps_response = ExecuteResponse(wps_request, process=process, uuid=process.uuid)
        # Store status file if the process is asynchronous
        wps_response.store_status_file = wps_request.is_async
        return process, wps_request, wps_response

    def launch_next_process(self):
        """Look at the queue of async process, if the queue is not empty launch the next pending request.
        """
        try:
            LOGGER.debug("Checking for stored requests")

            stored_request = dblog.pop_first_stored_with_limit(self.maxparallel)
            if not stored_request:
                LOGGER.debug("No stored request found")
                return False

            (uuid, request_json) = (stored_request.uuid, stored_request.request)
            request_json = request_json.decode('utf-8')
            LOGGER.debug("Launching the stored request {}".format(str(uuid)))
            wps_request = WPSRequest(json=json.loads(request_json))
            process = self.processes.get(wps_request.identifier, None)
            if process is None:
                raise InvalidParameterValue("Unknown process '{}'".format(wps_request.identifier), 'Identifier')
            process, wps_request, wps_response = self.prepare_process_for_execution(process, wps_request, False)
            self._run_async(process, wps_request, wps_response)
        except Exception as e:
            LOGGER.exception("Could not run stored process. {}".format(e))
        return True

    # This function may not raise exception and must return a valid wps_response
    # Failure must be reported as wps_response.status = WPS_STATUS.FAILED
    def _run_async(self, process, wps_request, wps_response):
        import pywps.processing
        xprocess = pywps.processing.Process(
            process=ServiceInstance(self, process),
            wps_request=wps_request,
            wps_response=wps_response)
        LOGGER.debug("Starting process for request: {}".format(process.uuid))
        xprocess.start()

    # This function may not raise exception and must return a valid wps_response
    # Failure must be reported as wps_response.status = WPS_STATUS.FAILED
    def _run_process(self, process, wps_request, wps_response):
        LOGGER.debug("Started processing request: {} with pid: {}".format(process.uuid, os.getpid()))
        # Update the actual pid of current process to check if failed latter
        dblog.update_pid(process.uuid, os.getpid())
        try:
            wps_response = process.run_process(wps_request, wps_response)
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

            msg = 'Process error: method={}.{}, line={}, msg={}'.format(fname, method_name, exc_tb.tb_lineno, e)
            LOGGER.error(msg)
            # In case of a ProcessError use the validated exception message.
            if isinstance(e, ProcessError):
                msg = "Process error: {}".format(e)
            # Only in debug mode we use the log message including the traceback ...
            elif config.get_config_value("logging", "level") != "DEBUG":
                # ... otherwise we use a sparse common error message.
                msg = 'Process failed, please check server error log'
            wps_response._update_status(WPS_STATUS.FAILED, msg, 100)

        finally:
            # The run of the next pending request if finished here, weather or not it successful
            self._try_run_stored_processes()

        return wps_response

    @staticmethod
    def _parse_request_inputs(process: Process, wps_request: WPSRequest):
        """Parse input data for the given process and update wps_request accordingly
        """
        LOGGER.debug('Checking if all mandatory inputs have been passed')
        data_inputs = {}
        for inpt in process.inputs:
            # Replace the dicts with the dict of Literal/Complex inputs
            # set the input to the type defined in the process.

            request_inputs = wps_request.inputs.get(inpt.identifier, None)

            if request_inputs is None:
                if inpt._default is not None:
                    if not inpt.data_set and isinstance(inpt, ComplexInput):
                        inpt._set_default_value()
                    data_inputs[inpt.identifier] = [inpt.clone()]
            else:
                if isinstance(inpt, ComplexInput):
                    data_inputs[inpt.identifier] = Service.create_complex_inputs(inpt, request_inputs)
                elif isinstance(inpt, LiteralInput):
                    data_inputs[inpt.identifier] = Service.create_literal_inputs(inpt, request_inputs)
                elif isinstance(inpt, BoundingBoxInput):
                    data_inputs[inpt.identifier] = Service.create_bbox_inputs(inpt, request_inputs)

        # Check for missing inputs
        for inpt in process.inputs:
            if inpt.min_occurs > 0 and inpt.identifier not in data_inputs:
                LOGGER.error('Missing parameter value: {}'.format(inpt.identifier))
                raise MissingParameterValue(inpt.identifier, inpt.identifier)

        wps_request.inputs = data_inputs

        return wps_request

    @staticmethod
    def create_complex_inputs(source, inputs):
        """Create new ComplexInput as clone of original ComplexInput
        because of inputs can be more than one, take it just as Prototype.

        :param source: The process's input definition.
        :param inputs: The request input data.
        :return collections.deque:
        """

        outinputs = deque(maxlen=source.max_occurs)

        for inpt in inputs:
            data_input = source.clone()
            frmt = data_input.supported_formats[0]
            if 'mimeType' in inpt:
                if inpt['mimeType']:
                    frmt = data_input.get_format(inpt['mimeType'])
                else:
                    frmt = data_input.data_format

            if frmt:
                data_input.data_format = frmt
            else:
                raise InvalidParameterValue(
                    'Invalid mimeType value {} for input {}'.format(inpt.get('mimeType'), source.identifier),
                    'mimeType')

            data_input.method = inpt.get('method', 'GET')
            data_input.process(inpt)
            outinputs.append(data_input)

        if len(outinputs) < source.min_occurs:
            description = "At least {} inputs are required. You provided {}.".format(
                source.min_occurs,
                len(outinputs),
            )
            raise MissingParameterValue(description=description, locator=source.identifier)
        return outinputs

    @staticmethod
    def create_literal_inputs(source, inputs):
        """ Takes the http_request and parses the input to objects
        :return collections.deque:
        """

        outinputs = deque(maxlen=source.max_occurs)

        for inpt in inputs:
            newinpt = source.clone()
            # set the input to the type defined in the process
            newinpt.uom = inpt.get('uom')
            data_type = inpt.get('datatype')
            if data_type:
                newinpt.data_type = data_type

            # get the value of the field
            newinpt.data = inpt.get('data')

            outinputs.append(newinpt)

        if len(outinputs) < source.min_occurs:
            description = "At least {} inputs are required. You provided {}.".format(
                source.min_occurs,
                len(outinputs),
            )
            raise MissingParameterValue(description, locator=source.identifier)

        return outinputs

    def _set_grass(self):
        """Set environment variables needed for GRASS GIS support
        """
        gisbase = config.get_config_value('grass', 'gisbase')
        if gisbase and os.path.isdir(gisbase):
            LOGGER.debug('GRASS GISBASE set to {}'.format(gisbase))

            os.environ['GISBASE'] = gisbase

            os.environ['LD_LIBRARY_PATH'] = '{}:{}'.format(
                os.environ.get('LD_LIBRARY_PATH'),
                os.path.join(gisbase, 'lib'))
            os.putenv('LD_LIBRARY_PATH', os.environ.get('LD_LIBRARY_PATH'))

            os.environ['PATH'] = '{}:{}:{}'.format(
                os.environ.get('PATH'),
                os.path.join(gisbase, 'bin'),
                os.path.join(gisbase, 'scripts'))
            os.putenv('PATH', os.environ.get('PATH'))

            python_path = os.path.join(gisbase, 'etc', 'python')
            os.environ['PYTHONPATH'] = '{}:{}'.format(os.environ.get('PYTHONPATH'),
                                                      python_path)
            os.putenv('PYTHONPATH', os.environ.get('PYTHONPATH'))
            sys.path.insert(0, python_path)

    @staticmethod
    def create_bbox_inputs(source, inputs):
        """ Takes the http_request and parses the input to objects
        :return collections.deque:
        """

        outinputs = deque(maxlen=source.max_occurs)

        for inpt in inputs:
            newinpt = source.clone()
            newinpt.data = inpt.get('data')
            LOGGER.debug(f'newinpt bbox data={newinpt.data}')
            newinpt.crs = inpt.get('crs')
            newinpt.dimensions = inpt.get('dimensions')
            outinputs.append(newinpt)

        if len(outinputs) < source.min_occurs:
            description = "At least {} inputs are required. You provided {}.".format(
                source.min_occurs,
                len(outinputs),
            )
            raise MissingParameterValue(description=description, locator=source.identifier)

        return outinputs

    @staticmethod
    def _process_files(http_request):
        if http_request.method != "GET":
            return Response("Method Not Allowed", status=405)
        file_uuid = http_request.args.get('uuid', None)
        if file_uuid is None:
            raise NoApplicableCode("Invalid uuid for files request", code=500)
        store = get_storage_instance(file_uuid)
        if store is None:
            raise NoApplicableCode("Invalid uuid for files request", code=500)
        if store.mimetype is None:
            raise NoApplicableCode("Invalid uuid for files request", code=500)
        return Response(store.open("r"),
                        mimetype=store.mimetype,
                        headers={'Content-Disposition': f'attachment; filename="{store.pretty_filename}"'})

    @staticmethod
    def _process_status(http_request):
        if http_request.method != "GET":
            return Response("Method Not Allowed", status=405)
        process_uuid = http_request.args.get('uuid', None)
        if process_uuid is None:
            raise NoApplicableCode("Invalid uuid for status request", code=500)
        status = dblog.get_status_record(process_uuid)
        if status is None:
            raise NoApplicableCode("Invalid uuid for status request", code=500)
        mimetype = select_response_mimetype(http_request.accept_mimetypes, None)
        return StatusResponse(status.data, mimetype)

    def _process_wps(self, http_request):
        """
        Process WPS request
        Note: the WPS request may use non standard REST api, see pywps.app.basic.parse_http_url
        """
        environ_cfg = http_request.environ.get('PYWPS_CFG')
        if 'PYWPS_CFG' not in os.environ and environ_cfg:
            LOGGER.debug('Setting PYWPS_CFG to {}'.format(environ_cfg))
            os.environ['PYWPS_CFG'] = environ_cfg

        wps_request = WPSRequest(http_request=http_request, preprocessors=self.preprocessors)
        LOGGER.info('Request: {}'.format(wps_request.operation))
        if wps_request.operation in ['getcapabilities',
                                     'describeprocess',
                                     'execute']:
            log_request(wps_request.uuid, wps_request)
            try:
                response = None
                if wps_request.operation == 'getcapabilities':
                    response = self.get_capabilities(wps_request, wps_request.uuid)
                    response._update_status(WPS_STATUS.SUCCEEDED, '', 100)

                elif wps_request.operation == 'describeprocess':
                    response = self.describe(wps_request, wps_request.uuid, wps_request.identifiers)
                    response._update_status(WPS_STATUS.SUCCEEDED, '', 100)

                elif wps_request.operation == 'execute':
                    response = self.execute(wps_request)
                return response
            except Exception as e:
                # This ensure that logged request get terminated in case of exception while the request is not
                # accepted
                store_status(wps_request.uuid, WPS_STATUS.FAILED, 'Request rejected due to exception', 100)
                raise e
        else:
            raise RuntimeError("Unknown operation {}".format(wps_request.operation))

    # May not raise exceptions, this function must return a valid werkzeug.wrappers.Response.
    def call(self, http_request):

        # Before running the current request try to run older async request
        self._try_run_stored_processes()

        try:
            # This try block handle Exception generated before the request is accepted. Once the request is accepted
            # a valid wps_reponse must exist. To report error use the wps_response using
            # wps_response._update_status(WPS_STATUS.FAILED, ...).
            #
            # We need this behaviour to handle the status file correctly, once the request is accepted, a
            # status file may be created and failure must be reported in this file instead of a raw ows:ExceptionReport
            #
            # Exeception from CapabilityResponse and DescribeResponse are always catched by this try ... except close
            # because they never have status.

            p = re.compile("^/(wps|api|processes|jobs|files|status)(/.+)?$")

            m = p.match(http_request.path)
            if m is None:
                return Response("Not Found", status=404)

            # TODO: make sane dispatch
            if m.group(1) in ['wps', 'api', 'processes', 'jobs']:
                return self._process_wps(http_request)
            elif m.group(1) == 'files':
                return Service._process_files(http_request)
            elif m.group(1) == 'status':
                return Service._process_status(http_request)
            else:
                return Response("Not Found", status=404)

        except NoApplicableCode as e:
            return e
        except HTTPException as e:
            return NoApplicableCode(e.description, code=e.code)
        except Exception:
            msg = "No applicable error code, please check error log."
            return NoApplicableCode(msg, code=500)

    @Request.application
    def __call__(self, http_request):
        return self.call(http_request)


def _build_input_file_name(href, workdir, extension=None):
    href = href or ''
    url_path = urlparse(href).path or ''
    file_name = os.path.basename(url_path).strip() or 'input'
    (prefix, suffix) = os.path.splitext(file_name)
    suffix = suffix or extension or ''
    if prefix and suffix:
        file_name = prefix + suffix
    input_file_name = os.path.join(workdir, file_name)
    # build tempfile in case of duplicates
    if os.path.exists(input_file_name):
        input_file_name = tempfile.mkstemp(
            suffix=suffix, prefix=prefix + '_',
            dir=workdir)[1]
    return input_file_name


def _validate_file_input(href):
    href = href or ''
    parsed_url = urlparse(href)
    if parsed_url.scheme != 'file':
        raise FileURLNotSupported('Invalid URL scheme')
    file_path = parsed_url.path
    if not file_path:
        raise FileURLNotSupported('Invalid URL path')
    file_path = os.path.abspath(file_path)
    # build allowed paths list
    inputpaths = config.get_config_value('server', 'allowedinputpaths')
    allowed_paths = [os.path.abspath(p.strip()) for p in inputpaths.split(os.pathsep) if p.strip()]
    for allowed_path in allowed_paths:
        if file_path.startswith(allowed_path):
            LOGGER.debug("Accepted file url as input.")
            return
    raise FileURLNotSupported()


def _extension(complexinput):
    extension = None
    if complexinput.data_format:
        extension = complexinput.data_format.extension
    return extension
