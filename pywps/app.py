"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""
import os
import tempfile
import time
import sys
from pywps.storage import FileStorage
from uuid import uuid4

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from pywps.exceptions import InvalidParameterValue, \
    MissingParameterValue, NoApplicableCode, \
    OperationNotSupported, VersionNegotiationFailed, FileSizeExceeded, StorageNotSupported
import lxml.etree
from lxml.builder import ElementMaker
from pywps._compat import text_type, StringIO
from pywps import inout
from pywps.inout import FormatBase
from pywps import config
from lxml import etree

from pywps._compat import PY2



xmlschema_2 = "http://www.w3.org/TR/xmlschema-2/#"
LITERAL_DATA_TYPES = ['string', 'float', 'integer', 'boolean']

NAMESPACES = {
    'xlink': "http://www.w3.org/1999/xlink",
    'wps': "http://www.opengis.net/wps/1.0.0",
    'ows': "http://www.opengis.net/ows/1.1",
    'gml': "http://www.opengis.net/gml",
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
            inpt['identifier'] = identifier_el.text
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
            inpt['identifier'] = identifier_el.text
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
            inpt['identifier'] = identifier_el.text
            inpt[identifier_el.text] = reference_data_el.text
            inpt['href'] = reference_data_el.attrib.get('href', '')
            if not inpt['href']:
                inpt['href'] = reference_data_el.attrib.get('{http://www.w3.org/1999/xlink}href', '')
            inpt['mimeType'] = reference_data_el.attrib.get('mimeType', '')
            the_input[identifier_el.text] = inpt
            continue

        # OWSlib is not python 3 compatible yet
        if PY2:
            from owslib.ows import BoundingBox

            bbox_data = xpath_ns(input_el, './wps:Data/wps:BoundingBoxData')
            if bbox_data:
                bbox_data_el = bbox_data[0]
                bbox = BoundingBox(bbox_data_el)
                the_input.update({identifier_el.text: bbox})
                continue

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
def get_output_from_xml(doc):
    the_output = {}

    if xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:ResponseDocument'):
        for output_el in xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:ResponseDocument/wps:Output'):
            [identifier_el] = xpath_ns(output_el, './ows:Identifier')
            outpt = {}
            outpt[identifier_el.text] = ''
            outpt['asReference'] = output_el.attrib.get('asReference', 'false')
            the_output[identifier_el.text] = outpt

    elif xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:RawDataOutput'):
        for output_el in xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:RawDataOutput'):
            [identifier_el] = xpath_ns(output_el, './ows:Identifier')
            outpt = {}
            outpt[identifier_el.text] = ''
            outpt['mimetype'] = output_el.attrib.get('mimeType', '')
            outpt['encoding'] = output_el.attrib.get('encoding', '')
            outpt['schema'] = output_el.attrib.get('schema', '')
            outpt['uom'] = output_el.attrib.get('uom', '')
            the_output[identifier_el.text] = outpt

    return the_output


def get_data_from_kvp(data):
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
            io['identifier'] = identifier
            io['data'] = val

            # Get the attributes of the data
            for attr in fields[1:]:
                (attribute, attr_val) = attr.split('=')
                io[attribute] = attr_val

            # Add the input/output with all its attributes and values to the dictionary
            the_data[identifier] = io
        except:
            the_data[d] = ''

    return the_data


def parse_complex_inputs(inputs):

    data_input = ComplexInput(inputs.get('identifier'), '', None)
    data_input.data_format = Format(
        inputs.get('mime_type'),
        inputs.get('encoding'),
        inputs.get('schema')
    )
    data_input.method = inputs.get('method', 'GET')

    # get the referenced input otherwise get the value of the field
    href = inputs.get('href', None)
    if href:
        tmp_dir = config.get_config_value('server', 'tempPath')

        # check if in the configuration file specified temp directory exists otherwise create it
        try:
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
        except Exception as e:
            raise NoApplicableCode('File error: Could not create %s. %s' % (tmp_dir, e))

        # save the reference input in tempPath
        tmp_file = tempfile.mkstemp(dir=tmp_dir)[1]

        try:
            if PY2:
                import urllib2
                reference_file = urllib2.urlopen(href)
            else:
                from urllib.request import urlopen
                reference_file = urlopen(href)

            reference_file_data = reference_file.read()
            data_size = reference_file.headers.get('Content-Length', 0)
        except Exception as e:
            raise NoApplicableCode('File reference error: %s' % e)

        # if the response did not return a 'Content-Length' header then calculate the size
        if data_size == 0:
            tmp_sio = StringIO()
            tmp_sio.write(reference_file_data)
            data_size = tmp_sio.len
            tmp_sio.close()

        # check if input file size was not exceeded
        byte_size = data_input.max_megabytes * 1024 * 1024
        if int(data_size) > int(byte_size):
            raise FileSizeExceeded('File size for input exceeded.'
                                   ' Maximum allowed: %i megabytes' % data_input.max_megabytes,
                                   inputs.get('identifier'))

        try:
            if PY2:
                mode = 'w'
            else:
                mode = 'wb'

            with open(tmp_file, mode) as f:
                f.write(reference_file_data)
                f.close()
        except Exception as e:
            raise NoApplicableCode(e)

        data_input.file = tmp_file
        data_input.url = href
        data_input.as_reference = True
    else:
        data = inputs.get('data')
        # check if input file size was not exceeded
        byte_size = data_input.max_megabytes * 1024 * 1024
        if len(data.encode('utf-8')) > int(byte_size):
            raise FileSizeExceeded('File size for input exceeded.'
                                   ' Maximum allowed: %i megabytes' % data_input.max_megabytes,
                                   inputs.get('identifier'))
        data_input.data = data
    return data_input


def parse_literal_inputs(inputs):
    """ Takes the http_request and parses the input to objects
    :return:
    """

    # set the input to the type defined in the process
    data_input = LiteralInput(inputs.get('identifier'), '')
    data_input.uom = inputs.get('uom')
    data_type = inputs.get('datatype')
    if data_type:
        data_input.data_type = data_type

    # get the value of the field
    data_input.data = inputs.get('data')

    return data_input


class WPSRequest(object):
    def __init__(self, http_request):
        self.http_request = http_request

        if http_request.method == 'GET':
            # WSDL request
            wsdl = self._get_get_param('WSDL')
            if wsdl is not None:
                # TODO: fix #57 then remove the exception
                raise NoApplicableCode('WSDL not implemented')

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
                self.status = self._get_get_param('status', 'false')
                self.lineage = self._get_get_param('lineage', 'false')
                self.inputs = get_data_from_kvp(self._get_get_param('DataInputs'))
                self.outputs = {}

                # take responseDocument preferably
                resp_outputs = get_data_from_kvp(self._get_get_param('ResponseDocument'))
                raw_outputs = get_data_from_kvp(self._get_get_param('RawDataOutput'))
                self.raw = False
                if resp_outputs:
                    self.outputs = resp_outputs
                elif raw_outputs:
                    self.outputs = raw_outputs
                    self.raw = True
                    # executeResponse XML will not be stored and no updating of status
                    self.store_execute = 'false'
                    self.status = 'false'

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
                self.lineage = 'false'
                self.store_execute = 'false'
                self.status = 'false'
                self.inputs = get_input_from_xml(doc)
                self.outputs = get_output_from_xml(doc)
                self.raw = False
                if xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:RawDataOutput'):
                    self.raw = True
                    # executeResponse XML will not be stored
                    self.store_execute = 'false'

                # check if response document tag has been set then retrieve
                response_document = xpath_ns(doc, './wps:ResponseForm/wps:ResponseDocument')
                if len(response_document) > 0:
                    self.lineage = response_document[0].attrib.get('lineage', 'false')
                    self.store_execute = response_document[0].attrib.get('storeExecuteResponse', 'false')
                    self.status = response_document[0].attrib.get('status', 'false')

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


class WPSResponse(object):

    NO_STATUS = 0
    STORE_STATUS = 1
    STORE_AND_UPDATE_STATUS = 2

    def __init__(self, process, wps_request):
        self.process = process
        self.wps_request = wps_request
        self.outputs = {o.identifier: o for o in process.outputs}
        self.message = ''
        self.status = self.NO_STATUS
        self.status_percentage = 0
        self.doc = None

    def update_status(self, message, status_percentage=None):
        self.message = message
        if status_percentage:
            self.status_percentage = status_percentage

            # rebuild the doc and update the status xml file
            self.doc = self._construct_doc()

        # check if storing of the status is requested
        if self.status >= self.STORE_STATUS:
            self.write_response_doc(self.doc)

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
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-CA'
        doc.attrib['serviceInstance'] = '%s:%s%s' % (
            config.get_config_value('wps', 'serveraddress'),
            config.get_config_value('wps', 'serverport'),
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
            doc.append(OWS.Abstract(self.process.abstract))
        # TODO: See Table 32 Metadata in OGC 06-121r3
        for m in self.process.metadata:
            doc.append(OWS.Metadata(m))
        if self.process.profile:
            doc.append(OWS.Profile(self.process.profile))
        if self.process.wsdl:
            doc.append(OWS.WSDL(self.process.wsdl))
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
            data_inputs = [self.wps_request.inputs[i].execute_xml() for i in self.wps_request.inputs]
            doc.append(WPS.DataInputs(*data_inputs))

            output_definitions = [self.outputs[o].describe_xml() for o in self.outputs]
            doc.append(WPS.OutputDefinitions(*output_definitions))

        # Process outputs XML
        output_elements = [self.outputs[o].execute_xml() for o in self.outputs]
        doc.append(WPS.ProcessOutputs(*output_elements))

        return doc

    @Request.application
    def __call__(self, request):
        return xml_response(self._construct_doc())


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
        literal_doc = WPS.LiteralData(self.data)

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
                 max_occurs='1', as_reference=False):
        inout.ComplexInput.__init__(self, identifier=identifier, title=title, abstract=abstract, data_format=data_format)
        self.allowed_formats = allowed_formats
        self.metadata = metadata
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.as_reference = as_reference
        self.url = ''
        self.method = ''
        self.max_megabytes = int(0)
        self.calculate_max_input_size()

    def calculate_max_input_size(self):
        """Calculates maximal size for input file based on configuration
        and units

        :return: maximum file size bytes
        """
        maxSize = config.get_config_value('server', 'maxfilesize')
        maxSize = maxSize.lower()

        import re

        units = re.compile("[gmkb].*")
        size = float(re.sub(units, '', maxSize))

        if maxSize.find("g") > -1:
            size *= 1024
        elif maxSize.find("m") > -1:
            size *= 1
        elif maxSize.find("k") > -1:
            size /= 1024
        else:
            size *= 1
        self.max_megabytes = size

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
            doc.attrib['maximumMegabytes'] = str(self.max_megabytes)

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
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.url
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

        literal_data_doc = WPS.LiteralData(text_type(self.data))
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
                 schema=None, abstract='', metadata=[]):
        inout.ComplexOutput.__init__(self, identifier, title=title, abstract=abstract)
        self.formats = formats
        self.metadata = metadata

        self._schema = None
        self._output_format = None
        self._encoding = None

        self.as_reference = False
        self.output_format = output_format
        self.encoding = encoding
        self.schema = schema
        self.storage = None

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
        self.storage = FileStorage(config)
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

        if self.data is None:
            complex_doc = WPS.ComplexData()
        else:
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
                 outputs=[], version='None', store_supported=False, status_supported=False):
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
        self.uuid = None
        self.status_location = ''
        self.status_url = ''

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

        if self.wsdl:
            doc.append(WPS.WSDL({'{http://www.w3.org/1999/xlink}href': self.wsdl}))

        if input_elements:
            doc.append(E.DataInputs(*input_elements))

        doc.append(E.ProcessOutputs(*output_elements))

        return doc

    def execute(self, wps_request):
        import multiprocessing
        self.uuid = str(uuid4())
        async = False
        wps_response = WPSResponse(self, wps_request)

        # check if status storage and updating are supported by this process
        if wps_request.store_execute == 'true':
            if self.store_supported != 'true':
                raise StorageNotSupported('Process does not support the storing of the execute response')

            file_path = config.get_config_value('server', 'outputPath')
            file_url = '%s:%s%s' % (
                config.get_config_value('wps', 'serveraddress'),
                config.get_config_value('wps', 'serverport'),
                config.get_config_value('server', 'outputUrl')
            )

            self.status_location = os.path.join(file_path, self.uuid) + '.xml'
            self.status_url = os.path.join(file_url, self.uuid) + '.xml'

            # check if in the configuration file specified directory exists otherwise create it
            try:
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
            except Exception as e:
                raise NoApplicableCode('File error: Could not create %s. %s' % (file_path, e))

            if wps_request.status == 'true':
                if self.status_supported != 'true':
                    raise OperationNotSupported('Process does not support the updating of status')

                wps_response.status = WPSResponse.STORE_AND_UPDATE_STATUS
                async = True
            else:
                wps_response.status = WPSResponse.STORE_STATUS

        # check if updating of status is not required then no need to spawn a process
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
                # update the process status to 100% if everything went correctly
                wps_response.update_status('PyWPS Process finished', 100)
        except Exception as e:
            # retrieve the file and line number where the exception occurred
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
            wps_response.update_status('Process error: %s.%s Line %i %s' % (fname, method_name, exc_tb.tb_lineno, e), -1)

        return wps_response


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
        data_inputs = {}
        for inpt in process.inputs:
            if inpt.identifier not in wps_request.inputs:
                raise MissingParameterValue('', inpt.identifier)

            # Replace the dicts with the dict of Literal/Complex inputs
            # set the input to the type defined in the process
            if isinstance(inpt, ComplexInput):
                data_inputs[inpt.identifier] = parse_complex_inputs(wps_request.inputs[inpt.identifier])
            elif isinstance(inpt, LiteralInput):
                data_inputs[inpt.identifier] = parse_literal_inputs(wps_request.inputs[inpt.identifier])
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
