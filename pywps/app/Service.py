##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


import logging
import tempfile
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request, Response
from pywps import WPS, OWS
from pywps._compat import PY2
from pywps._compat import urlopen
from pywps.app.basic import xml_response
from pywps.app.WPSRequest import WPSRequest
import pywps.configuration as config
from pywps.exceptions import MissingParameterValue, NoApplicableCode, InvalidParameterValue, FileSizeExceeded, \
    StorageNotSupported
from pywps.inout.inputs import ComplexInput, LiteralInput, BoundingBoxInput
from pywps.dblog import log_request, update_response

from collections import deque
import os
import sys
import uuid
import copy

LOGGER = logging.getLogger("PYWPS")


class Service(object):

    """ The top-level object that represents a WPS service. It's a WSGI
    application.

    :param processes: A list of :class:`~Process` objects that are
                      provided by this service.

    :param cfgfiles: A list of configuration files
    """

    def __init__(self, processes=[], cfgfiles=None):
        self.processes = {p.identifier: p for p in processes}

        if cfgfiles:
            config.load_configuration(cfgfiles)

        if config.get_config_value('logging', 'file') and config.get_config_value('logging', 'level'):
            LOGGER.setLevel(getattr(logging, config.get_config_value('logging', 'level')))
            msg_fmt = '%(asctime)s] [%(levelname)s] file=%(pathname)s line=%(lineno)s module=%(module)s function=%(funcName)s %(message)s'  # noqa
            fh = logging.FileHandler(config.get_config_value('logging', 'file'))
            fh.setFormatter(logging.Formatter(msg_fmt))
            LOGGER.addHandler(fh)
        else:  # NullHandler
            LOGGER.addHandler(logging.NullHandler())

    def get_capabilities(self):
        process_elements = [p.capabilities_xml()
                            for p in self.processes.values()]

        doc = WPS.Capabilities()

        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-US'
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = \
            'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd'
        # TODO: check Table 7 in OGC 05-007r7
        doc.attrib['updateSequence'] = '1'

        # Service Identification
        service_ident_doc = OWS.ServiceIdentification(
            OWS.Title(config.get_config_value('metadata:main', 'identification_title'))
        )

        if config.get_config_value('metadata:main', 'identification_abstract'):
            service_ident_doc.append(
                OWS.Abstract(config.get_config_value('metadata:main', 'identification_abstract')))

        if config.get_config_value('metadata:main', 'identification_keywords'):
            keywords_doc = OWS.Keywords()
            for k in config.get_config_value('metadata:main', 'identification_keywords').split(','):
                if k:
                    keywords_doc.append(OWS.Keyword(k))
            service_ident_doc.append(keywords_doc)

        if config.get_config_value('metadata:main', 'identification_keywords_type'):
            keywords_type = OWS.Type(config.get_config_value('metadata:main', 'identification_keywords_type'))
            keywords_type.attrib['codeSpace'] = 'ISOTC211/19115'
            keywords_doc.append(keywords_type)

        service_ident_doc.append(OWS.ServiceType('WPS'))

        # TODO: set proper version support
        service_ident_doc.append(OWS.ServiceTypeVersion('1.0.0'))

        service_ident_doc.append(
            OWS.Fees(config.get_config_value('metadata:main', 'identification_fees')))

        for con in config.get_config_value('metadata:main', 'identification_accessconstraints').split(','):
            service_ident_doc.append(OWS.AccessConstraints(con))

        if config.get_config_value('metadata:main', 'identification_profile'):
            service_ident_doc.append(
                OWS.Profile(config.get_config_value('metadata:main', 'identification_profile')))

        doc.append(service_ident_doc)

        # Service Provider
        service_prov_doc = OWS.ServiceProvider(
            OWS.ProviderName(config.get_config_value('metadata:main', 'provider_name')))

        if config.get_config_value('metadata:main', 'provider_url'):
            service_prov_doc.append(OWS.ProviderSite(
                {'{http://www.w3.org/1999/xlink}href': config.get_config_value('metadata:main', 'provider_url')})
            )

        # Service Contact
        service_contact_doc = OWS.ServiceContact()

        # Add Contact information only if a name is set
        if config.get_config_value('metadata:main', 'contact_name'):
            service_contact_doc.append(
                OWS.IndividualName(config.get_config_value('metadata:main', 'contact_name')))
            if config.get_config_value('metadata:main', 'contact_position'):
                service_contact_doc.append(
                    OWS.PositionName(config.get_config_value('metadata:main', 'contact_position')))

            contact_info_doc = OWS.ContactInfo()

            phone_doc = OWS.Phone()
            if config.get_config_value('metadata:main', 'contact_phone'):
                phone_doc.append(
                    OWS.Voice(config.get_config_value('metadata:main', 'contact_phone')))
            if config.get_config_value('metadata:main', 'contaact_fax'):
                phone_doc.append(
                    OWS.Facsimile(config.get_config_value('metadata:main', 'contact_fax')))
            # Add Phone if not empty
            if len(phone_doc):
                contact_info_doc.append(phone_doc)

            address_doc = OWS.Address()
            if config.get_config_value('metadata:main', 'deliveryPoint'):
                address_doc.append(
                    OWS.DeliveryPoint(config.get_config_value('metadata:main', 'contact_address')))
            if config.get_config_value('metadata:main', 'city'):
                address_doc.append(
                    OWS.City(config.get_config_value('metadata:main', 'contact_city')))
            if config.get_config_value('metadata:main', 'contact_stateorprovince'):
                address_doc.append(
                    OWS.AdministrativeArea(config.get_config_value('metadata:main', 'contact_stateorprovince')))
            if config.get_config_value('metadata:main', 'contact_postalcode'):
                address_doc.append(
                    OWS.PostalCode(config.get_config_value('metadata:main', 'contact_postalcode')))
            if config.get_config_value('metadata:main', 'contact_country'):
                address_doc.append(
                    OWS.Country(config.get_config_value('metadata:main', 'contact_country')))
            if config.get_config_value('metadata:main', 'contact_email'):
                address_doc.append(
                    OWS.ElectronicMailAddress(
                        config.get_config_value('metadata:main', 'contact_email'))
                )
            # Add Address if not empty
            if len(address_doc):
                contact_info_doc.append(address_doc)

            if config.get_config_value('metadata:main', 'contact_url'):
                contact_info_doc.append(OWS.OnlineResource(
                    {'{http://www.w3.org/1999/xlink}href': config.get_config_value('metadata:main', 'contact_url')})
                )
            if config.get_config_value('metadata:main', 'contact_hours'):
                contact_info_doc.append(
                    OWS.HoursOfService(config.get_config_value('metadata:main', 'contact_hours')))
            if config.get_config_value('metadata:main', 'contact_instructions'):
                contact_info_doc.append(OWS.ContactInstructions(
                    config.get_config_value('metadata:main', 'contact_instructions')))

            # Add Contact information if not empty
            if len(contact_info_doc):
                service_contact_doc.append(contact_info_doc)

            if config.get_config_value('metadata:main', 'contact_role'):
                service_contact_doc.append(
                    OWS.Role(config.get_config_value('metadata:main', 'contact_role')))

        # Add Service Contact only if ProviderName and PositionName are set
        if len(service_contact_doc):
            service_prov_doc.append(service_contact_doc)

        doc.append(service_prov_doc)

        server_href = {'{http://www.w3.org/1999/xlink}href': config.get_config_value('server', 'url')}

        # Operations Metadata
        operations_metadata_doc = OWS.OperationsMetadata(
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get(server_href),
                        OWS.Post(server_href)
                    )
                ),
                name="GetCapabilities"
            ),
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get(server_href),
                        OWS.Post(server_href)
                    )
                ),
                name="DescribeProcess"
            ),
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get(server_href),
                        OWS.Post(server_href)
                    )
                ),
                name="Execute"
            )
        )
        doc.append(operations_metadata_doc)

        doc.append(WPS.ProcessOfferings(*process_elements))

        languages = config.get_config_value('server', 'language').split(',')
        languages_doc = WPS.Languages(
            WPS.Default(
                OWS.Language(languages[0])
            )
        )
        lang_supported_doc = WPS.Supported()
        for l in languages:
            lang_supported_doc.append(OWS.Language(l))
        languages_doc.append(lang_supported_doc)

        doc.append(languages_doc)

        return xml_response(doc)

    def describe(self, identifiers):
        if not identifiers:
            raise MissingParameterValue('', 'identifier')

        identifier_elements = []
        # 'all' keyword means all processes
        if 'all' in (ident.lower() for ident in identifiers):
            for process in self.processes:
                try:
                    identifier_elements.append(
                        self.processes[process].describe_xml())
                except Exception as e:
                    raise NoApplicableCode(e)
        else:
            for identifier in identifiers:
                try:
                    process = self.processes[identifier]
                except KeyError:
                    raise InvalidParameterValue(
                        "Unknown process %r" % identifier, "identifier")
                else:
                    try:
                        identifier_elements.append(process.describe_xml())
                    except Exception as e:
                        raise NoApplicableCode(e)

        doc = WPS.ProcessDescriptions(
            *identifier_elements
        )
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = \
            'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'
        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-US'
        return xml_response(doc)

    def execute(self, identifier, wps_request, uuid):
        """Parse and perform Execute WPS request call

        :param identifier: process identifier string
        :param wps_request: pywps.WPSRequest structure with parsed inputs, still in memory
        :param uuid: string identifier of the request
        """
        self._set_grass()
        response = None
        try:
            process = self.processes[identifier]

            # make deep copy of the process instace
            # so that processes are not overriding each other
            # just for execute
            process = copy.deepcopy(process)

            workdir = os.path.abspath(config.get_config_value('server', 'workdir'))
            tempdir = tempfile.mkdtemp(prefix='pywps_process_', dir=workdir)
            process.set_workdir(tempdir)
        except KeyError:
            raise InvalidParameterValue("Unknown process '%r'" % identifier, 'Identifier')

        olddir = os.path.abspath(os.curdir)
        try:
            os.chdir(process.workdir)
            response = self._parse_and_execute(process, wps_request, uuid)
        finally:
            os.chdir(olddir)

        return response

    def _parse_and_execute(self, process, wps_request, uuid):
        """Parse and execute request
        """
        LOGGER.debug('Checking if datainputs is required and has been passed')
        if process.inputs:
            if wps_request.inputs is None:
                raise MissingParameterValue('Missing "datainputs" parameter', 'datainputs')

        LOGGER.debug('Checking if all mandatory inputs have been passed')
        data_inputs = {}
        for inpt in process.inputs:
            if inpt.identifier not in wps_request.inputs:
                if inpt.min_occurs > 0:
                    LOGGER.error('Missing parameter value: %s', inpt.identifier)
                    raise MissingParameterValue(
                        inpt.identifier, inpt.identifier)
                else:
                    # inputs = deque(maxlen=inpt.max_occurs)
                    # inputs.append(inpt.clone())
                    # data_inputs[inpt.identifier] = inputs
                    pass
            else:
                # Replace the dicts with the dict of Literal/Complex inputs
                # set the input to the type defined in the process.
                if isinstance(inpt, ComplexInput):
                    data_inputs[inpt.identifier] = self.create_complex_inputs(
                        inpt, wps_request.inputs[inpt.identifier])
                elif isinstance(inpt, LiteralInput):
                    data_inputs[inpt.identifier] = self.create_literal_inputs(
                        inpt, wps_request.inputs[inpt.identifier])
                elif isinstance(inpt, BoundingBoxInput):
                    data_inputs[inpt.identifier] = self.create_bbox_inputs(
                        inpt, wps_request.inputs[inpt.identifier])

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

        # catch error generated by process code
        try:
            wps_response = process.execute(wps_request, uuid)
        except Exception as e:
            if not isinstance(e, NoApplicableCode):
                raise NoApplicableCode('Service error: %s' % e)
            raise e

        # get the specified output as raw
        if wps_request.raw:
            for outpt in wps_request.outputs:
                for proc_outpt in process.outputs:
                    if outpt == proc_outpt.identifier:
                        resp = Response(proc_outpt.data)
                        resp.call_on_close(process.clean)
                        return resp

            # if the specified identifier was not found raise error
            raise InvalidParameterValue('')

        return wps_response

    def _get_complex_input_handler(self, href):
        """Return function for parsing and storing complexdata
        :param href: href object yes or not
        """

        def href_handler(complexinput, datain):
            """<wps:Reference /> handler"""
            # save the reference input in workdir
            tmp_file = tempfile.mkstemp(dir=complexinput.workdir)[1]

            try:
                (reference_file, reference_file_data) = _openurl(datain)
                data_size = reference_file.headers.get('Content-Length', 0)
            except Exception as e:
                raise NoApplicableCode('File reference error: %s' % e)

            # if the response did not return a 'Content-Length' header then
            # calculate the size
            if data_size == 0:
                LOGGER.debug('no Content-Length, calculating size')
                data_size = _get_datasize(reference_file_data)

            # check if input file size was not exceeded
            complexinput.calculate_max_input_size()
            byte_size = complexinput.max_size * 1024 * 1024
            if int(data_size) > int(byte_size):
                raise FileSizeExceeded('File size for input exceeded.'
                                       ' Maximum allowed: %i megabytes' %
                                       complexinput.max_size, complexinput.get('identifier'))

            try:
                with open(tmp_file, 'w') as f:
                    f.write(reference_file_data)
            except Exception as e:
                raise NoApplicableCode(e)

            complexinput.file = tmp_file
            complexinput.url = datain.get('href')
            complexinput.as_reference = True

        def data_handler(complexinput, datain):
            """<wps:Data> ... </wps:Data> handler"""

            complexinput.data = datain.get('data')

        if href:
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

    @Request.application
    def __call__(self, http_request):

        request_uuid = uuid.uuid1()

        environ_cfg = http_request.environ.get('PYWPS_CFG')
        if 'PYWPS_CFG' not in os.environ and environ_cfg:
            LOGGER.debug('Setting PYWPS_CFG to %s', environ_cfg)
            os.environ['PYWPS_CFG'] = environ_cfg

        try:
            wps_request = WPSRequest(http_request)
            LOGGER.info('Request: %s', wps_request.operation)
            if wps_request.operation in ['getcapabilities',
                                         'describeprocess',
                                         'execute']:
                log_request(request_uuid, wps_request)
                response = None
                if wps_request.operation == 'getcapabilities':
                    response = self.get_capabilities()

                elif wps_request.operation == 'describeprocess':
                    response = self.describe(wps_request.identifiers)

                elif wps_request.operation == 'execute':
                    response = self.execute(
                        wps_request.identifier,
                        wps_request,
                        request_uuid
                    )
                update_response(request_uuid, response, close=True)
                return response
            else:
                update_response(request_uuid, response, close=True)
                raise RuntimeError("Unknown operation %r"
                                   % wps_request.operation)

        except HTTPException as e:
            # transform HTTPException to OWS NoApplicableCode exception
            if not isinstance(e, NoApplicableCode):
                e = NoApplicableCode(e.description, code=e.code)

            class FakeResponse:
                message = e.locator
                status = e.code
                status_percentage = 100
            try:
                update_response(request_uuid, FakeResponse, close=True)
            except NoApplicableCode as e:
                return e
            return e


def _openurl(inpt):
    """use urllib to open given href
    """
    data = None
    reference_file = None
    href = inpt.get('href')

    LOGGER.debug('Fetching URL %s', href)
    if inpt.get('method') == 'POST':
        if 'body' in inpt:
            data = inpt.get('body')
        elif 'bodyreference' in inpt:
            data = urlopen(url=inpt.get('bodyreference')).read()

        reference_file = urlopen(url=href, data=data)
    else:
        reference_file = urlopen(url=href)

    if PY2:
        reference_file_data = reference_file.read()
    else:
        reference_file_data = reference_file.read().decode('utf-8')

    return (reference_file, reference_file_data)


def _get_datasize(reference_file_data):

    tmp_sio = None
    data_size = 0

    if PY2:
        from StringIO import StringIO

        tmp_sio = StringIO(reference_file_data)
        data_size = tmp_sio.len
    else:
        from io import StringIO

        tmp_sio = StringIO()
        data_size = tmp_sio.write(reference_file_data)
    tmp_sio.close()

    return data_size
