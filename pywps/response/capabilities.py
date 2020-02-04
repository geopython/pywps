from werkzeug.wrappers import Request
import pywps.configuration as config
from pywps.app.basic import xml_response
from pywps.response import WPSResponse
from pywps import __version__
from pywps.exceptions import NoApplicableCode
import os


class CapabilitiesResponse(WPSResponse):

    def __init__(self, wps_request, uuid, version, **kwargs):

        super(CapabilitiesResponse, self).__init__(wps_request, uuid, version)

        self.processes = kwargs["processes"]

    @property
    def json(self):
        """Convert the response to JSON structure
        """

        processes = [p.json for p in self.processes.values()]
        return {
            'pywps_version': __version__,
            'version': self.version,
            'title': config.get_config_value('metadata:main', 'identification_title'),
            'abstract': config.get_config_value('metadata:main', 'identification_abstract'),
            'keywords': config.get_config_value('metadata:main', 'identification_keywords').split(","),
            'keywords_type': config.get_config_value('metadata:main', 'identification_keywords_type').split(","),
            'fees': config.get_config_value('metadata:main', 'identification_fees'),
            'accessconstraints': config.get_config_value(
                'metadata:main',
                'identification_accessconstraints'
            ).split(','),
            'profile': config.get_config_value('metadata:main', 'identification_profile'),
            'provider': {
                'name': config.get_config_value('metadata:main', 'provider_name'),
                'site': config.get_config_value('metadata:main', 'provider_url'),
                'individual': config.get_config_value('metadata:main', 'contact_name'),
                'position': config.get_config_value('metadata:main', 'contact_position'),
                'voice': config.get_config_value('metadata:main', 'contact_phone'),
                'fascimile': config.get_config_value('metadata:main', 'contaact_fax'),
                'address': {
                    'delivery': config.get_config_value('metadata:main', 'deliveryPoint'),
                    'city': config.get_config_value('metadata:main', 'contact_city'),
                    'state': config.get_config_value('metadata:main', 'contact_stateorprovince'),
                    'postalcode': config.get_config_value('metadata:main', 'contact_postalcode'),
                    'country': config.get_config_value('metadata:main', 'contact_country'),
                    'email': config.get_config_value('metadata:main', 'contact_email')
                },
                'url': config.get_config_value('metadata:main', 'contact_url'),
                'hours': config.get_config_value('metadata:main', 'contact_hours'),
                'instructions': config.get_config_value('metadata:main', 'contact_instructions'),
                'role': config.get_config_value('metadata:main', 'contact_role')
            },
            'serviceurl': config.get_config_value('server', 'url'),
            'languages': config.get_config_value('server', 'language').split(','),
            'language': self.wps_request.language,
            'processes': processes
        }

    def _construct_doc(self):

        template = self.template_env.get_template(self.version + '/capabilities/main.xml')

        doc = template.render(**self.json)

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
