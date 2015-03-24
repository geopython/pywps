"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from pywps.exceptions import InvalidParameterValue, \
    MissingParameterValue, NoApplicableCode,\
    OperationNotSupported
from werkzeug.datastructures import MultiDict
import lxml.etree
from lxml.builder import ElementMaker
from pywps._compat import text_type, StringIO
from pywps import inout
from pywps.formats import FORMATS
from pywps.inout import FormatBase
from lxml.etree import SubElement
from lxml import etree

xmlschema_2 = "http://www.w3.org/TR/xmlschema-2/#"
LITERAL_DATA_TYPES = ['string', 'float', 'integer', 'boolean']

NAMESPACES = {
    'xlink': "http://www.w3.org/1999/xlink",
    'wps': "http://www.opengis.net/wps/1.0.0",
    'ows': "http://www.opengis.net/ows/1.1",
    #'gml': "http://www.opengis.net/gml",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

E = ElementMaker()
WPS = ElementMaker(namespace=NAMESPACES['wps'], nsmap=NAMESPACES)
OWS = ElementMaker(namespace=NAMESPACES['ows'], nsmap=NAMESPACES)


def xpath_ns(el, path):
    return el.xpath(path, namespaces=NAMESPACES)


def xml_response(doc):
    return Response(lxml.etree.tostring(doc, pretty_print=True),
                    content_type='text/xml')


def get_input_from_xml(doc):
    the_input = MultiDict()
    for input_el in xpath_ns(doc, '/wps:Execute/wps:DataInputs/wps:Input'):
        [identifier_el] = xpath_ns(input_el, './ows:Identifier')

        literal_data = xpath_ns(input_el, './wps:Data/wps:LiteralData')
        if literal_data:
            value_el = literal_data[0]
            the_input.update({identifier_el.text: text_type(value_el.text)})
            continue

        complex_data = xpath_ns(input_el, './wps:Data/wps:ComplexData')
        if complex_data:
            complex_data_el = complex_data[0]
            value_el = complex_data_el[0]
            tmp = StringIO(lxml.etree.tounicode(value_el))
            tmp.mime_type = complex_data_el.attrib.get('mimeType')
            the_input.update({identifier_el.text: tmp})
            continue

        # TODO bounding box data

    return the_input


class FileReference(object):
    """
    :param url: URL where the file can be downloaded by the client.
    :param mime_type: MIME type of the file.
    """

    def __init__(self, url, mime_type):
        self.url = url
        self.mime_type = mime_type

    def execute_xml(self):
        #TODO: Empty attributes should not be displayed
        f = Format(self.mime_type)
        doc = WPS.Reference(
            href=self.url,
            mimeType=f.mime_type,
            encoding=f.encoding,
            schema=f.schema
        )
        return doc

class WPSRequest(object):
    def __init__(self, http_request):
        self.http_request = http_request

        if http_request.method == 'GET':
            # service shall be WPS
            service = self._get_get_param('service',
                                            aslist=False)
            if service:
                if str(service).lower() != 'wps':
                    raise OperationNotSupported(
                        'parameter SERVICE [%s] not supported' % service)
            else:
                raise MissingParameterValue('service','service')

            # operation shall be one of GetCapabilities, DescribeProcess,
            # Execute
            self.operation = self._get_get_param('request',
                                                 aslist=False)

            if not self.operation:
                raise MissingParameterValue('Missing request value', 'request')
            else:
                self.operation = self.operation.lower()

            if self.operation == 'getcapabilities':
                pass

            elif self.operation == 'describeprocess':
                self.identifiers = self._get_get_param('identifier',
                                                       aslist=True)

            elif self.operation == 'execute':
                self.identifier = self._get_get_param('identifier')
                self.lineage = self._get_get_param('lineage')
                if not self.lineage:
                    self.lineage = ''
                self.inputs = self._get_input_from_kvp(
                    self._get_get_param('datainputs'))

            else:
                raise InvalidParameterValue('Unknown request %r' % self.operation, 'request')

        elif http_request.method == 'POST':
            doc = lxml.etree.fromstring(http_request.get_data())

            if doc.tag == WPS.GetCapabilities().tag:
                self.operation = 'getcapabilities'

            elif doc.tag == WPS.DescribeProcess().tag:
                self.operation = 'describeprocess'
                self.identifiers = [identifier_el.text for identifier_el in
                                    xpath_ns(doc, './ows:Identifier')]

            elif doc.tag == WPS.Execute().tag:
                self.operation = 'execute'
                self.identifier = xpath_ns(doc, './ows:Identifier')[0].text
                self.inputs = get_input_from_xml(doc)

            else:
                raise InvalidParameterValue(doc.tag)

        else:
            raise MethodNotAllowed()

    def _get_get_param(self, key, aslist=False):
        """Returns value from the key:value pair, of the HTTP GET request, for
        example 'service' or 'request'

        :param key: key value you need to dig out of the HTTP GET request
        :param value: default value
        """
        
        key = key.lower()
        value = None
        for k in self.http_request.args.keys():
            if k.lower() == key:
                value = self.http_request.args.get(k)
                if aslist:
                    value = value.split(",")
        
        return value
    
    def _get_input_from_kvp(self, datainputs):
        """Get execute DataInputs from URL (key-value-pairs) encoding
        :param datainputs: key:value pair list of the datainputs parameter
        """
        
        inputs = {}
        
        if datainputs is None:
            return None
        
        for inpt in datainputs.split(";"):
            try:
                (identifier, val) = inpt.split("=")
                inputs[identifier] = val
            except:
                inputs[inpt] = ''

        return inputs


class WPSResponse(object):
    """
    :param outputs: A dictionary of output values that will be returned
                    to the client. The values can be strings or
                    :class:`~FileReference` objects.
    """

    def __init__(self, outputs=None):
        self.outputs = outputs or {}
        self.message = None

    @Request.application
    def __call__(self, request):
        doc = WPS.ExecuteResponse('WPSRESPONSE')
        return doc

class LiteralInput(inout.LiteralInput):
    """
    :param identifier: The name of this input.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    """

    def __init__(self, identifier, title, data_type=None, abstract='', metadata=[], uom=[], default='',
                 min_occurs='1', max_occurs='1'):
        inout.LiteralInput.__init__(self, identifier=identifier, data_type=data_type)
        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.uom = uom
        self.default = default
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs

    def describe_xml(self):
        return E.Input(
            OWS.Identifier(self.identifier),
            E.LiteralData(
                OWS.DataType(
                    self.data_type,
                    reference=xmlschema_2 + self.data_type)
            )
        )

    def execute_xml(self):
        """Render Execute response XML node

        :return: node
        :rtype: ElementMaker
        """
        # TODO: check for optional tags and attributes
        node = None
        # TODO: check asReference==true
        if False:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        return WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title),
            OWS.Abstract(self.abstract),
            node
        )

    def _execute_xml_reference(self):
        """Return Reference node
        """
        # TODO: literalinput reference
        url = 'bla'
        doc = WPS.Reference()
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = url
        doc.attrib['method'] = 'GET'
        return doc

    def _execute_xml_data(self):
        return WPS.Data(WPS.LiteralData(
            self.data,
            data_type=self.data_type,
            uom='n/a'
            )
        )


class ComplexInput(inout.ComplexInput):
    """
    :param identifier: The name of this input.
    :param formats: Allowed formats for this input. Should be a list of
                    one or more :class:`~Format` objects.
    """

    def __init__(self, identifier, title, formats, abstract='', metadata=[], min_occurs='1',
                 max_occurs='1', max_megabytes=None):
        inout.ComplexInput.__init__(self, identifier)
        self.formats = formats
        self.title = title
        self.formats = formats
        self.abstract = abstract
        self.metadata = metadata
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.max_megabytes = max_megabytes

        # TODO: if not set then set to default max size
        if max_megabytes:
            self.max_fileSize = max_megabytes * 1024 * 1024

    def describe_xml(self):
        default_format_el = self.formats[0].describe_xml()
        supported_format_elements = [f.describe_xml() for f in self.formats]
        return E.Input(
            OWS.Identifier(self.identifier),
            E.ComplexData(
                E.Default(default_format_el),
                E.Supported(*supported_format_elements)
            )
        )

    def execute_xml(self):
        """Render Execute response XML node

        :return: node
        :rtype: ElementMaker
        """
        # TODO: check for optional tags and attributes
        node = None
        # TODO: check asReference==true
        if True:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        return WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title),
            OWS.Abstract(self.abstract),
            node
        )

    def _execute_xml_reference(self):
        """Return Reference node
        """
        doc = WPS.Reference()
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.stream
        # TODO: check if method was GET or POST
        doc.attrib['method'] = 'GET'
        return doc

    def _execute_xml_data(self):
        # TODO: complexinput data
        return WPS.Data(WPS.LiteralData(
            self.data,
            data_type=self.data_type,
            uom='n/a'
            )
        )

class LiteralOutput(inout.LiteralOutput):
    """
    :param identifier: The name of this output.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    :param value: Resulting value
            Should be :class:`~String` object.
    """

    def __init__(self, identifier, title, data_type='string', abstract='', metadata=[], uom=[]):
        inout.LiteralOutput.__init__(self, identifier, data_type=data_type)
        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.uom = uom
        self._value = None

    @property
    def value(self):
        """Get resulting value
        :rtype: Stringvalue
        """

        return self._value

    @value.setter
    def value(self, value):
        """Set resulting value
        """

        self._value = value

    def describe_xml(self):
        return WPS.Output(
            OWS.Identifier(self.identifier),
            WPS.LiteralData(OWS.DataType(self.data_type, reference=xmlschema_2 + self.data_type))
        )

    def execute_xml(self):
        doc = WPS.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        data_doc = WPS.Data()

        literal_data_doc = WPS.LiteralData(self.value)
        literal_data_doc.attrib['dataType'] = self.data_type
        literal_data_doc.attrib['reference'] = xmlschema_2 + self.data_type
        if self.uom:
            default_uom_element = self.uom[0].describe_xml()
            supported_uom_elements = [u.describe_xml() for u in self.uom]

            literal_data_doc.append(
                E.UOMs(
                    E.Default(default_uom_element),
                    E.Supported(*supported_uom_elements)
                )
            )
        data_doc.append(literal_data_doc)

        doc.append(data_doc)

        return doc


class ComplexOutput(inout.ComplexOutput):
    """
    :param identifier: The name of this output.
    :param formats: Possible output formats for this output.
            Should be list of :class:`~Format` object.
    :param output_format: Required format for this output.
            Should be :class:`~Format` object.
    :param encoding: The encoding of this input or requested for this output
            (e.g., UTF-8).
    """

    def __init__(self, identifier, formats, output_format=None,
                 encoding="UTF-8", schema=None):
        inout.ComplexOutput.__init__(self, identifier)

        self.identifier = identifier
        self.formats = formats

        self._schema = None
        self._output_format = None
        self._encoding = None

        self.as_reference = False
        self.output_format = output_format
        self.encoding = encoding
        self.schema = schema

    @property
    def output_format(self):
        """Get output format
        :rtype: String
        """

        if self._output_format:
            return self._output_format
        else:
            return ''

    @output_format.setter
    def output_format(self, output_format):
        """Set output format
        """
        self._output_format = output_format

    @property
    def encoding(self ):
        """Get output encoding
        :rtype: String
        """

        if self._encoding:
            return self._encoding
        else:
            return ''

    @encoding.setter
    def encoding(self, encoding):
        """Set output encoding
        """
        self._encoding = encoding

    @property
    def schema(self):
        """Get output schema
        :rtype: String
        """

        return self._schema

    @schema.setter
    def schema(self, schema):
        """Set output schema
        """
        self._schema = schema

    def describe_xml(self):
        default_format_el = self.formats[0].describe_xml()
        supported_format_elements = [f.describe_xml() for f in self.formats]
        return WPS.Output(
            OWS.Identifier(self.identifier),
            E.ComplexOutput(
                E.Default(default_format_el),
                E.Supported(*supported_format_elements)
            )
        )

    def execute_xml(self):
        """Render Execute response XML node

        :return: node
        :rtype: ElementMaker
        """

        node = None
        if self.as_reference == True:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        return WPS.Output(
            OWS.Identifier(self.identifier),
            WPS.Data(node)
        )

    def _execute_xml_reference(self):
        """Return Reference node
        """
        (store_type, path, url) = self.storage.store(self)

    def _execute_xml_data(self):
        return WPS.ComplexData(
                self.get_stream().read(),
                mimeType=self.output_format,
                encoding=self.encoding,
                schema=self.schema
        )

class BoundingBoxOutput(object):
    """bounding box output
    """
    # TODO
    pass


class Format(FormatBase):
    """
    :param mime_type: MIME type allowed for a complex input.
    :param encoding: The encoding of this input or requested for this output
            (e.g., UTF-8).
    """    

    def __init__(self, mime_type, encoding='UTF-8', schema=None):
        FormatBase.__init__(self, mime_type, schema, encoding)

    def describe_xml(self):
        return E.Format(
            OWS.MimeType(self.mime_type) # Zero or one (optional)
        )


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

    def __init__(self, handler, identifier=None, title='', abstract='', profile=[], wsdl='', metadata=[], version='',
                 inputs=[], outputs=[], store_supported=False, status_supported=False):
        self.identifier = identifier or handler.__name__
        self.handler = handler
        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.profile = profile
        self.version = version
        self.wsdl = wsdl
        self.inputs = inputs
        self.outputs = outputs

        if store_supported:
            self.store_supported = 'true'
        else:
            self.store_supported = 'false'

        if status_supported:
            self.status_supported = 'true'
        else:
            self.status_supported = 'false'

    def capabilities_xml(self):
        return WPS.Process(
            # TODO: replace None with the actual provided version
            {'{http://www.opengis.net/wps/1.0.0}processVersion': "None"}, # Zero or one (optional)
            OWS.Identifier(self.identifier),
            OWS.Title('None'),
            OWS.Abstract('None') # Zero or one (optional)
            # OWS.Metadata Zero or one (optional)
            # OWS.Profile Zero or one (optional)
            # OWS.WSDL Zero or one (optional)
        )

    def describe_xml(self):
        input_elements = [i.describe_xml() for i in self.inputs]
        output_elements = [i.describe_xml() for i in self.outputs]
        return E.ProcessDescription(
            OWS.Identifier(self.identifier),
            E.DataInputs(*input_elements),
            E.DataOutputs(*output_elements)
        )

    def execute(self, wps_request):
        wps_response = WPSResponse({o.identifier: o for o in self.outputs})
        wps_response = self.handler(wps_request, wps_response) 

        doc = WPS.ExecuteResponse()

        # Process XML
        process_doc = WPS.Process(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        # TODO: See Table 32 Metadata in OGC 06-121r3
        for m in self.metadata:
            doc.append(OWS.Metadata(m))
        if self.profile:
            doc.append(OWS.Profile(self.profile))
        if self.wsdl:
            doc.append(OWS.WSDL(self.wsdl))
        if self.version:
            process_doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = self.version
        doc.append(process_doc)

        # Status XML
        status_doc = WPS.Status(WPS.ProcessSucceeded("great success"))
        doc.append(status_doc)

        # DataInputs XML if lineage=true
        if wps_request.lineage.lower() == 'true':
            data_inputs = [i.execute_xml() for i in self.inputs]
            datainputs_doc = WPS.DataInputs(*data_inputs)
            doc.append(datainputs_doc)

        # DataOutput definition XML if lineage=true
        if wps_request.lineage.lower() == 'true':
            output_definitions = [i.describe_xml() for i in self.outputs]
            dataoutputs_doc = WPS.OutputDefinitions(*output_definitions)
            doc.append(dataoutputs_doc)

        # Process outputs XML
        output_elements = [wps_response.outputs[o].execute_xml() for o in wps_response.outputs]
        process_output_doc = WPS.ProcessOutputs(*output_elements)
        doc.append(process_output_doc)

        import config
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = 'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'
        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-CA'
        doc.attrib['serviceInstance'] = config.get_config_value('wps', 'serveraddress') + '?service=wps&request=getcapabilities'
        # TODO: get the location of the status file for the process
        doc.attrib['statusLocation'] = 'localhost/foo.xml'
        
        return doc


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

        # TODO: retrieve information and put it here
        doc = WPS.Capabilities(
            {'{http://www.w3.org/XML/1998/namespace}lang': 'en-CA'},
            {'{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd'},
            OWS.ServiceIdentification(
                OWS.Title('PyWPS 4 Server'), # one or more
                OWS.Abstract('See http://www.opengeospatial.org/standards/wps and https://github.com/jachym/pywps-4'), # Zero or one (optional)
                OWS.Keywords( # Zero or one (optional)
                    OWS.Keyword('GRASS'),
                    OWS.Keyword('GIS'),
                    OWS.Keyword('WPS')
                ),
                OWS.ServiceType('WPS'),
                OWS.ServiceTypeVersion('1.0.0'), # one or more
                OWS.Fees('None'), # Zero or one (optional)
                OWS.AccessConstraints('none') # Zero or one (optional)
                # OWS.Profile Zero or one (optional)
            ),
            OWS.ServiceProvider(
                OWS.ProviderName('Your Company Name'),
                OWS.ProviderSite({'{http://www.w3.org/1999/xlink}href': "http://foo.bar"}), # Zero or one (optional)
                OWS.ServiceContact( # Zero or one (optional)
                    OWS.IndividualName('Your Name'),
                    OWS.PositionName('Your Position'),
                    OWS.ContactInfo(
                        OWS.Address(
                            OWS.DeliveryPoint('Street'),
                            OWS.City('City'),
                            OWS.PostalCode('000 00'),
                            OWS.Country('eu'),
                            OWS.ElectronicMailAddress('login@server.org')
                        ),
                        OWS.OnlineResource({'{http://www.w3.org/1999/xlink}href': "http://foo.bar"}),
                        OWS.HoursOfService('0:00-24:00'),
                        OWS.ContactInstructions('none')
                    ),
                    OWS.Role('Your role')
                )
            ),
            OWS.OperationsMetadata(
                OWS.Operation( # one or more
                    OWS.DCP( # one or more
                        OWS.HTTP(
                            OWS.Get({'{http://www.w3.org/1999/xlink}href': "http://localhost:5000/wps?"}),
                            OWS.Post({'{http://www.w3.org/1999/xlink}href': "http://localhost:5000/wps"}),
                        )
                    ),
                    name="GetCapabilities"
                    # paramenter Zero or one (optional)
                    # constraint Zero or one (optional)
                    # metadata Zero or one (optional)
                ),
                OWS.Operation(
                    OWS.DCP(
                        OWS.HTTP(
                            OWS.Get({'{http://www.w3.org/1999/xlink}href': "http://localhost:5000/wps?"}),
                            OWS.Post({'{http://www.w3.org/1999/xlink}href': "http://localhost:5000/wps"}),
                        )
                    ),
                    name="DescribeProcess"
                ),
                OWS.Operation(
                    OWS.DCP(
                        OWS.HTTP(
                            OWS.Get({'{http://www.w3.org/1999/xlink}href': "http://localhost:5000/wps?"}),
                            OWS.Post({'{http://www.w3.org/1999/xlink}href': "http://localhost:5000/wps"}),
                        )
                    ),
                    name="Execute"
                )
                # OWS.Parameter Zero or one (optional)
                # OWS.Constraint Zero or one (optional)
                # OWS.ExtendedCapabilities Zero or one (optional)
            ),
            WPS.ProcessOfferings(*process_elements),
            WPS.Languages(
                WPS.Default(
                    OWS.Language('en-CA')
                ),
                WPS.Supported(
                    OWS.Language('en-CA')
                )
            ),
            WPS.WSDL({'{http://www.w3.org/1999/xlink}href': "http://localhost:5000/wps?WSDL"}), # Zero or one (optional)
            service="WPS",
            version="1.0.0",
            updateSequence="1" # Zero or one (optional)
        )    

        return xml_response(doc)

    def describe(self, identifiers):
        if not identifiers:
            raise MissingParameterValue('', 'identifier')
        
        identifier_elements = []
        # 'all' keyword means all processes
        if 'all' in (ident.lower() for ident in identifiers):
            for process in self.processes:
                identifier_elements.append(self.processes[process].describe_xml())
        else:
            for identifier in identifiers:
                try:
                    process = self.processes[identifier]
                except KeyError:
                    raise InvalidParameterValue("Unknown process %r" % identifier, "identifier")
                else:
                    identifier_elements.append(process.describe_xml())
        doc = WPS.ProcessDescriptions(*identifier_elements)
        return xml_response(doc)

    def execute(self, identifier, wps_request):
        # check if process is valid
        try:
            process = self.processes[identifier]
        except KeyError:
            raise BadRequest("Unknown process %r" % identifier)
        
        # check if datainputs is required and has been passed
        if process.inputs:
            if wps_request.inputs is None:
                raise MissingParameterValue('', 'datainputs')
        
        # check if all mandatory inputs have been passed and set process inputs to the passed values
        for inpt in process.inputs:
            if inpt.identifier not in wps_request.inputs:
                raise MissingParameterValue('', inpt.identifier)
            for wps_identifier in wps_request.inputs:
                if inpt.identifier == wps_identifier:
                    # TODO: check if reference or data
                    inpt.set_stream(wps_request.inputs[wps_identifier])
                    break

            
        # catch error generated by process code
        #try:
            doc = process.execute(wps_request)
        #except Exception as e:
        #    raise NoApplicableCode(e)

        return xml_response(doc)

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
