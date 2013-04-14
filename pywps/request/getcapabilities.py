from pywps.request import *

class GetCapabilities(Request):
    """Parser of GetCapabilities
    """

    def parse(self,data):
        """Parse given data
        """
        return super(GetCapabilities, self).parse(data)
        

    def is_valid(self):
        """Returns  self-control of the reuquest - if all necessary variables
        are set"""

        if self.service == "wps" and self.request == "getcapabilities":
            return True
        else:
            return False


    def _set_from_url(self,pairs):
        """Set local values from key-value-pairs
        """

        pairs = super(GetCapabilities,self)._set_from_url(pairs)
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

        return pairs

    def _set_from_xml(self,root):
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

