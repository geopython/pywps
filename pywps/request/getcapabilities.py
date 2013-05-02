from pywps.request import *

class GetCapabilities(Request):
    """Parser of GetCapabilities
    """

    version = "1.0.0"
    request = "getcapabilities"

    def is_valid(self):
        """Returns  self-control of the reuquest - if all necessary variables
        are set"""

        if self.service == "wps" and self.request == "getcapabilities":
            return True
        else:
            return False


    def set_from_url(self,pairs):
        """Set local values from key-value-pairs
        """

        Request.set_from_url(self,pairs)

        return pairs

    def set_from_xml(self,root):
        """Set local values from xml encoded request (using objectify)
        """
        global namespaces

        Request.set_from_xml(self,root)

        if hasattr(root,"AcceptVersions"):
            self.acceptversions = root.AcceptVersions.xpath("ows:Version",
                        namespaces = namespaces)
            self.version = self.acceptversions[0]

