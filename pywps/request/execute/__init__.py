from pywps.request import *

class Execute(Request):
    """Parser of Execute
    """

    request="execute"
    identifiers=None
    inputs = None
    outputs = None

    def set_from_url(self,pairs):
        """Set local values from key-value-pairs
        """
        Request.set_from_url(self,pairs)

        return pairs

    def set_from_xml(self,root):
        """Set local values from key-value-pairs
        """

        global namespaces
        Request.set_from_xml(self,root)

