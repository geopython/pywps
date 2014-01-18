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

xmlschema_2 = "http://www.w3.org/TR/xmlschema-2/#"
LITERAL_DATA_TYPES = ['string', 'float', 'integer', 'boolean']

NAMESPACES = {
    'wps': "http://www.opengis.net/wps/1.0.0",
    'ows': "http://www.opengis.net/ows/1.1",
    'gml': "http://www.opengis.net/gml",
}

E = ElementMaker()
WPS = ElementMaker(namespace=NAMESPACES['wps'], nsmap=NAMESPACES)
OWS = ElementMaker(namespace=NAMESPACES['ows'], nsmap=NAMESPACES)


def xpath_ns(el, path):
    return el.xpath(path, namespaces=NAMESPACES)


def xml_response(doc):
    return Response(lxml.etree.tostring(doc, pretty_print=True),
                    content_type='text/xml')


def get_input_from_kvp(datainputs):
    """Get execute DataInputs from URL (key-value-pairs) encoding
    """

    inputs = {}

    if datainputs:
        for inpt in datainputs.split(";"):
            (identifier, val) = inpt.split("=")

            # add input to Inputs
            inputs[identifier] = val

    return inputs

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
                raise MissingParameterValue('request')
            else:
                self.operation = self.operation.lower()

            if self.operation == 'getcapabilities':
                pass

            elif self.operation == 'describeprocess':
                self.identifiers = self._get_get_param('identifier',
                                                       aslist=True)
                if not self.identifiers:
                    raise MissingParameterValue('identifier')

            elif self.operation == 'execute':
                self.identifier = self._get_get_param('identifier')
                self.inputs = get_input_from_kvp(
                    self._get_get_param('datainputs'))

            else:
                raise InvalidParameterValue(self.operation)

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
        """Returns key from the key:value pair, of the HTTP GET request, for
        example 'service' or 'request'

        If no value,

        :param key: key value you need to dig out of the HTTP GET request
        :param value: default value
        """
        key = key.lower()
        for k in self.http_request.args.keys():
            if k.lower() == key:
                if aslist:
                    return self.http_request.args.getlist(k)
                else:
                    return self.http_request.args.get(k)

        # raise error
        return None


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


class LiteralInput(object):
    """
    :param identifier: The name of this input.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    """

    def __init__(self, identifier, data_type='string'):
        self.identifier = identifier
        assert data_type in LITERAL_DATA_TYPES
        self.data_type = data_type

    def describe_xml(self):
        return E.Input(
            OWS.Identifier(self.identifier),
            E.LiteralData(
                OWS.DataType(self.data_type,
                             reference=xmlschema_2 + self.data_type)
            )
        )


class ComplexInput(object):
    """
    :param identifier: The name of this input.
    :param formats: Allowed formats for this input. Should be a list of
                    one or more :class:`~Format` objects.
    """

    def __init__(self, identifier, formats):
        self.identifier = identifier
        self.formats = formats

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


class LiteralOutput(object):
    """
    :param identifier: The name of this output.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    :param value: Resulting value
            Should be :class:`~String` object.
    """

    def __init__(self, identifier, data_type='string'):
        self.identifier = identifier
        assert data_type in LITERAL_DATA_TYPES
        self.data_type = data_type
        self.value = None

    def setvalue(self, value):
        self.value = value

    def getvalue(self):
        return self.value

    def describe_xml(self):
        return WPS.Output(
            OWS.Identifier(self.identifier),
            WPS.LiteralData(OWS.DataType(self.data_type, reference=xmlschema_2 + self.data_type))
        )

    def execute_xml(self):
        return WPS.Output(
            OWS.Identifier(self.identifier),
            WPS.Data(WPS.LiteralData(
                self.getvalue(),
                dataType=self.data_type,
                reference=xmlschema_2 + self.data_type
            ))
        )


class ComplexOutput(object):
    """
    :param identifier: The name of this output.
    :param formats: Possible output formats for this output.
            Should be list of :class:`~Format` object.
    :param output_format: Required format for this output.
            Should be :class:`~Format` object.
    :param encoding: The encoding of this input or requested for this output
            (e.g., UTF-8).
    """

    def __init__(self, identifier, formats, output_format=None, encoding="UTF-8", schema=None):
        self.identifier = identifier
        self.formats = formats
        self.value = None
        self.as_reference = False
        self.set_outputformat(output_format)
        self.set_encoding(encoding)
        self.set_schema(schema)

    def getvalue(self):
        """Get value of this output
        """

        return str(self.value)

    def get_outputformat(self):
        """Get output format
        :rtype: String
        """

        if self.output_format:
            return self.output_format
        else:
            return ''

    def set_outputformat(self, output_format):
        """Set output format
        """
        self.output_format = output_format

    def get_encoding(self ):
        """Get output encoding
        :rtype: String
        """

        if self.encoding:
            return self.encoding
        else:
            return ''

    def set_encoding(self, encoding):
        """Set output encoding
        """
        self.encoding = encoding

    def get_schema(self):
        """Get output schema
        :rtype: String
        """

        return ""

    def set_schema(self, schema):
        """Set output encoding
        """
        self.schema = schema

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
        pass

    def _execute_xml_data(self):
        return WPS.ComplexData(
                self.getvalue(),
                mimeType=self.get_outputformat(),
                encoding=self.get_encoding(),
                schema=self.get_schema()
        )

class BoundingBoxOutput(object):
    """bounding box output
    """
    # TODO
    pass


class Format(object):
    """
    :param mime_type: MIME type allowed for a complex input.
    """
    mime_type = None

    def __init__(self, mime_type):

        self.mime_type = mime_type

    def describe_xml(self):
        return E.Format(OWS.MimeType(self.mime_type))


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

    def __init__(self, handler, identifier=None, inputs=[], outputs=[]):
        self.identifier = identifier or handler.__name__
        self.handler = handler
        self.inputs = inputs
        self.outputs = outputs

    def capabilities_xml(self):
        return WPS.Process(OWS.Identifier(self.identifier))

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
        return self.handler(wps_request, wps_response)


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
        try:
            process = self.processes[identifier]
        except KeyError:
            raise BadRequest("Unknown process %r" % identifier)
        return process.execute(wps_request)

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
