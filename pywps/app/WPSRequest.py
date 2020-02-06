##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
import lxml
import lxml.etree
from werkzeug.exceptions import MethodNotAllowed
from pywps import get_ElementMakerForVersion
import base64
import datetime
from pywps._compat import text_type, PY2
from pywps.app.basic import get_xpath_ns
from pywps.inout.inputs import input_from_json
from pywps.exceptions import NoApplicableCode, OperationNotSupported, MissingParameterValue, VersionNegotiationFailed, \
    InvalidParameterValue, FileSizeExceeded
from pywps import configuration
from pywps import get_version_from_ns

import json

LOGGER = logging.getLogger("PYWPS")


class WPSRequest(object):

    def __init__(self, http_request=None):
        self.http_request = http_request

        self.operation = None
        self.version = None
        self.language = None
        self.identifier = None
        self.identifiers = None
        self.store_execute = None
        self.status = None
        self.lineage = None
        self.inputs = {}
        self.outputs = {}
        self.raw = None
        self.WPS = None
        self.OWS = None
        self.xpath_ns = None

        if self.http_request:
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

        # service shall be WPS
        service = _get_get_param(self.http_request, 'service')
        if service:
            if str(service).lower() != 'wps':
                raise InvalidParameterValue(
                    'parameter SERVICE [{}] not supported'.format(service), 'service')
        else:
            raise MissingParameterValue('service', 'service')

        operation = _get_get_param(self.http_request, 'request')

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
                                   ' Maximum request size allowed: {} megabytes'.format(maxsize / 1024 / 1024))

        try:
            doc = lxml.etree.fromstring(self.http_request.get_data())
        except Exception as e:
            if PY2:
                raise NoApplicableCode(e.message)
            else:
                raise NoApplicableCode(e.msg)

        operation = doc.tag
        version = get_version_from_ns(doc.nsmap[doc.prefix])
        self.set_version(version)
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

            language = _get_get_param(http_request, 'language')
            wpsrequest.check_and_set_language(language)

        def parse_get_describeprocess(http_request):
            """Parse GET DescribeProcess request
            """
            version = _get_get_param(http_request, 'version')
            wpsrequest.check_and_set_version(version)

            language = _get_get_param(http_request, 'language')
            wpsrequest.check_and_set_language(language)

            wpsrequest.identifiers = _get_get_param(
                http_request, 'identifier', aslist=True)

        def parse_get_execute(http_request):
            """Parse GET Execute request
            """
            version = _get_get_param(http_request, 'version')
            wpsrequest.check_and_set_version(version)

            language = _get_get_param(http_request, 'language')
            wpsrequest.check_and_set_language(language)

            wpsrequest.identifier = _get_get_param(http_request, 'identifier')
            wpsrequest.store_execute = _get_get_param(
                http_request, 'storeExecuteResponse', 'false')
            wpsrequest.status = _get_get_param(http_request, 'status', 'false')
            wpsrequest.lineage = _get_get_param(
                http_request, 'lineage', 'false')
            wpsrequest.inputs = get_data_from_kvp(
                _get_get_param(http_request, 'DataInputs'), 'DataInputs')
            if self.inputs is None:
                self.inputs = {}

            wpsrequest.outputs = {}

            # take responseDocument preferably
            resp_outputs = get_data_from_kvp(
                _get_get_param(http_request, 'ResponseDocument'))
            raw_outputs = get_data_from_kvp(
                _get_get_param(http_request, 'RawDataOutput'))
            wpsrequest.raw = False
            if resp_outputs:
                wpsrequest.outputs = resp_outputs
            elif raw_outputs:
                wpsrequest.outputs = raw_outputs
                wpsrequest.raw = True
                # executeResponse XML will not be stored and no updating of
                # status
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
            raise OperationNotSupported(
                'Unknown request {}'.format(self.operation), operation)

    def _post_request_parser(self, tagname):
        """Factory function returing propper parsing function
        """

        wpsrequest = self

        def parse_post_getcapabilities(doc):
            """Parse POST GetCapabilities request
            """
            acceptedversions = self.xpath_ns(
                doc, '/wps:GetCapabilities/ows:AcceptVersions/ows:Version')
            acceptedversions = ','.join(
                map(lambda v: v.text, acceptedversions))
            wpsrequest.check_accepted_versions(acceptedversions)

            language = doc.attrib.get('language')
            wpsrequest.check_and_set_language(language)

        def parse_post_describeprocess(doc):
            """Parse POST DescribeProcess request
            """

            version = doc.attrib.get('version')
            wpsrequest.check_and_set_version(version)

            language = doc.attrib.get('language')
            wpsrequest.check_and_set_language(language)

            wpsrequest.operation = 'describeprocess'
            wpsrequest.identifiers = [identifier_el.text for identifier_el in
                                      self.xpath_ns(doc, './ows:Identifier')]

        def parse_post_execute(doc):
            """Parse POST Execute request
            """
            version = doc.attrib.get('version')
            wpsrequest.check_and_set_version(version)

            language = doc.attrib.get('language')
            wpsrequest.check_and_set_language(language)

            wpsrequest.operation = 'execute'

            identifier = self.xpath_ns(doc, './ows:Identifier')

            if not identifier:
                raise MissingParameterValue(
                    'Process identifier not set', 'Identifier')

            wpsrequest.identifier = identifier[0].text
            wpsrequest.lineage = 'false'
            wpsrequest.store_execute = 'false'
            wpsrequest.status = 'false'
            wpsrequest.inputs = get_inputs_from_xml(doc)
            wpsrequest.outputs = get_output_from_xml(doc)
            wpsrequest.raw = False
            if self.xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:RawDataOutput'):
                wpsrequest.raw = True
                # executeResponse XML will not be stored
                wpsrequest.store_execute = 'false'

            # check if response document tag has been set then retrieve
            response_document = self.xpath_ns(
                doc, './wps:ResponseForm/wps:ResponseDocument')
            if len(response_document) > 0:
                wpsrequest.lineage = response_document[
                    0].attrib.get('lineage', 'false')
                wpsrequest.store_execute = response_document[
                    0].attrib.get('storeExecuteResponse', 'false')
                wpsrequest.status = response_document[
                    0].attrib.get('status', 'false')

        if tagname == self.WPS.GetCapabilities().tag:
            self.operation = 'getcapabilities'
            return parse_post_getcapabilities
        elif tagname == self.WPS.DescribeProcess().tag:
            self.operation = 'describeprocess'
            return parse_post_describeprocess
        elif tagname == self.WPS.Execute().tag:
            self.operation = 'execute'
            return parse_post_execute
        else:
            raise InvalidParameterValue(
                'Unknown request {}'.format(tagname), 'request')

    def set_version(self, version):
        self.version = version
        self.xpath_ns = get_xpath_ns(version)
        self.WPS, self.OWS = get_ElementMakerForVersion(self.version)

    def check_accepted_versions(self, acceptedversions):
        """
        :param acceptedversions: string
        """

        version = None

        if acceptedversions:
            acceptedversions_array = acceptedversions.split(',')
            for aversion in acceptedversions_array:
                if _check_version(aversion):
                    version = aversion
        else:
            version = '1.0.0'

        if version:
            self.check_and_set_version(version)
        else:
            raise VersionNegotiationFailed(
                'The requested version "{}" is not supported by this server'.format(acceptedversions), 'version')

    def check_and_set_version(self, version):
        """set this.version
        """

        if not version:
            raise MissingParameterValue('Missing version', 'version')
        elif not _check_version(version):
            raise VersionNegotiationFailed(
                'The requested version "{}" is not supported by this server'.format(version), 'version')
        else:
            self.set_version(version)

    def check_and_set_language(self, language):
        """set this.language
        """
        supported_languages = configuration.get_config_value('server', 'language').split(',')
        supported_languages = [lang.strip() for lang in supported_languages]

        if not language:
            # default to the first supported language
            language = supported_languages[0]

        if language not in supported_languages:
            raise InvalidParameterValue(
                'The requested language "{}" is not supported by this server'.format(language),
                'language',
            )

        self.language = language

    @property
    def json(self):
        """Return JSON encoded representation of the request
        """
        class ExtendedJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime.date) or isinstance(obj, datetime.time):
                    encoded_object = obj.isoformat()
                else:
                    encoded_object = json.JSONEncoder.default(self, obj)
                return encoded_object

        obj = {
            'operation': self.operation,
            'version': self.version,
            'language': self.language,
            'identifier': self.identifier,
            'identifiers': self.identifiers,
            'store_execute': self.store_execute,
            'status': self.status,
            'lineage': self.lineage,
            'inputs': dict((i, [inpt.json for inpt in self.inputs[i]]) for i in self.inputs),
            'outputs': self.outputs,
            'raw': self.raw
        }

        return json.dumps(obj, allow_nan=False, cls=ExtendedJSONEncoder)

    @json.setter
    def json(self, value):
        """init this request from json back again

        :param value: the json (not string) representation
        """

        self.operation = value['operation']
        self.version = value['version']
        self.language = value['language']
        self.identifier = value['identifier']
        self.identifiers = value['identifiers']
        self.store_execute = value['store_execute']
        self.status = value['status']
        self.lineage = value['lineage']
        self.outputs = value['outputs']
        self.raw = value['raw']
        self.inputs = {}

        for identifier in value['inputs']:
            inpt_defs = value['inputs'][identifier]

            for inpt_def in inpt_defs:
                inpt = input_from_json(inpt_def)

                if identifier in self.inputs:
                    self.inputs[identifier].append(inpt)
                else:
                    self.inputs[identifier] = [inpt]


def get_inputs_from_xml(doc):
    the_inputs = {}
    version = get_version_from_ns(doc.nsmap[doc.prefix])
    xpath_ns = get_xpath_ns(version)
    for input_el in xpath_ns(doc, '/wps:Execute/wps:DataInputs/wps:Input'):
        [identifier_el] = xpath_ns(input_el, './ows:Identifier')
        identifier = identifier_el.text

        if identifier not in the_inputs:
            the_inputs[identifier] = []

        literal_data = xpath_ns(input_el, './wps:Data/wps:LiteralData')
        if literal_data:
            value_el = literal_data[0]
            inpt = {}
            inpt['identifier'] = identifier_el.text
            inpt['data'] = text_type(value_el.text)
            inpt['uom'] = value_el.attrib.get('uom', '')
            inpt['datatype'] = value_el.attrib.get('datatype', '')
            the_inputs[identifier].append(inpt)
            continue

        complex_data = xpath_ns(input_el, './wps:Data/wps:ComplexData')
        if complex_data:

            complex_data_el = complex_data[0]
            inpt = {}
            inpt['identifier'] = identifier_el.text
            inpt['mimeType'] = complex_data_el.attrib.get('mimeType', '')
            inpt['encoding'] = complex_data_el.attrib.get(
                'encoding', '').lower()
            inpt['schema'] = complex_data_el.attrib.get('schema', '')
            inpt['method'] = complex_data_el.attrib.get('method', 'GET')
            if len(complex_data_el.getchildren()) > 0:
                value_el = complex_data_el[0]
                inpt['data'] = _get_dataelement_value(value_el)
            else:
                inpt['data'] = _get_rawvalue_value(
                    complex_data_el.text, inpt['encoding'])
            the_inputs[identifier].append(inpt)
            continue

        reference_data = xpath_ns(input_el, './wps:Reference')
        if reference_data:
            reference_data_el = reference_data[0]
            inpt = {}
            inpt['identifier'] = identifier_el.text
            inpt[identifier_el.text] = reference_data_el.text
            inpt['href'] = reference_data_el.attrib.get(
                '{http://www.w3.org/1999/xlink}href', '')
            inpt['mimeType'] = reference_data_el.attrib.get('mimeType', '')
            inpt['method'] = reference_data_el.attrib.get('method', 'GET')
            header_element = xpath_ns(reference_data_el, './wps:Header')
            if header_element:
                inpt['header'] = _get_reference_header(header_element)
            body_element = xpath_ns(reference_data_el, './wps:Body')
            if body_element:
                inpt['body'] = _get_reference_body(body_element[0])
            bodyreference_element = xpath_ns(reference_data_el,
                                             './wps:BodyReference')
            if bodyreference_element:
                inpt['bodyreference'] = _get_reference_bodyreference(
                    bodyreference_element[0])
            the_inputs[identifier].append(inpt)
            continue

        # Using OWSlib BoundingBox
        from owslib.ows import BoundingBox
        bbox_datas = xpath_ns(input_el, './wps:Data/wps:BoundingBoxData')
        if bbox_datas:
            for bbox_data in bbox_datas:
                bbox_data_el = bbox_data
                bbox = BoundingBox(bbox_data_el)
                the_inputs[identifier].append(bbox)
                LOGGER.debug("parse bbox: {},{},{},{}".format(bbox.minx, bbox.miny, bbox.maxx, bbox.maxy))
    return the_inputs


def get_output_from_xml(doc):
    the_output = {}

    version = get_version_from_ns(doc.nsmap[doc.prefix])
    xpath_ns = get_xpath_ns(version)

    if xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:ResponseDocument'):
        for output_el in xpath_ns(doc, '/wps:Execute/wps:ResponseForm/wps:ResponseDocument/wps:Output'):
            [identifier_el] = xpath_ns(output_el, './ows:Identifier')
            outpt = {}
            outpt[identifier_el.text] = ''
            outpt['mimetype'] = output_el.attrib.get('mimeType', '')
            outpt['encoding'] = output_el.attrib.get('encoding', '')
            outpt['schema'] = output_el.attrib.get('schema', '')
            outpt['uom'] = output_el.attrib.get('uom', '')
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


def get_data_from_kvp(data, part=None):
    """Get execute DataInputs and ResponseDocument from URL (key-value-pairs) encoding
    :param data: key:value pair list of the datainputs and responseDocument parameter
    :param part: DataInputs or similar part of input url
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
                (attribute, attr_val) = attr.split('=', 1)
                if attribute == 'xlink:href':
                    io['href'] = attr_val
                else:
                    io[attribute] = attr_val

            # Add the input/output with all its attributes and values to the
            # dictionary
            if part == 'DataInputs':
                if identifier not in the_data:
                    the_data[identifier] = []
                the_data[identifier].append(io)
            else:
                the_data[identifier] = io
        except Exception as e:
            LOGGER.warning(e)
            the_data[d] = {'identifier': d, 'data': ''}

    return the_data


def _check_version(version):
    """ check given version
    """
    if version not in ['1.0.0', '2.0.0']:
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
    # http_request.args.keys will make + sign disappear in GET url if not
    # urlencoded
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
            return lxml.etree.tostring(value_el, encoding=unicode)  # noqa
        else:
            return lxml.etree.tostring(value_el, encoding=str)
    else:
        return value_el


def _get_rawvalue_value(data, encoding=None):
    """Return real value of CDATA section"""

    try:
        if encoding is None or encoding == "":
            return data
        elif encoding == 'base64':
            return base64.b64decode(data)
        return base64.b64decode(data)
    except Exception:
        return data


def _get_reference_header(header_element):
    """Parses ReferenceInput Header element
    """
    header = {}
    header['key'] = header_element.attrib('key')
    header['value'] = header_element.attrib('value')
    return header


def _get_reference_body(body_element):
    """Parses ReferenceInput Body element
    """

    body = None
    if len(body_element.getchildren()) > 0:
        value_el = body_element[0]
        body = _get_dataelement_value(value_el)
    else:
        body = _get_rawvalue_value(body_element.text)

    return body


def _get_reference_bodyreference(referencebody_element):
    """Parse ReferenceInput BodyReference element
    """
    return referencebody_element.attrib.get(
        '{http://www.w3.org/1999/xlink}href', '')
