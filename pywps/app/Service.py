import tempfile
from werkzeug.exceptions import BadRequest, HTTPException
from werkzeug.wrappers import Request, Response
from pywps import WPS, OWS
from pywps.inout import Format
from pywps._compat import PY2
from pywps.app.basic import xml_response
from pywps.app.WPSRequest import WPSRequest
import pywps.configuration as config
from pywps.exceptions import MissingParameterValue, NoApplicableCode, InvalidParameterValue, FileSizeExceeded, \
    StorageNotSupported
from pywps.inout.inputs import ComplexInput, LiteralInput, BoundingBoxInput

from collections import deque
import shutil
import os


class Service(object):
    """ The top-level object that represents a WPS service. It's a WSGI
    application.

    :param processes: A list of :class:`~Process` objects that are
                      provided by this service.
    """

    def __init__(self, processes=[]):
        self.processes = {p.identifier: p for p in processes}

    def get_capabilities(self):
        process_elements = [p.capabilities_xml()
                            for p in self.processes.values()]

        doc = WPS.Capabilities()

        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-CA'
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = 'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'
        # TODO: check Table 7 in OGC 05-007r7
        doc.attrib['updateSequence'] = '1'

        # Service Identification
        service_ident_doc = OWS.ServiceIdentification(
            OWS.Title(config.get_config_value('wps', 'title'))
        )

        if config.get_config_value('wps', 'abstract'):
            service_ident_doc.append(OWS.Abstract(config.get_config_value('wps', 'abstract')))

        if config.get_config_value('wps', 'keywords'):
            keywords_doc = OWS.Keywords()
            for k in config.get_config_value('wps', 'keywords').split(','):
                if k:
                    keywords_doc.append(OWS.Keyword(k))
            service_ident_doc.append(keywords_doc)

        service_ident_doc.append(OWS.ServiceType('WPS'))

        for v in config.get_config_value('wps', 'version').split(','):
            service_ident_doc.append(OWS.ServiceTypeVersion(v))

        service_ident_doc.append(OWS.Fees(config.get_config_value('wps', 'fees')))

        for con in config.get_config_value('wps', 'constraints').split(','):
            service_ident_doc.append(OWS.AccessConstraints(con))

        if config.get_config_value('wps', 'profile'):
            service_ident_doc.append(OWS.Profile(config.get_config_value('wps', 'profile')))

        doc.append(service_ident_doc)

        # Service Provider
        service_prov_doc = OWS.ServiceProvider(OWS.ProviderName(config.get_config_value('provider', 'providerName')))

        if config.get_config_value('provider', 'providerSite'):
            service_prov_doc.append(OWS.ProviderSite(
                {'{http://www.w3.org/1999/xlink}href': config.get_config_value('provider', 'providerSite')})
            )

        # Service Contact
        service_contact_doc = OWS.ServiceContact()

        # Add Contact information only if a name is set
        if config.get_config_value('provider', 'individualName'):
            service_contact_doc.append(OWS.IndividualName(config.get_config_value('provider', 'individualName')))
            if config.get_config_value('provider', 'positionName'):
                service_contact_doc.append(OWS.PositionName(config.get_config_value('provider', 'positionName')))

            contact_info_doc = OWS.ContactInfo()

            phone_doc = OWS.Phone()
            if config.get_config_value('provider', 'phoneVoice'):
                phone_doc.append(OWS.Voice(config.get_config_value('provider', 'phoneVoice')))
            if config.get_config_value('provider', 'phoneFacsimile'):
                phone_doc.append(OWS.Facsimile(config.get_config_value('provider', 'phoneFacsimile')))
            # Add Phone if not empty
            if len(phone_doc):
                contact_info_doc.append(phone_doc)

            address_doc = OWS.Address()
            if config.get_config_value('provider', 'deliveryPoint'):
                address_doc.append(OWS.DeliveryPoint(config.get_config_value('provider', 'deliveryPoint')))
            if config.get_config_value('provider', 'city'):
                address_doc.append(OWS.City(config.get_config_value('provider', 'city')))
            if config.get_config_value('provider', 'postalCode'):
                address_doc.append(OWS.PostalCode(config.get_config_value('provider', 'postalCode')))
            if config.get_config_value('provider', 'country'):
                address_doc.append(OWS.Country(config.get_config_value('provider', 'country')))
            if config.get_config_value('provider', 'electronicalMailAddress'):
                address_doc.append(
                    OWS.ElectronicMailAddress(config.get_config_value('provider', 'electronicalMailAddress'))
                )
            # Add Address if not empty
            if len(address_doc):
                contact_info_doc.append(address_doc)

            if config.get_config_value('provider', 'onlineResource'):
                contact_info_doc.append(OWS.OnlineResource(
                    {'{http://www.w3.org/1999/xlink}href': config.get_config_value('provider', 'onlineResource')})
                )
            if config.get_config_value('provider', 'hoursOfService'):
                contact_info_doc.append(OWS.HoursOfService(config.get_config_value('provider', 'hoursOfService')))
            if config.get_config_value('provider', 'contactInstructions'):
                contact_info_doc.append(OWS.ContactInstructions(config.get_config_value('provider', 'contactInstructions')))

            # Add Contact information if not empty
            if len(contact_info_doc):
                service_contact_doc.append(contact_info_doc)

            if config.get_config_value('provider', 'role'):
                service_contact_doc.append(OWS.Role(config.get_config_value('provider', 'role')))

        # Add Service Contact only if ProviderName and PositionName are set
        if len(service_contact_doc):
            service_prov_doc.append(service_contact_doc)

        doc.append(service_prov_doc)

        # Operations Metadata
        operations_metadata_doc = OWS.OperationsMetadata(
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get({'{http://www.w3.org/1999/xlink}href': '%s:%s%s' % (
                            config.get_config_value('wps', 'serveraddress'),
                            config.get_config_value('wps', 'serverport'),
                            '/wps?'
                        )}),
                        OWS.Post({'{http://www.w3.org/1999/xlink}href': '%s:%s%s' % (
                            config.get_config_value('wps', 'serveraddress'),
                            config.get_config_value('wps', 'serverport'),
                            '/wps'
                        )})
                    )
                ),
                name="GetCapabilities"
            ),
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get({'{http://www.w3.org/1999/xlink}href': '%s:%s%s' % (
                            config.get_config_value('wps', 'serveraddress'),
                            config.get_config_value('wps', 'serverport'),
                            '/wps?'
                        )}),
                        OWS.Post({'{http://www.w3.org/1999/xlink}href': '%s:%s%s' % (
                            config.get_config_value('wps', 'serveraddress'),
                            config.get_config_value('wps', 'serverport'),
                            '/wps'
                        )})
                    )
                ),
                name="DescribeProcess"
            ),
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get({'{http://www.w3.org/1999/xlink}href': '%s:%s%s' % (
                            config.get_config_value('wps', 'serveraddress'),
                            config.get_config_value('wps', 'serverport'),
                            '/wps?'
                        )}),
                        OWS.Post({'{http://www.w3.org/1999/xlink}href': '%s:%s%s' % (
                            config.get_config_value('wps', 'serveraddress'),
                            config.get_config_value('wps', 'serverport'),
                            '/wps'
                        )})
                    )
                ),
                name="Execute"
            )
        )
        doc.append(operations_metadata_doc)

        doc.append(WPS.ProcessOfferings(*process_elements))

        languages = config.get_config_value('wps', 'lang').split(',')
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

        doc.append(WPS.WSDL({'{http://www.w3.org/1999/xlink}href':  '%s:%s%s' % (
            config.get_config_value('wps', 'serveraddress'),
            config.get_config_value('wps', 'serverport'),
            '/wps?WSDL')
        }))

        return xml_response(doc)

    def describe(self, identifiers):
        if not identifiers:
            raise MissingParameterValue('', 'identifier')
        
        identifier_elements = []
        # 'all' keyword means all processes
        if 'all' in (ident.lower() for ident in identifiers):
            for process in self.processes:
                try:
                    identifier_elements.append(self.processes[process].describe_xml())
                except Exception as e:
                    raise NoApplicableCode(e)
        else:
            for identifier in identifiers:
                try:
                    process = self.processes[identifier]
                except KeyError:
                    raise InvalidParameterValue("Unknown process %r" % identifier, "identifier")
                else:
                    try:
                        identifier_elements.append(process.describe_xml())
                    except Exception as e:
                        raise NoApplicableCode(e)

        doc = WPS.ProcessDescriptions(
            *identifier_elements
        )
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = 'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'
        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-CA'
        return xml_response(doc)

    def execute(self, identifier, wps_request):
        """Parse and perform Execute WPS request call

        :param identifier: process identifier string
        :param wps_request: pywps.WPSRequest structure with parsed inputs, still in memory
        """
        response = None
        try:
            process = self.processes[identifier]

            workdir = config.get_config_value('server', 'workdir')
            tempdir = tempfile.mkdtemp(prefix='pypws_process_', dir=workdir)
            process.set_workdir(tempdir)
        except KeyError:
            raise InvalidParameterValue("Unknown process '%r'" % identifier)

        olddir = os.path.abspath(os.curdir)
        try:
            os.chdir(process.workdir)
            response = self._parse_and_execute(process, wps_request)
        finally:
            os.chdir(olddir)
            shutil.rmtree(process.workdir)

        return response

    def _parse_and_execute(self, process, wps_request):
        """Parse and execute request
        """
        # check if datainputs is required and has been passed
        if process.inputs:
            if wps_request.inputs is None:
                raise MissingParameterValue('', 'datainputs')

        # check if all mandatory inputs have been passed
        data_inputs = {}
        for inpt in process.inputs:
            if inpt.identifier not in wps_request.inputs:
                if inpt.min_occurs > 0:
                    raise MissingParameterValue(inpt.identifier, inpt.identifier)
                else:
                    data_inputs[inpt.identifier] = inpt.clone()

            # Replace the dicts with the dict of Literal/Complex inputs
            # set the input to the type defined in the process
            if isinstance(inpt, ComplexInput):
                data_inputs[inpt.identifier] = self.create_complex_inputs(inpt,
                    wps_request.inputs[inpt.identifier])
            elif isinstance(inpt, LiteralInput):
                data_inputs[inpt.identifier] = self.create_literal_inputs(inpt,
                    wps_request.inputs[inpt.identifier])
            elif isinstance(inpt, BoundingBoxInput):
                data_inputs[inpt.identifier] = self.create_bbox_inputs(inpt,
                    wps_request.inputs[inpt.identifier])

        wps_request.inputs = data_inputs
        
        # set as_reference to True for all the outputs specified as reference
        # if the output is not required to be raw
        if not wps_request.raw:
            for wps_outpt in wps_request.outputs:

                is_reference = wps_request.outputs[wps_outpt].get('asReference', 'false')
                if is_reference.lower() == 'true':
                    # check if store is supported
                    if process.store_supported == 'false':
                        raise StorageNotSupported('The storage of data is not supported for this process.')

                    is_reference = True
                else:
                    is_reference = False

                for outpt in process.outputs:
                    if outpt.identifier == wps_outpt:
                        outpt.as_reference = is_reference

        # catch error generated by process code
        try:
            wps_response = process.execute(wps_request)
        except Exception as e:
            raise NoApplicableCode('Service error: %s' % e)

        # get the specified output as raw
        if wps_request.raw:
            for outpt in wps_request.outputs:
                for proc_outpt in process.outputs:
                    if outpt == proc_outpt.identifier:
                        return Response(proc_outpt.data)

            # if the specified identifier was not found raise error
            raise InvalidParameterValue('')

        return wps_response

    def _get_complex_input_handler(self, href):
        """Return function for parsing and storing complexdata
        :param href: href object yes or not
        """

        def href_handler(complexinput, datain):
            """<wps:Reference /> handler"""
            tmp_dir = config.get_config_value('server', 'workdir')
    
            # save the reference input in workdir
            tmp_file = tempfile.mkstemp(dir=complexinput.workdir)[1]
    
            try:
                (reference_file, reference_file_data) = _openurl(href)
                data_size = reference_file.headers.get('Content-Length', 0)
            except Exception as e:
                raise NoApplicableCode('File reference error: %s' % e)

            # if the response did not return a 'Content-Length' header then calculate the size
            if data_size == 0:
                data_size = _get_datasize(reference_file_data)

            # check if input file size was not exceeded
            complexinput.calculate_max_input_size()
            byte_size = complexinput.max_size * 1024 * 1024
            if int(data_size) > int(byte_size):
                raise FileSizeExceeded('File size for input exceeded.'
                                       ' Maximum allowed: %i megabytes' %\
                       complexinput.max_size, complexinput.get('identifier'))

            try:
                with open(tmp_file, 'w') as f:
                    f.write(reference_file_data)
                    f.close()
            except Exception as e:
                raise NoApplicableCode(e)
    
            complexinput.file = tmp_file
            complexinput.url = href
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
                    'Invalid mimeType value %s for input %s' %\
                    (inpt.get('mimeType'), source.identifier),
                    'mimeType') 

            data_input.method = inpt.get('method', 'GET')

            # get the referenced input otherwise get the value of the field
            href = inpt.get('href', None)

            complex_data_handler = self._get_complex_input_handler(href)
            complex_data_handler(data_input, inpt)

            outinputs.append(data_input)

        if len(outinputs) < source.min_occurs:
            raise MissingParameterValue(locator = source.identifier)
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
            raise MissingParameterValue(locator = source.identifier)

        return outinputs


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
            raise MissingParameterValue(locator = source.identifier)

        return outinputs


    @Request.application
    def __call__(self, http_request):
        try:
            wps_request = WPSRequest(http_request)
            if wps_request.operation == 'getcapabilities':
                return self.get_capabilities()

            elif wps_request.operation == 'describeprocess':
                return self.describe(wps_request.identifiers)

            elif wps_request.operation == 'execute':
                return self.execute(wps_request.identifier, wps_request)
            else:
                raise RuntimeError("Unknown operation %r"
                                   % wps_request.operation)

        except HTTPException as e:
            # transform HTTPException to OWS NoApplicableCode exception
            if not isinstance(e, NoApplicableCode):
                e = NoApplicableCode(e.description, code=e.code)
            return e


def _openurl(href):
    """use urllib to open given href
    """
    if PY2:
        import urllib2
        reference_file = urllib2.urlopen(href)
        reference_file_data = reference_file.read()
    else:
        from urllib.request import urlopen
        reference_file = urlopen(href)
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
