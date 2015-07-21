import lxml
import lxml.etree
from werkzeug.exceptions import MethodNotAllowed
from pywps import WPS
from pywps._compat import text_type, PY2
from pywps.app.basic import xpath_ns
from pywps.exceptions import NoApplicableCode, OperationNotSupported, MissingParameterValue, VersionNegotiationFailed, \
    InvalidParameterValue, FileSizeExceeded
from pywps import configuration
from pywps._compat import PY2


class WPSRequest(object):
    def __init__(self, http_request):
        self.http_request = http_request

        request_parser = self._get_request_parser_method(http_request.method)
        request_parser()


    def _get_request_parser_method(self, method):

        if method == 'GET':
            return self._get_request
        elif method == 'POST':
            return self._post_request
        else:
            raise MethodNotAllowed()


    def _get_request(self):
        """HTTP GET request parser
        """

        # WSDL request
        wsdl = _get_get_param(self.http_request, 'WSDL')
        if wsdl is not None:
            # TODO: fix #57 then remove the exception
            raise NoApplicableCode('WSDL not implemented')

        # service shall be WPS
        service = _get_get_param(self.http_request, 'service', aslist=False)
        if service:
            if str(service).lower() != 'wps':
                raise InvalidParameterValue(
                    'parameter SERVICE [%s] not supported' % service)
        else:
            raise MissingParameterValue('service', 'service')

        operation = _get_get_param(self.http_request, 'request', aslist=False)

        request_parser = self._get_request_parser(operation)
        request_parser(self.http_request)


    def _post_request(self):
        """HTTP GET request parser
        """
            
        # check if input file size was not exceeded
        maxsize = configuration.get_config_value('server', 'maxrequestsize')
        maxsize = configuration.get_size_mb(maxsize) * 1024 * 1024
        if self.http_request.content_length > maxsize:
            raise FileSizeExceeded('File size for input exceeded.'
                                   ' Maximum request size allowed: %i megabytes' % maxsize / 1024 / 1024)

        try:
                doc = lxml.etree.fromstring(self.http_request.get_data())
        except Exception as e:
            if PY2:
                raise NoApplicableCode(e.message)
            else:
                raise NoApplicableCode(e.msg)

        operation = doc.tag
        request_parser = self._post_request_parser(operation)
        request_parser(doc)


    def _get_request_parser(self, operation):
        """Factory function returing propper parsing function
        """

        wpsrequest = self

        def parse_get_getcapabilities(http_request):
            """Parse GET GetCapabilities request
            """

            acceptedversions = _get_get_param(http_request, 'acceptversions')
            wpsrequest.check_accepted_versions(acceptedversions)

        def parse_get_describeprocess(http_request):
            """Parse GET DescribeProcess request
            """
            version = _get_get_param(http_request, 'version')
            wpsrequest.check_and_set_version(version)
            wpsrequest.identifiers = _get_get_param(http_request, 'identifier', aslist=True)

        def parse_get_execute(http_request):
            """Parse GET Execute request
            """
            version = _get_get_param(http_request, 'version')
            wpsrequest.check_and_set_version(version)
            wpsrequest.identifier = _get_get_param(http_request, 'identifier')
            wpsrequest.store_execute = _get_get_param(http_request, 'storeExecuteResponse', 'false')
            wpsrequest.status = _get_get_param(http_request, 'status', 'false')
            wpsrequest.lineage = _get_get_param(http_request, 'lineage', 'false')
            wpsrequest.inputs = get_data_from_kvp(_get_get_param(http_request, 'DataInputs'))
            wpsrequest.outputs = {}

            # take responseDocument preferably
            resp_outputs = get_data_from_kvp(_get_get_param(http_request, 'ResponseDocument'))
            raw_outputs = get_data_from_kvp(_get_get_param(http_request, 'RawDataOutput'))
            wpsrequest.raw = False
            if resp_outputs:
                wpsrequest.outputs = resp_outputs
            elif raw_outputs:
                wpsrequest.outputs = raw_outputs
                wpsrequest.raw = True
                # executeResponse XML will not be stored and no updating of status
                wpsrequest.store_execute = 'false'
                wpsrequest.status = 'false'


        if not operation:
            raise MissingParameterValue('Missing request value', 'request')
        else:
            self.operation = operation.lower()

        if self.operation == 'getcapabilities':
            return parse_get_getcapabilities
        elif self.operation == 'describeprocess':
            return parse_get_describeprocess
        elif self.operation == 'execute':
            return parse_get_execute
        else:
            raise InvalidParameterValue('Unknown request %r' % self.operation, 'request')



    def _post_request_parser(self, tagname):
        """Factory function returing propper parsing function
        """

        wpsrequest = self

        def parse_post_getcapabilities(doc):
            """Parse POST GetCapabilities request
            """
            acceptedversions = xpath_ns(doc, '/wps:GetCapabilities/ows:AcceptVersions/ows:Version')
            acceptedversions = ','.join(map(lambda v: v.text, acceptedversions))
            wpsrequest.check_accepted_versions(acceptedversions)

        def parse_post_describeprocess(doc):
            """Parse POST DescribeProcess request
            """

            version = doc.attrib.get('version')
            wpsrequest.check_and_set_version(version)

            wpsrequest.operation = 'describeprocess'
            wpsrequest.identifiers = [identifier_el.text for identifier_el in
                                xpath_ns(doc, './ows:Identifier')]

        def parse_post_execute(doc):
            """Parse POST Execute request
            """

            version = doc.attrib.get('version')
            wpsrequest.check_and_set_version(version)

            wpsrequest.operation = 'execute'
            wpsrequest.identifier = xpath_ns(doc, './ows:Identifier')[0].text
            wpsrequest.lineage = 'false'
            wpsrequest.store_execute = 'false'
            wpsrequest.status = 'false'
            wpsrequest.inputs = get_input_from_xml(doc)
            wpsrequest.outputs = get_output_from_xml(doc)
            wpsrequest.raw = False
            if xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:RawDataOutput'):
                wpsrequest.raw = True
                # executeResponse XML will not be stored
                wpsrequest.store_execute = 'false'

            # check if response document tag has been set then retrieve
            response_document = xpath_ns(doc, './wps:ResponseForm/wps:ResponseDocument')
            if len(response_document) > 0:
                wpsrequest.lineage = response_document[0].attrib.get('lineage', 'false')
                wpsrequest.store_execute = response_document[0].attrib.get('storeExecuteResponse', 'false')
                wpsrequest.status = response_document[0].attrib.get('status', 'false')


        if tagname == WPS.GetCapabilities().tag:
            self.operation = 'getcapabilities'
            return parse_post_getcapabilities
        elif tagname == WPS.DescribeProcess().tag:
            self.operation = 'describeprocess'
            return parse_post_describeprocess
        elif tagname == WPS.Execute().tag:
            self.operation = 'execute'
            return parse_post_execute
        else:
            raise InvalidParameterValue('Unknown request %r' % tagname, 'request')

    def check_accepted_versions(self, acceptedversions):
        """
        :param acceptedversions: string
        """

        version = None

        if acceptedversions:
            acceptedversions_array = acceptedversions.split(',')
            for aversion in acceptedversions_array:
                if _check_version(aversion):
                    version  = aversion
        else:
            version = '1.0.0'

        if version:
            self.check_and_set_version(version)
        else:
            raise VersionNegotiationFailed('The requested version "%s" is not supported by this server' % acceptedversions, 'version')
    
    def check_and_set_version(self, version):
        """set this.version
        """

        if not version:
            raise MissingParameterValue('Missing version', 'version')
        elif not _check_version(version):
            raise VersionNegotiationFailed('The requested version "%s" is not supported by this server' % version, 'version')
        else:
            self.version = version

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
            inpt['data'] = _get_dataelement_value(value_el)
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
                if attribute == 'xlink:href':
                    io['href'] = attr_val
                else:
                    io[attribute] = attr_val

            # Add the input/output with all its attributes and values to the dictionary
            the_data[identifier] = io
        except:
            the_data[d] = {'identifier': d, 'data': ''}

    return the_data

def _check_version(version):    
    """ check given version
    """
    if version != '1.0.0':
        return False
    else:
        return True

    

def _get_get_param(http_request, key, default=None, aslist=False):
    """Returns value from the key:value pair, of the HTTP GET request, for
    example 'service' or 'request'

    :param http_request: http_request object
    :param key: key value you need to dig out of the HTTP GET request
    """

    key = key.lower()
    value = default
    # http_request.args.keys will make + sign disappear in GET url if not urlencoded
    for k in http_request.args.keys():
        if k.lower() == key:
            value = http_request.args.get(k)
            if aslist:
                value = value.split(",")

    return value

def _get_dataelement_value(value_el):
    """Return real value of XML Element (e.g. convert Element.FeatureCollection
    to String
    """

    if isinstance(value_el, lxml.etree._Element):
        if PY2:
            return lxml.etree.tostring(value_el, encoding=unicode)
        else:
            return lxml.etree.tostring(value_el, encoding=str)
    else:
        return value_el
