"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""
import os
import config
from storage import FileStorage
from uuid import uuid4
import flask

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
import urllib2

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
    the_input = {}
    for input_el in xpath_ns(doc, '/wps:Execute/wps:DataInputs/wps:Input'):
        [identifier_el] = xpath_ns(input_el, './ows:Identifier')

        literal_data = xpath_ns(input_el, './wps:Data/wps:LiteralData')
        if literal_data:
            value_el = literal_data[0]
            inpt = {}
            inpt['data'] = text_type(value_el.text)
            inpt['uom'] = value_el.attrib.get('uom', '')
            inpt['datatype'] = value_el.attrib.get('datatype', '')
            the_input[identifier_el.text] = inpt
            continue

        complex_data = xpath_ns(input_el, './wps:Data/wps:ComplexData')
        if complex_data:
            complex_data_el = complex_data[0]
            value_el = complex_data_el[0]
            inpt = {}
            inpt['data'] = value_el
            inpt['mime_type'] = complex_data_el.attrib.get('mimeType', '')
            inpt['encoding'] = complex_data_el.attrib.get('encoding', '')
            inpt['schema'] = complex_data_el.attrib.get('schema', '')
            inpt['method'] = complex_data_el.attrib.get('method', 'GET')
            the_input[identifier_el.text] = inpt
            continue

        reference_data = xpath_ns(input_el, './wps:Reference')
        if reference_data:
            reference_data_el = reference_data[0]
            inpt = {}
            inpt[identifier_el.text] = reference_data_el.text
            inpt['href'] = reference_data_el.attrib.get('{http://www.w3.org/1999/xlink}href', '')
            inpt['mimeType'] = reference_data_el.attrib.get('mimeType', '')
            the_input[identifier_el.text] = inpt
            continue

        # TODO bounding box data

    return the_input





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
def get_resp_doc_from_xml(doc):
    the_output = {}
    for output_el in xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:ResponseDocument/wps:Output'):
        [identifier_el] = xpath_ns(output_el, './ows:Identifier')
        outpt = {}
        outpt[identifier_el.text] = ''
        outpt['asReference'] = output_el.attrib.get('asReference', 'false')
        the_output[identifier_el.text] = outpt

    return the_output


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
                self.version = self._get_get_param('version')
                if not self.version:
                    raise MissingParameterValue('Missing version', 'version')
                if self.version != '1.0.0':
                    raise VersionNegotiationFailed('The requested version "%s" is not supported by this server' % self.version, 'version')

                self.identifier = self._get_get_param('identifier')
                self.store_execute = self._get_get_param('storeExecuteResponse', 'false')
                self.lineage = self._get_get_param('lineage', 'false')
                self.outputs = self._get_data_from_kvp(
                    self._get_get_param('ResponseDocument'))
                self.inputs = self._get_data_from_kvp(
                    self._get_get_param('DataInputs'))

            else:
                raise InvalidParameterValue('Unknown request %r' % self.operation, 'request')

        elif http_request.method == 'POST':
            doc = lxml.etree.fromstring(http_request.get_data())

            if doc.tag == WPS.GetCapabilities().tag:
                self.operation = 'getcapabilities'

            elif doc.tag == WPS.DescribeProcess().tag:
                self.version = doc.attrib.get('version')
                if not self.version:
                    raise MissingParameterValue('Missing version', 'version')
                if self.version != '1.0.0':
                    raise VersionNegotiationFailed('The requested version "%s" is not supported by this server' % self.version, 'version')

                self.operation = 'describeprocess'
                self.identifiers = [identifier_el.text for identifier_el in
                                    xpath_ns(doc, './ows:Identifier')]

            elif doc.tag == WPS.Execute().tag:
                self.version = doc.attrib.get('version')
                if not self.version:
                    raise MissingParameterValue('Missing version', 'version')
                if self.version != '1.0.0':
                    raise VersionNegotiationFailed('The requested version "%s" is not supported by this server' % self.version, 'version')

                self.operation = 'execute'
                self.identifier = xpath_ns(doc, './ows:Identifier')[0].text
                self.inputs = get_input_from_xml(doc)
                self.outputs = get_resp_doc_from_xml(doc)
                response_document = xpath_ns(doc, './wps:ResponseForm/wps:ResponseDocument')
                if len(response_document) > 0:
                    self.lineage = response_document[0].attrib.get('lineage', 'false')
                    self.store_execute = response_document[0].attrib.get('storeExecute', 'false')
                else:
                    self.lineage = 'false'
                    self.store_execute = 'false'
            else:
                raise InvalidParameterValue(doc.tag)

        else:
            raise MethodNotAllowed()

    def _get_get_param(self, key, default=None, aslist=False):
        """Returns value from the key:value pair, of the HTTP GET request, for
        example 'service' or 'request'

        :param key: key value you need to dig out of the HTTP GET request
        """

        
        key = key.lower()
        value = default
        # http_request.args.keys will make + sign disappear in GET url if not urlencoded
        for k in self.http_request.args.keys():
            if k.lower() == key:
                value = self.http_request.args.get(k)
                if aslist:
                    value = value.split(",")
        
        return value

    def _get_data_from_kvp(self, data):
        """Get execute DataInputs and ResponseDocument from URL (key-value-pairs) encoding
        :param data: key:value pair list of the datainputs and responseDocument parameter
        """

        the_data = {}

        if data is None:
            return None
        
        for d in data.split(";"):
            try:
                io = {}
                fields = d.split('@')

                # First field is identifier and its value
                (identifier, val) = fields[0].split("=")
                io['value'] = val

                # Get the attributes of the data
                for attr in fields[1:]:
                    (attribute, attr_val) = attr.split('=')
                    io[attribute] = attr_val

                # Add the input/output with all its attributes and values to the dictionary
                the_data[identifier] = io
            except:
                the_data[d] = ''

        return the_data


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

    def __init__(self, identifier, title='', data_type='string', abstract='', metadata=[], uom=[], default='',
                 min_occurs='1', max_occurs='1', as_reference=False):
        inout.LiteralInput.__init__(self, identifier=identifier, title=title, abstract=abstract, data_type=data_type)
        self.metadata = metadata
        self.uom = uom
        self.default = default
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.as_reference = as_reference
        self._value = None

    def setvalue(self, value):
        self._value = value

    def getvalue(self):
        return self._value

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

    def execute_xml(self):
        """Render Execute response XML node

        :return: node
        :rtype: ElementMaker
        """
        node = None
        if self.as_reference:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        doc = WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        doc.append(node)

        return doc

    def _execute_xml_reference(self):
        """Return Reference node
        """
        doc = WPS.Reference()
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.stream
        if self.method.upper() == 'POST' or self.method.upper() == 'GET':
            doc.attrib['method'] = self.method.upper()
        return doc

    def _execute_xml_data(self):
        """Return Data node
        """
        doc = WPS.Data()
        literal_doc = WPS.LiteralData(self._value)

        if self.data_type:
            literal_doc.attrib['dataType'] = self.data_type
        if self.uom:
            literal_doc.attrib['uom'] = self.uom
        doc.append(literal_doc)
        return doc


class ComplexInput(inout.ComplexInput):
    """
    :param identifier: The name of this input.
    :param allowed_formats: Allowed formats for this input. Should be a list of
                    one or more :class:`~Format` objects.
    :param data_format: Format of the passed input. Should be :class:`~Format` object
    """

    def __init__(self, identifier, title='', allowed_formats=None, data_format=None, abstract='', metadata=[], min_occurs='1',
                 max_occurs='1', max_megabytes=None, as_reference=False):
        inout.ComplexInput.__init__(self, identifier=identifier, title=title, abstract=abstract, data_format=data_format)
        self.allowed_formats = allowed_formats
        self.metadata = metadata
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.max_megabytes = max_megabytes
        self.as_reference = as_reference
        self.method = ''

        # TODO: if not set then set to default max size
        if max_megabytes:
            self.max_fileSize = max_megabytes * 1024 * 1024

    def describe_xml(self):
        default_format_el = self.allowed_formats[0].describe_xml()
        supported_format_elements = [f.describe_xml() for f in self.allowed_formats]
        
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
    
    def execute_xml(self):
        """Render Execute response XML node


        :return: node
        :rtype: ElementMaker
        """
        node = None
        if self.as_reference:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        doc = WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        doc.append(node)

        return doc

    def _execute_xml_reference(self):
        """Return Reference node
        """
        doc = WPS.Reference()
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.stream.url
        if self.data_format:
            if self.data_format.mime_type:
                doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                doc.attrib['schema'] = self.data_format.schema
        if self.method.upper() == 'POST' or self.method.upper() == 'GET':
            doc.attrib['method'] = self.method.upper()
        return doc

    def _execute_xml_data(self):
        """Return Data node
        """
        doc = WPS.Data()
        complex_doc = WPS.ComplexData(self.data)

        if self.data_format:
            if self.data_format.mime_type:
                complex_doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                complex_doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                complex_doc.attrib['schema'] = self.data_format.schema
        doc.append(complex_doc)
        return doc

class LiteralOutput(inout.LiteralOutput):
    """
    :param identifier: The name of this output.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    :param value: Resulting value
            Should be :class:`~String` object.
    """

    def __init__(self, identifier, title='', data_type='string', abstract='', metadata=[], uom=[]):
        inout.LiteralOutput.__init__(self, identifier, title=title, data_type=data_type)
        self.abstract = abstract
        self.metadata = metadata
        self.uom = uom
        self._value = None

    def setvalue(self, value):
        self.value = value

    def getvalue(self):
        return self.value

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

    def __init__(self, identifier, title='', formats=None, output_format=None, encoding="UTF-8",
                 schema=None, abstract='', metadata=[], max_megabytes=None):
        inout.ComplexOutput.__init__(self, identifier, title=title, abstract=abstract)
        self.formats = formats
        self.metadata = metadata
        self.max_megabytes = max_megabytes

        self._schema = None
        self._output_format = None
        self._encoding = None

        self.as_reference = False
        self.output_format = output_format
        self.encoding = encoding
        self.schema = schema
        self._out_bytes = None
        self.storage = FileStorage(config)

        # TODO: if not set then set to default max size
        if max_megabytes:
            self.max_fileSize = max_megabytes * 1024 * 1024

    @property
    def out_bytes(self):
        """Get resulting bytes
        """

        return self._out_bytes

    @out_bytes.setter
    def out_bytes(self, out_bytes):
        """Set resulting bytes
        """

        self._out_bytes = out_bytes
        self.data = out_bytes

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
        if self.as_reference:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        doc = WPS.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        doc.append(node)

        return doc

    def _execute_xml_reference(self):
        """Return Reference node
        """
        doc = WPS.Reference()

        # get_url will create the file and return the url for it
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.get_url()

        if self.data_format:
            if self.data_format.mime_type:
                doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                doc.attrib['schema'] = self.data_format.schema
        return doc

    def _execute_xml_data(self):
        """Return Data node
        """
        doc = WPS.Data()

        complex_doc = WPS.ComplexData(self.data)

        if self.data_format:
            if self.data_format.mime_type:
                complex_doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                complex_doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                complex_doc.attrib['schema'] = self.data_format.schema
        doc.append(complex_doc)
        return doc


class BoundingBoxOutput(object):
    """bounding box output
    """
    # TODO: BoundingBoxOutput
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
                 outputs=[], version='None', lineage=False, store_supported=False, status_supported=False):
        self.identifier = identifier or handler.__name__
        self.handler = handler
        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.profile = profile
        self.wsdl = wsdl
        self.version = version
        self.inputs = inputs
        self.outputs = outputs
        self.status_location = ''

        if lineage:
            self.lineage = 'true'
        else:
            self.lineage = 'false'

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
        for m in self.metadata:
            doc.append(OWS.Metadata(m))
        if self.profile:
            doc.append(OWS.Profile(self.profile))
        if self.wsdl:
            doc.append(OWS.WSDL(self.wsdl))
        if self.version != 'None':
            doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = self.version

        return doc

    def describe_xml(self):
        input_elements = [i.describe_xml() for i in self.inputs]
        output_elements = [i.describe_xml() for i in self.outputs]

        doc = E.ProcessDescription(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = self.version

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
        process_doc.attrib['{http://www.opengis.net/wps/1.0.0}processVersion'] = self.version
        doc.append(process_doc)

        # Status XML
        status_doc = WPS.Status(WPS.ProcessSucceeded("great success"))
        doc.append(status_doc)

        # DataInputs XML if lineage=true
        if wps_request.lineage.lower() == 'true':
            data_inputs = [wps_request.inputs[i].execute_xml() for i in wps_request.inputs]
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

        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = 'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'
        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-CA'
        doc.attrib['serviceInstance'] = config.get_config_value('wps', 'serveraddress') + '/wps?service=wps&request=getcapabilities'

        # store the execute response document if true
        if wps_request.store_execute.lower() == 'true':
            file_path = config.get_config_value('server', 'outputPath')
            file_url = config.get_config_value('wps', 'serveraddress') + config.get_config_value('server', 'outputUrl')
            status_uuid = str(uuid4())
            status_file_path = os.path.join(file_path, status_uuid)+'.xml'
            status_file_url = os.path.join(file_url, status_uuid)+'.xml'

            doc.attrib['statusLocation'] = status_file_url

            file_obj = open(status_file_path, 'w')
            file_obj.write(etree.tostring(doc, pretty_print=True))
            file_obj.close()

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

        import config

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
            if config.get_config_value('provider', 'role'):
                service_contact_doc.append(OWS.Role(config.get_config_value('provider', 'role')))

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

        # Add Service Contact only if ProviderName and PositionName are set
        if len(service_contact_doc):
            service_prov_doc.append(service_contact_doc)

        doc.append(service_prov_doc)

        # Operations Metadata
        operations_metadata_doc = OWS.OperationsMetadata(
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get({'{http://www.w3.org/1999/xlink}href': config.get_config_value('wps', 'serveraddress')+'/wps?'}),
                        OWS.Post({'{http://www.w3.org/1999/xlink}href': config.get_config_value('wps', 'serveraddress')+'/wps'}),
                    )
                ),
                name="GetCapabilities"
            ),
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get({'{http://www.w3.org/1999/xlink}href': config.get_config_value('wps', 'serveraddress')+'/wps?'}),
                        OWS.Post({'{http://www.w3.org/1999/xlink}href': config.get_config_value('wps', 'serveraddress')+'/wps'}),
                    )
                ),
                name="DescribeProcess"
            ),
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get({'{http://www.w3.org/1999/xlink}href': config.get_config_value('wps', 'serveraddress')+'/wps?'}),
                        OWS.Post({'{http://www.w3.org/1999/xlink}href': config.get_config_value('wps', 'serveraddress')+'/wps'}),
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

        doc.append(WPS.WSDL({'{http://www.w3.org/1999/xlink}href': config.get_config_value('wps', 'serveraddress')+'/wps?WSDL'}))

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

        # check if all mandatory inputs have been passed
        request_inputs = {}
        for inpt in process.inputs:
            if inpt.identifier not in wps_request.inputs:
                raise MissingParameterValue('', inpt.identifier)

            # set process inputs to the passed values from GET/POST
            for wps_identifier in wps_request.inputs:
                if inpt.identifier == wps_identifier:
                    wps_attrs = wps_request.inputs[wps_identifier]

                    # set the input to the type defined in the process
                    if isinstance(inpt, ComplexInput):
                        data_input = ComplexInput(inpt.identifier, '', None)
                    else:
                        data_input = LiteralInput(inpt.identifier, '')

                    if isinstance(data_input, ComplexInput):
                        f = Format()
                        f.mime_type = wps_attrs.get('mime_type')
                        f.encoding = wps_attrs.get('encoding')
                        f.schema = wps_attrs.get('schema')
                        data_input.data_format = f
                        data_input.method = wps_attrs.get('method', 'GET')

                        # get the referenced input otherwise get the value of the field
                        is_reference = wps_attrs.get('href', None)
                        if is_reference:
                            data_input.stream = urllib2.urlopen(wps_attrs.get('href'))
                            data_input.as_reference = True
                        else:
                            data_input.data = wps_request.inputs[wps_identifier]['data']

                    elif isinstance(data_input, LiteralInput):
                        data_input.uom = wps_attrs.get('uom')
                        data_type = wps_attrs.get('datatype')
                        if data_type:
                            data_input.data_type = data_type

                        # get the value of the field
                        data_input.setvalue(wps_request.inputs[wps_identifier]['data'])

                    # add Literal/Complex input to the dict
                    request_inputs[wps_identifier] = data_input

            # Replace the dicts with the dict of Literal/Complex inputs
            wps_request.inputs = request_inputs

        # set all the specified outputs as reference if asReference=true
        for outpt in process.outputs:
            if wps_request.outputs is not None:
                for wps_identifier in wps_request.outputs:
                    if outpt.identifier == wps_identifier:
                        wps_attrs = wps_request.outputs[wps_identifier]

                        is_reference = wps_attrs.get('asReference', None)
                        if is_reference.lower() == 'true':
                            outpt.as_reference = True
                        else:
                            outpt.as_reference = False

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
