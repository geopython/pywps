from pywps.request import *

class DescribeProcess(Request):
    """Parser of DescribeProcess
    """

    request="describeprocess"
    identifiers=None
    version = None

    def set_from_url(self,pairs):
        """Set local values from key-value-pairs
        """

        Request.set_from_url(self,pairs)

        self.identifiers = pairs["identifier"].split(",")

        return pairs

    def set_from_xml(self,root):
        """Set local values from xml encoded request (using objectify)
        """
        global namespaces

        Request.set_from_xml(self,root)

        self.identifiers = []

        [self.__parse_identifier(i) for i in root.xpath("ows:Identifier", namespaces = namespaces)]

        self.version = root.attrib["version"]

    def __parse_identifier(self,node):
        
        self.identifiers.append(node.text)
