from werkzeug.wrappers import Request
from pywps import WPS, OWS
import pywps.configuration as config
from pywps.app.basic import xml_response
from pywps.response import WPSResponse
from pywps.response.status import STATUS


class CapabilitiesResponse(WPSResponse):

    def __init__(self, wps_request, uuid, **kwargs):

        super(CapabilitiesResponse, self).__init__(wps_request, uuid)

        self.processes = kwargs["processes"]

    def _construct_doc(self):

        process_elements = [p.capabilities_xml()
                            for p in self.processes.values()]

        doc = WPS.Capabilities()

        doc.attrib['service'] = 'WPS'
        doc.attrib['version'] = '1.0.0'
        doc.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'en-US'
        doc.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = \
            'http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd'
        # TODO: check Table 7 in OGC 05-007r7
        doc.attrib['updateSequence'] = '1'

        # Service Identification
        service_ident_doc = OWS.ServiceIdentification(
            OWS.Title(config.get_config_value('metadata:main', 'identification_title'))
        )

        if config.get_config_value('metadata:main', 'identification_abstract'):
            service_ident_doc.append(
                OWS.Abstract(config.get_config_value('metadata:main', 'identification_abstract')))

        if config.get_config_value('metadata:main', 'identification_keywords'):
            keywords_doc = OWS.Keywords()
            for k in config.get_config_value('metadata:main', 'identification_keywords').split(','):
                if k:
                    keywords_doc.append(OWS.Keyword(k))
            service_ident_doc.append(keywords_doc)

        if config.get_config_value('metadata:main', 'identification_keywords_type'):
            keywords_type = OWS.Type(config.get_config_value('metadata:main', 'identification_keywords_type'))
            keywords_type.attrib['codeSpace'] = 'ISOTC211/19115'
            keywords_doc.append(keywords_type)

        service_ident_doc.append(OWS.ServiceType('WPS'))

        # TODO: set proper version support
        service_ident_doc.append(OWS.ServiceTypeVersion('1.0.0'))

        service_ident_doc.append(
            OWS.Fees(config.get_config_value('metadata:main', 'identification_fees')))

        for con in config.get_config_value('metadata:main', 'identification_accessconstraints').split(','):
            service_ident_doc.append(OWS.AccessConstraints(con))

        if config.get_config_value('metadata:main', 'identification_profile'):
            service_ident_doc.append(
                OWS.Profile(config.get_config_value('metadata:main', 'identification_profile')))

        doc.append(service_ident_doc)

        # Service Provider
        service_prov_doc = OWS.ServiceProvider(
            OWS.ProviderName(config.get_config_value('metadata:main', 'provider_name')))

        if config.get_config_value('metadata:main', 'provider_url'):
            service_prov_doc.append(OWS.ProviderSite(
                {'{http://www.w3.org/1999/xlink}href': config.get_config_value('metadata:main', 'provider_url')})
            )

        # Service Contact
        service_contact_doc = OWS.ServiceContact()

        # Add Contact information only if a name is set
        if config.get_config_value('metadata:main', 'contact_name'):
            service_contact_doc.append(
                OWS.IndividualName(config.get_config_value('metadata:main', 'contact_name')))
            if config.get_config_value('metadata:main', 'contact_position'):
                service_contact_doc.append(
                    OWS.PositionName(config.get_config_value('metadata:main', 'contact_position')))

            contact_info_doc = OWS.ContactInfo()

            phone_doc = OWS.Phone()
            if config.get_config_value('metadata:main', 'contact_phone'):
                phone_doc.append(
                    OWS.Voice(config.get_config_value('metadata:main', 'contact_phone')))
            if config.get_config_value('metadata:main', 'contaact_fax'):
                phone_doc.append(
                    OWS.Facsimile(config.get_config_value('metadata:main', 'contact_fax')))
            # Add Phone if not empty
            if len(phone_doc):
                contact_info_doc.append(phone_doc)

            address_doc = OWS.Address()
            if config.get_config_value('metadata:main', 'deliveryPoint'):
                address_doc.append(
                    OWS.DeliveryPoint(config.get_config_value('metadata:main', 'contact_address')))
            if config.get_config_value('metadata:main', 'city'):
                address_doc.append(
                    OWS.City(config.get_config_value('metadata:main', 'contact_city')))
            if config.get_config_value('metadata:main', 'contact_stateorprovince'):
                address_doc.append(
                    OWS.AdministrativeArea(config.get_config_value('metadata:main', 'contact_stateorprovince')))
            if config.get_config_value('metadata:main', 'contact_postalcode'):
                address_doc.append(
                    OWS.PostalCode(config.get_config_value('metadata:main', 'contact_postalcode')))
            if config.get_config_value('metadata:main', 'contact_country'):
                address_doc.append(
                    OWS.Country(config.get_config_value('metadata:main', 'contact_country')))
            if config.get_config_value('metadata:main', 'contact_email'):
                address_doc.append(
                    OWS.ElectronicMailAddress(
                        config.get_config_value('metadata:main', 'contact_email'))
                )
            # Add Address if not empty
            if len(address_doc):
                contact_info_doc.append(address_doc)

            if config.get_config_value('metadata:main', 'contact_url'):
                contact_info_doc.append(OWS.OnlineResource(
                    {'{http://www.w3.org/1999/xlink}href': config.get_config_value('metadata:main', 'contact_url')})
                )
            if config.get_config_value('metadata:main', 'contact_hours'):
                contact_info_doc.append(
                    OWS.HoursOfService(config.get_config_value('metadata:main', 'contact_hours')))
            if config.get_config_value('metadata:main', 'contact_instructions'):
                contact_info_doc.append(OWS.ContactInstructions(
                    config.get_config_value('metadata:main', 'contact_instructions')))

            # Add Contact information if not empty
            if len(contact_info_doc):
                service_contact_doc.append(contact_info_doc)

            if config.get_config_value('metadata:main', 'contact_role'):
                service_contact_doc.append(
                    OWS.Role(config.get_config_value('metadata:main', 'contact_role')))

        # Add Service Contact only if ProviderName and PositionName are set
        if len(service_contact_doc):
            service_prov_doc.append(service_contact_doc)

        doc.append(service_prov_doc)

        server_href = {'{http://www.w3.org/1999/xlink}href': config.get_config_value('server', 'url')}

        # Operations Metadata
        operations_metadata_doc = OWS.OperationsMetadata(
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get(server_href),
                        OWS.Post(server_href)
                    )
                ),
                name="GetCapabilities"
            ),
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get(server_href),
                        OWS.Post(server_href)
                    )
                ),
                name="DescribeProcess"
            ),
            OWS.Operation(
                OWS.DCP(
                    OWS.HTTP(
                        OWS.Get(server_href),
                        OWS.Post(server_href)
                    )
                ),
                name="Execute"
            )
        )
        doc.append(operations_metadata_doc)

        doc.append(WPS.ProcessOfferings(*process_elements))

        languages = config.get_config_value('server', 'language').split(',')
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

        return doc

    @Request.application
    def __call__(self, request):
        doc = self.get_response_doc()
        return xml_response(doc)
