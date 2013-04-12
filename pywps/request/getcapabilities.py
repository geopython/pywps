from pywps.request import *

class GetCapabilities(Request):
    """Parser of GetCapabilities
    """

    request="getcapabilities"
    acceptversions = None

    def parse(self,data):
        """Parse given data
        """
        
        import io

        # parse get request
        if isinstance(data, str):
            kvs = self._parse_params(data)
            self.__set_from_url(kvs)
            
        elif isinstance(data, io.IOBase):
            root = self._parse_xml(data)
            self.__set_from_xml(root)

    def is_valid(self):
        """Returns  self-control of the reuquest - if all necessary variables
        are set"""

        if self.service == "wps" and self.request == "getcapabilities":
            return True
        else:
            return False


    def __set_from_url(self,pairs):
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

        if "acceptversions" in keys:
            self.acceptversions = keys["acceptversions"]

        if "language" in keys:
            self.language = keys["language"].lower()

    def __set_from_xml(self,root):
        """Set local values from xml encoded request (using objectify)
        """
        global namespaces
        
        keys = root.attrib.keys()
        if "language" in keys:
            self.lang = root.attrib["language"].lower()

        if hasattr(root,"AcceptVersions"):
            self.acceptversions = root.AcceptVersions.xpath("ows:Version",
                        namespaces = namespaces)
            self.version = self.acceptversions[0]

