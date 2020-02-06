from werkzeug.wrappers import Request
import pywps.configuration as config
from pywps.app.basic import xml_response
from pywps.exceptions import NoApplicableCode
from pywps.exceptions import MissingParameterValue
from pywps.exceptions import InvalidParameterValue
from pywps.response import WPSResponse
from pywps import __version__
import os


class DescribeResponse(WPSResponse):

    def __init__(self, wps_request, uuid, **kwargs):

        super(DescribeResponse, self).__init__(wps_request, uuid)

        self.identifiers = None
        if "identifiers" in kwargs:
            self.identifiers = kwargs["identifiers"]
        self.processes = kwargs["processes"]

    @property
    def json(self):

        processes = []

        if 'all' in (ident.lower() for ident in self.identifiers):
            processes = (self.processes[p].json for p in self.processes)
        else:
            for identifier in self.identifiers:
                if identifier not in self.processes:
                    msg = "Unknown process {}".format(identifier)
                    raise InvalidParameterValue(msg, "identifier")
                else:
                    processes.append(self.processes[identifier].json)

        return {
            'pywps_version': __version__,
            'processes': processes,
            'language': self.wps_request.language,
        }

    def _construct_doc(self):

        if not self.identifiers:
            raise MissingParameterValue('Missing parameter value "identifier"', 'identifier')

        template = self.template_env.get_template(self.version + '/describe/main.xml')
        max_size = int(config.get_size_mb(config.get_config_value('server', 'maxsingleinputsize')))
        doc = template.render(max_size=max_size, **self.json)

        return doc

    @Request.application
    def __call__(self, request):
        # This function must return a valid response.
        try:
            doc = self.get_response_doc()
            return xml_response(doc)
        except NoApplicableCode as e:
            return e
        except Exception as e:
            return NoApplicableCode(str(e))
