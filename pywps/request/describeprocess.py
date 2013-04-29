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

        super(DescribeProcess, self).set_from_url(pairs)

        self.identifiers = pairs["identifier"][0].split(",")

        return pairs

    def set_from_xml(self,root):
        """Set local values from xml encoded request (using objectify)
        """
        global namespaces

        super(DescribeProcess, self).set_from_xml(root)

        self.identifiers = []

        [self.__parse_identifier(i) for i in root.xpath("ows:Identifier", namespaces = namespaces)]

        self.version = root.attrib["version"]

    def __parse_identifier(self,node):
        
        self.identifiers.append(node.text)
