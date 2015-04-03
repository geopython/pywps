"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from pywps.exceptions import InvalidParameterValue, \
    MissingParameterValue, NoApplicableCode, \
    OperationNotSupported, VersionNegotiationFailed
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
    # 'gml': "http://www.opengis.net/gml",
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
        # TODO: Empty attributes should not be displayed
        f = Format(self.mime_type)
        return WPS.Output(
            WPS.Reference(href=self.url,
                          mimeType=f.mime_type,
                          encoding=f.encoding,
                          schema=f.schema
                          )
        )



class Format(FormatBase):
    """
    :param mime_type: MIME type allowed for a complex input.
    :param encoding: The encoding of this input or requested for this output
            (e.g., UTF-8).
    """

    def __init__(self, mime_type, encoding='UTF-8', schema=None):
        FormatBase.__init__(self, mime_type, schema, encoding)

    def describe_xml(self):
        doc = E.Format(
            E.MimeType(self.mime_type)
        )

        if self.encoding:
            doc.append(E.Encoding(self.encoding))

        if self.schema:
            doc.append(E.Schema(self.schema))

        return doc


class UOM(object):
    """
    :param uom: unit of measure
    """

    def __init__(self, uom=''):
        self.uom = uom

    def describe_xml(self):
        return OWS.UOM(
            self.uom
        )


class WPSRequest(object):
    def __init__(self, http_request):
        self.http_request = http_request

        if http_request.method == 'GET':
            # service shall be WPS
            service = self._get_get_param('service', aslist=False)
            if service:
                if str(service).lower() != 'wps':
                    raise OperationNotSupported(
                        'parameter SERVICE [%s] not supported' % service)
            else:
                raise MissingParameterValue('service', 'service')

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
                self.version = self._get_get_param('version')
                if not self.version:
                    raise MissingParameterValue('Missing version', 'version')
                if self.version != '1.0.0':
                    raise VersionNegotiationFailed('The requested version "%s" is not supported by this server' % self.version, 'version')

                self.identifiers = self._get_get_param('identifier',
                                                       aslist=True)

            elif self.operation == 'execute':
                self.identifier = self._get_get_param('identifier')
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
        output_elements = []
        for identifier in self.outputs:
            output = self.outputs[identifier]
            output_elements.append(output.execute_xml())

        doc = WPS.ExecuteResponse(
            WPS.Status(
                WPS.ProcessSucceeded("great success")
            ),
            WPS.ProcessOutputs(*output_elements)
        )
        return xml_response(doc)


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
        doc = E.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        doc.attrib['minOccurs'] = self.min_occurs
        doc.attrib['maxOccurs'] = self.max_occurs

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        if self.metadata:
            doc.append(OWS.Metadata(*self.metadata))

        literal_data_doc = E.LiteralData()

        if self.data_type:
            literal_data_doc.append(OWS.DataType(self.data_type, reference=xmlschema_2 + self.data_type))

        if self.uom:
            default_uom_element = self.uom[0].describe_xml()
            supported_uom_elements = [u.describe_xml() for u in self.uom]

            literal_data_doc.append(
                E.UOMs(
                    E.Default(default_uom_element),
                    E.Supported(*supported_uom_elements)
                )
            )

        doc.append(literal_data_doc)

        # TODO: refer to table 29 and 30
        doc.append(OWS.AnyValue())

        if self.default:
            doc.append(E.DefaultValue(self.default))

        return doc


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

        doc = E.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        doc.attrib['minOccurs'] = self.min_occurs
        doc.attrib['maxOccurs'] = self.max_occurs

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        if self.metadata:
            doc.append(OWS.Metadata(*self.metadata))

        doc.append(
            E.ComplexData(
                E.Default(default_format_el),
                E.Supported(*supported_format_elements)
            )
        )

        if self.max_megabytes:
            doc.attrib['maximumMegabytes'] = self.max_megabytes

        return doc


class LiteralOutput(inout.LiteralOutput):
    """
    :param identifier: The name of this output.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    :param value: Resulting value
            Should be :class:`~String` object.
    """

    def __init__(self, identifier, title, data_type=None, abstract='', metadata=[], uom=[]):
        inout.LiteralOutput.__init__(self, identifier, data_type=data_type)
        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.uom = uom
        self._value = None

    @property
    def value(self):
        """Get resulting value
        :rtype: String
        """

        return self._value

    @value.setter
    def value(self, value):
        """Set resulting value
        """

        self._value = value

    def describe_xml(self):
        doc = E.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata(m))

        literal_data_doc = E.LiteralData()

        if self.data_type:
            literal_data_doc.append(OWS.DataType(self.data_type, reference=xmlschema_2 + self.data_type))

        if self.uom:
            default_uom_element = self.uom[0].describe_xml()
            supported_uom_elements = [u.describe_xml() for u in self.uom]

            literal_data_doc.append(
                E.UOMs(
                    E.Default(default_uom_element),
                    E.Supported(*supported_uom_elements)
                )
            )

        return doc

    def execute_xml(self):
        return WPS.Output(
            OWS.Identifier(self.identifier),
            WPS.Data(WPS.LiteralData(
                self.getvalue(),
                dataType=self.data_type,
                reference=xmlschema_2 + self.data_type
            )
            )
        )


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

    def __init__(self, identifier, title, formats, output_format=None, encoding="UTF-8",
                 schema=None, abstract='', metadata=[], max_megabytes=None):
        inout.ComplexOutput.__init__(self, identifier)
        self.formats = formats
        self.title = title
        self.formats = formats
        self.abstract = abstract
        self.metadata = metadata
        self.max_megabytes = max_megabytes

        self._schema = None
        self._output_format = None
        self._encoding = None

        self.as_reference = False
        self.output_format = output_format
        self.encoding = encoding
        self.schema = schema

        # TODO: if not set then set to default max size
        if max_megabytes:
            self.max_fileSize = max_megabytes * 1024 * 1024

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
    def encoding(self):
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

        doc = E.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata(*self.metadata))

        doc.append(
            E.ComplexOutput(
                E.Default(default_format_el),
                E.Supported(*supported_format_elements)
            )
        )

        if self.max_megabytes:
            doc.attrib['maximumMegabytes'] = self.max_megabytes

        return doc

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

    def __init__(self, handler, identifier=None, title='', abstract='', profile=[], wsdl='', metadata=[], inputs=[],
                 outputs=[], store_supported=False, status_supported=False):
        self.identifier = identifier or handler.__name__
        self.handler = handler
        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.profile = profile
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
        return WPS.Process(OWS.Identifier(self.identifier))

    def describe_xml(self):
        input_elements = [i.describe_xml() for i in self.inputs]
        output_elements = [i.describe_xml() for i in self.outputs]

        doc = E.ProcessDescription(
            {'{http://www.opengis.net/wps/1.0.0}processVersion': "None"},
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        # TODO: include if storage of outputs or execute response document is supported
        doc.attrib['storeSupported'] = self.store_supported

        # TODO: include if updating of status data is supported
        doc.attrib['statusSupported'] = self.status_supported

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata({'{http://www.w3.org/1999/xlink}title': m}))

        for p in self.profile:
            doc.append(WPS.Profile(p))

        if self.wsdl:
            doc.append(WPS.WSDL({'{http://www.w3.org/1999/xlink}href': self.wsdl}))

        if input_elements:
            doc.append(E.DataInputs(*input_elements))

        doc.append(E.ProcessOutputs(*output_elements))

        return doc

    def execute(self, wps_request):
        wps_response = WPSResponse({o.identifier: o for o in self.outputs})
        wps_response = self.handler(wps_request, wps_response)

        output_elements = [wps_response.outputs[o].execute_xml() for o in wps_response.outputs]

        doc = []
        doc.extend((
            WPS.Process(OWS.Identifier(self.identifier)),
            WPS.Status(WPS.ProcessSucceeded("great success")),
            WPS.ProcessOutputs(*output_elements)
        ))
        
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

        doc = WPS.Capabilities(
            OWS.ServiceIdentification(
                OWS.Title('PyWPS Server')
            ),
            WPS.ProcessOfferings(*process_elements)
        )

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
        # check if process is valid
        try:
            process = self.processes[identifier]
        except KeyError:
            raise BadRequest("Unknown process %r" % identifier)
        
        # check if datainputs is required and has been passed
        if process.inputs:
            if wps_request.inputs is None:
                raise MissingParameterValue('', 'datainputs')
        
        # check if all mandatory inputs are passed
        for inpt in process.inputs:
            if inpt.identifier not in wps_request.inputs:
                raise MissingParameterValue('', inpt.identifier)
        
        # catch error generated by process code
        try:
            doc = WPS.ExecuteResponse(*process.execute(wps_request))
        except Exception as e:
            raise NoApplicableCode(e)
        
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
