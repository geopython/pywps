"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from werkzeug.datastructures import MultiDict
import lxml.etree
from lxml.builder import ElementMaker
from pywps._compat import text_type


NAMESPACES = {
    'wps': "http://www.opengis.net/wps/1.0.0",
    'ows': "http://www.opengis.net/ows/1.1",
}

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
        [value_el] = xpath_ns(input_el, './wps:Data/wps:LiteralData')
        the_input.update({identifier_el.text: text_type(value_el.text)})
    return the_input


class WPSRequest(object):

    def __init__(self, http_request):
        self.http_request = http_request

        if http_request.method == 'GET':
            self.operation = self._get_get_param('request').lower()

            if self.operation == 'getcapabilities':
                pass

            elif self.operation == 'describeprocess':
                self.identifiers = self._get_get_param('identifier',
                                                       aslist=True)

            elif self.operation == 'execute':
                self.identifier = self._get_get_param('identifier')

            else:
                raise BadRequest("Unknown request type %r" % self.operation)

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
                raise BadRequest("Unknown request type %r" % doc.tag)

        else:
            raise MethodNotAllowed()

    def _get_get_param(self, key, aslist=False):
        """Returns key from the key:value pair, of the HTTP GET request, for
        example 'service' or 'request'

        :param key: key value you need to dig out of the HTTP GET request
        :param value: default value
        """
        key = key.lower()
        for k in self.http_request.args.keys():
            if k.lower() == key:
                if aslist is True:
                    return self.http_request.args.getlist(k)
                else:
                    return self.http_request.args.get(k)

        # raise error
        if aslist:
            return ()
        else:
            return self.http_request.args[key]


class WPSResponse(object):

    def __init__(self, outputs=None):
        self.outputs = outputs or {}

    @Request.application
    def __call__(self, request):
        output_elements = []
        for key, value in self.outputs.items():
            output_elements.append(WPS.Output(
                OWS.Identifier(key),
                WPS.Data(WPS.LiteralData(value))
            ))

        doc = WPS.ExecuteResponse(
            WPS.Status(
                WPS.ProcessSucceeded("great success")
            ),
            WPS.ProcessOutputs(*output_elements)
        )
        return xml_response(doc)


class Process(object):
    """ WPS process """

    def __init__(self, handler, identifier=None):
        self.identifier = identifier or handler.__name__
        self.handler = handler

    def capabilities_xml(self):
        return WPS.Process(OWS.Identifier(self.identifier))

    def describe_xml(self):
        return WPS.ProcessDescription(
            OWS.Identifier(self.identifier)
        )

    def execute(self, wps_request):
        return self.handler(wps_request)


class Service(object):
    """ WPS service """

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
        for identifier in identifiers:
            try:
                process = self.processes[identifier]
            except KeyError:
                raise BadRequest("Unknown process %r" % identifier)
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
            return e
