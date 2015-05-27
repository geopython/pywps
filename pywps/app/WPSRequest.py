import lxml
from werkzeug.exceptions import MethodNotAllowed
from pywps import WPS
from pywps._compat import text_type, PY2
from pywps.app.basic import xpath_ns
from pywps.exceptions import NoApplicableCode, OperationNotSupported, MissingParameterValue, VersionNegotiationFailed, \
    InvalidParameterValue


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
                self.inputs = self.get_data_from_kvp(self._get_get_param('DataInputs'))
                self.outputs = {}

                # take responseDocument preferably
                resp_outputs = self.get_data_from_kvp(self._get_get_param('ResponseDocument'))
                raw_outputs = self.get_data_from_kvp(self._get_get_param('RawDataOutput'))
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
                self.inputs = self.get_input_from_xml(doc)
                self.outputs = self.get_output_from_xml(doc)
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
                the_data[d] = {'identifier': d, 'data': ''}

        return the_data
