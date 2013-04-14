import types
import logging
import io

namespaces = {
    "ows":"http://www.opengis.net/ows/1.1",
    "wps": "http://www.opengis.net/wps/1.0.0"
}

class Request:
    """ Base request class
    """

    version = None
    request = None
    service = None
    request = None

    validate = False
    lang = "en"

    def parse(self,data):
        """Parses given data
        """

        # parse get request
        if isinstance(data, str):
            kvs = self._parse_params(data)
            self._set_from_url(kvs)
            
        elif isinstance(data, io.IOBase):
            root = self._parse_xml(data)
            self._set_from_xml(root)

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

    def _set_from_url(self,pairs):
        """Set local values from key-value-pairs
        """

        # convert keys to lowercase
        pairs = dict((k.lower(), v) for k, v in pairs.items())
        keys = pairs.keys()
        if "version" in keys:
            self.version = self.pairs["version"]
        else:
            # set default value
            self.version = "1.0.0"

        if "service" in keys:
            self.service = self.pairs["service"]

        if "version" in keys:
            self.version = self.pairs["version"]

        if "language" in keys:
            self.language = keys["language"].lower()

        return pairs
