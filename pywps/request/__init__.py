import types
import logging

namespaces = {
    "ows":"http://www.opengis.net/ows/1.1",
    "wps": "http://www.opengis.net/wps/1.0.0"
}

class Request:
    """ Base request class
    """

    version = None
    request = None
    service = "wps"
    validate = False
    lang = "en"


    def parse(self,data):
        """Parses given data
        """
        pass

    def is_valid(self):
        """Returns  self-control of the reuquest - if all necessary variables
        are set"""
        return True

    def _parse_xml(self,data):
        """Parse xml tree
        """

        from lxml import etree
        from lxml import objectify
        logging.debug("Continuing with lxml xml etree parser")

        schema = None
        if self.validate:
            schema = etree.XMLSchema(file="pywps/resources/schemas/wps_all.xsd")
        parser = objectify.makeparser(remove_blank_text = True,
                                    remove_comments = True,
                                 schema = schema)
        objects = objectify.parse(data,parser)

        return objects.getroot()

    def _parse_params(self,data):
        """Parse params
        """
        from urllib.parse import parse_qs

        params = parse_qs(data)
        return params
