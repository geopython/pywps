##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
import tempfile
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request, Response
from pywps._compat import PY2
from pywps._compat import urlparse
from pywps.app.WPSRequest import WPSRequest
import pywps.configuration as config
from pywps.exceptions import MissingParameterValue, NoApplicableCode, InvalidParameterValue, FileSizeExceeded, \
    StorageNotSupported, FileURLNotSupported
from pywps.inout.inputs import ComplexInput, LiteralInput, BoundingBoxInput
from pywps.dblog import log_request, store_status
from pywps import response
from pywps.response.status import WPS_STATUS

from collections import deque, OrderedDict
import os
import sys
import uuid
import copy
import requests
import shutil


LOGGER = logging.getLogger("PYWPS")


class Service(object):

    """ The top-level object that represents a WPS service. It's a WSGI
    application.

    :param processes: A list of :class:`~Process` objects that are
                      provided by this service.

    :param cfgfiles: A list of configuration files
    """

    def __init__(self, processes=[], cfgfiles=None):
        # ordered dict of processes
        self.processes = OrderedDict((p.identifier, p) for p in processes)

        if cfgfiles:
            config.load_configuration(cfgfiles)

        if config.get_config_value('logging', 'file') and config.get_config_value('logging', 'level'):
            LOGGER.setLevel(getattr(logging, config.get_config_value('logging', 'level')))
            fh = logging.FileHandler(config.get_config_value('logging', 'file'))
            fh.setFormatter(logging.Formatter(config.get_config_value('logging', 'format')))
            LOGGER.addHandler(fh)
        else:  # NullHandler | StreamHandler
            LOGGER.addHandler(logging.NullHandler())

    def get_capabilities(self, wps_request, uuid):

        response_cls = response.get_response("capabilities")
        return response_cls(wps_request, uuid, version=wps_request.version, processes=self.processes)

    def describe(self, wps_request, uuid, identifiers):

        response_cls = response.get_response("describe")
        return response_cls(wps_request, uuid, processes=self.processes,
                            identifiers=identifiers)

    def execute(self, identifier, wps_request, uuid):
        """Parse and perform Execute WPS request call

        :param identifier: process identifier string
        :param wps_request: pywps.WPSRequest structure with parsed inputs, still in memory
        :param uuid: string identifier of the request
        """
        self._set_grass()
        process = self.prepare_process_for_execution(identifier)
        return self._parse_and_execute(process, wps_request, uuid)

    def prepare_process_for_execution(self, identifier):
        """Prepare the process identified by ``identifier`` for execution.
        """
        try:
            process = self.processes[identifier]
        except KeyError:
            raise InvalidParameterValue("Unknown process '%r'" % identifier, 'Identifier')
        # make deep copy of the process instace
        # so that processes are not overriding each other
        # just for execute
        process = copy.deepcopy(process)
        process.service = self
        workdir = os.path.abspath(config.get_config_value('server', 'workdir'))
        tempdir = tempfile.mkdtemp(prefix='pywps_process_', dir=workdir)
        process.set_workdir(tempdir)
        return process

    def _parse_and_execute(self, process, wps_request, uuid):
        """Parse and execute request
        """

        LOGGER.debug('Checking if all mandatory inputs have been passed')
        data_inputs = {}
        for inpt in process.inputs:
            # Replace the dicts with the dict of Literal/Complex inputs
            # set the input to the type defined in the process.

            request_inputs = None
            if inpt.identifier in wps_request.inputs:
                request_inputs = wps_request.inputs[inpt.identifier]

            if not request_inputs:
                if inpt.data_set:
                    data_inputs[inpt.identifier] = [inpt.clone()]
            else:

                if isinstance(inpt, ComplexInput):
                    data_inputs[inpt.identifier] = self.create_complex_inputs(
                        inpt, request_inputs)
                elif isinstance(inpt, LiteralInput):
                    data_inputs[inpt.identifier] = self.create_literal_inputs(
                        inpt, request_inputs)
                elif isinstance(inpt, BoundingBoxInput):
                    data_inputs[inpt.identifier] = self.create_bbox_inputs(
                        inpt, request_inputs)

        for inpt in process.inputs:

            if inpt.identifier not in data_inputs:
                if inpt.min_occurs > 0:
                    LOGGER.error('Missing parameter value: %s', inpt.identifier)
                    raise MissingParameterValue(
                        inpt.identifier, inpt.identifier)

        wps_request.inputs = data_inputs

        # set as_reference to True for all the outputs specified as reference
        # if the output is not required to be raw
        if not wps_request.raw:
            for wps_outpt in wps_request.outputs:

                is_reference = wps_request.outputs[
                    wps_outpt].get('asReference', 'false')
                if is_reference.lower() == 'true':
                    # check if store is supported
                    if process.store_supported == 'false':
                        raise StorageNotSupported(
                            'The storage of data is not supported for this process.')

                    is_reference = True
                else:
                    is_reference = False

                for outpt in process.outputs:
                    if outpt.identifier == wps_outpt:
                        outpt.as_reference = is_reference

        wps_response = process.execute(wps_request, uuid)
        return wps_response

    def _get_complex_input_handler(self, href):
        """Return function for parsing and storing complexdata
        :param href: href object yes or not
        """

        def href_handler(complexinput, datain):
            """<wps:Reference /> handler"""
            # save the reference input in workdir
            tmp_file = _build_input_file_name(
                href=datain.get('href'),
                workdir=complexinput.workdir,
                extension=_extension(complexinput))

            try:
                reference_file = _openurl(datain)
                data_size = reference_file.headers.get('Content-Length', 0)
            except Exception as e:
                raise NoApplicableCode('File reference error: %s' % e)

            # if the response did not return a 'Content-Length' header then
            # calculate the size
            if data_size == 0:
                LOGGER.debug('no Content-Length, calculating size')

            # check if input file size was not exceeded
            complexinput.calculate_max_input_size()
            max_byte_size = complexinput.max_size * 1024 * 1024
            if int(data_size) > int(max_byte_size):
                raise FileSizeExceeded('File size for input exceeded.'
                                       ' Maximum allowed: %i megabytes' %
                                       complexinput.max_size, complexinput.identifier)

            try:
                with open(tmp_file, 'wb') as f:
                    data_size = 0
                    for chunk in reference_file.iter_content(chunk_size=1024):
                        data_size += len(chunk)
                        if int(data_size) > int(max_byte_size):
                            raise FileSizeExceeded('File size for input exceeded.'
                                                   ' Maximum allowed: %i megabytes' %
                                                   complexinput.max_size, complexinput.identifier)
                        f.write(chunk)
            except Exception as e:
                raise NoApplicableCode(e)

            complexinput.file = tmp_file
            assert complexinput.url == datain.get('href')

        def file_handler(complexinput, datain):
            """<wps:Reference /> handler.
            Used when href is a file url."""
            # check if file url is allowed
            _validate_file_input(href=datain.get('href'))
            # save the file reference input in workdir
            tmp_file = _build_input_file_name(
                href=datain.get('href'),
                workdir=complexinput.workdir,
                extension=_extension(complexinput))
            try:
                inpt_file = urlparse(datain.get('href')).path
                inpt_file = os.path.abspath(inpt_file)
                os.symlink(inpt_file, tmp_file)
                LOGGER.debug("Linked input file %s to %s.", inpt_file, tmp_file)
            except Exception:
                # TODO: handle os.symlink on windows
                # raise NoApplicableCode("Could not link file reference: %s" % e)
                LOGGER.warn("Could not link file reference")
                shutil.copy2(inpt_file, tmp_file)

            complexinput.file = tmp_file
            assert complexinput.url == datain.get('href')

        def data_handler(complexinput, datain):
            """<wps:Data> ... </wps:Data> handler"""

            complexinput.data = datain.get('data')

        if href:
            if urlparse(href).scheme == 'file':
                return file_handler
            else:
                return href_handler
        else:
            return data_handler

    def create_complex_inputs(self, source, inputs):
        """Create new ComplexInput as clone of original ComplexInput
        because of inputs can be more then one, take it just as Prototype
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
                    'Invalid mimeType value %s for input %s' %
                    (inpt.get('mimeType'), source.identifier),
                    'mimeType')

            data_input.method = inpt.get('method', 'GET')

            # get the referenced input otherwise get the value of the field
            href = inpt.get('href', None)

            complex_data_handler = self._get_complex_input_handler(href)
            complex_data_handler(data_input, inpt)

            outinputs.append(data_input)
        if len(outinputs) < source.min_occurs:
            raise MissingParameterValue(description="Given data input is missing", locator=source.identifier)
        return outinputs

    def create_literal_inputs(self, source, inputs):
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
            raise MissingParameterValue(locator=source.identifier)

        return outinputs

    def _set_grass(self):
        """Set environment variables needed for GRASS GIS support
        """

        if not PY2:
            LOGGER.debug('Python3 is not supported by GRASS')
            return

        gisbase = config.get_config_value('grass', 'gisbase')
        if gisbase and os.path.isdir(gisbase):
            LOGGER.debug('GRASS GISBASE set to %s' % gisbase)

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

    def create_bbox_inputs(self, source, inputs):
        """ Takes the http_request and parses the input to objects
        :return collections.deque:
        """

        outinputs = deque(maxlen=source.max_occurs)

        for datainput in inputs:
            newinpt = source.clone()
            newinpt.data = [datainput.minx, datainput.miny,
                            datainput.maxx, datainput.maxy]
            outinputs.append(newinpt)

        if len(outinputs) < source.min_occurs:
            raise MissingParameterValue(
                description='Number of inputs is lower than minium required number of inputs',
                locator=source.identifier)

        return outinputs

    # May not raise exceptions, this function must return a valid werkzeug.wrappers.Response.
    def call(self, http_request):
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

            request_uuid = uuid.uuid1()

            environ_cfg = http_request.environ.get('PYWPS_CFG')
            if 'PYWPS_CFG' not in os.environ and environ_cfg:
                LOGGER.debug('Setting PYWPS_CFG to %s', environ_cfg)
                os.environ['PYWPS_CFG'] = environ_cfg

            wps_request = WPSRequest(http_request)
            LOGGER.info('Request: %s', wps_request.operation)
            if wps_request.operation in ['getcapabilities',
                                         'describeprocess',
                                         'execute']:
                log_request(request_uuid, wps_request)
                try:
                    response = None
                    if wps_request.operation == 'getcapabilities':
                        response = self.get_capabilities(wps_request, request_uuid)
                        response._update_status(WPS_STATUS.SUCCEEDED, u'', 100)

                    elif wps_request.operation == 'describeprocess':
                        response = self.describe(wps_request, request_uuid, wps_request.identifiers)
                        response._update_status(WPS_STATUS.SUCCEEDED, u'', 100)

                    elif wps_request.operation == 'execute':
                        response = self.execute(
                            wps_request.identifier,
                            wps_request,
                            request_uuid
                        )
                    return response
                except Exception as e:
                    # This ensure that logged request get terminated in case of exception while the request is not
                    # accepted
                    store_status(request_uuid, WPS_STATUS.FAILED, u'Request rejected due to exception', 100)
                    raise e
            else:
                raise RuntimeError("Unknown operation %r"
                                   % wps_request.operation)

        except NoApplicableCode as e:
            return e
        except HTTPException as e:
            return NoApplicableCode(e.description, code=e.code)
        except Exception as e:
            return NoApplicableCode("No applicable error code, please check error log", code=500)

    @Request.application
    def __call__(self, http_request):
        return self.call(http_request)


def _openurl(inpt):
    """use requests to open given href
    """
    data = None
    href = inpt.get('href')

    LOGGER.debug('Fetching URL %s', href)
    if inpt.get('method') == 'POST':
        if 'body' in inpt:
            data = inpt.get('body')
        elif 'bodyreference' in inpt:
            data = requests.get(url=inpt.get('bodyreference')).text

        reference_file = requests.post(url=href, data=data, stream=True)
    else:
        reference_file = requests.get(url=href, stream=True)

    return reference_file


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
    allowed_paths = [os.path.abspath(p.strip()) for p in inputpaths.split(':') if p.strip()]
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
