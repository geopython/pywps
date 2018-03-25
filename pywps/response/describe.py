from werkzeug.wrappers import Request
from pywps import WPS, OWS
import pywps.configuration as config
from pywps.app.basic import xml_response
from pywps.exceptions import NoApplicableCode
from pywps.exceptions import MissingParameterValue
from pywps.exceptions import InvalidParameterValue
from pywps.response import WPSResponse
from pywps.response.status import STATUS


class DescribeResponse(WPSResponse):

    def __init__(self, wps_request, uuid, **kwargs):

        super(DescribeResponse, self).__init__(wps_request, uuid)

        self.identifiers = None
        if "identifiers" in kwargs:
            self.identifiers = kwargs["identifiers"]
        self.processes = kwargs["processes"]

    def _construct_doc(self):

        if not self.identifiers:
            raise MissingParameterValue('Missing parameter value "identifier"', 'identifier')

        identifier_elements = []
        # 'all' keyword means all processes
        if 'all' in (ident.lower() for ident in self.identifiers):
            for process in self.processes:
                try:
                    identifier_elements.append(
                        self.processes[process].describe_xml())
                except Exception as e:
                    raise NoApplicableCode(e)
        else:
            for identifier in self.identifiers:
                if identifier not in self.processes:
                    msg = "Unknown process %r" % identifier
                    raise InvalidParameterValue(msg, "identifier")
                else:
                    try:
                        process = self.processes[identifier]
                        identifier_elements.append(process.describe_xml())
                    except Exception as e:
                        raise NoApplicableCode(e)

        doc = WPS.ProcessDescriptions(
            *identifier_elements
        )
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = \
            'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'
        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-US'

        return doc

    @Request.application
    def __call__(self, request):
        doc = self.get_response_doc()
        return xml_response(doc)
