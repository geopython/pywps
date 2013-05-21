from pywps import namespaces
from lxml import etree

class Reference:
    """Basic reference input class
    """

    mimetype = None
    encoding = None
    schema = None
    href = None
    method = "GET"
    header = None
    body = None
    bodyref = None

    def set_from_url(self,inpt_str):
        """Parse reference input from KVP http GET
        """

        attribs = inpt_str.split("@")

        # identify, if the input value is not URL by chance
        idx = 0
        if not inpt_str.find("@") == 0:
            idx = 1
            self.href = attribs[0]

        # parse attributes
        for a in attribs[idx:]:

            if not a: continue # there might be empty value

            (k,v) = a.split("=")

            if k.lower() == "mimetype":
                self.mimetype = v
            elif k.lower() == "encoding":
                self.encoding = v
            elif k.lower() == "schema":
                self.schema = v
            elif k.lower() == "href":
                self.href = v
            elif k.lower() == "method":
                self.method = v.upper()

    def set_from_xml(self, node):
        """Set reference value from xml node
        """
        
        #
        # Attributes
        #

        # href is mandatory, so no check
        self.href = node.attrib["{%s}href"%namespaces["xlink"]]

        # anything else
        attribs = node.attrib.keys()

        if "mimeType" in attribs:
            self.mimetype = node.attrib["mimeType"]

        if "encoding" in attribs:
            self.encoding = node.attrib["encoding"]

        if "schema" in attribs:
            self.schema = node.attrib["schema"]

        if "method" in attribs:
            self.method = node.attrib["method"].upper()

        #
        # Child nodes
        #
        if hasattr(node,"Header"):
            from copy import copy
            self.header = copy(node.Header.attrib)

        if hasattr(node,"Body"):
            self.body = etree.tostring(node.Body)

        if hasattr(node,"BodyReference"):
            self.bodyref = node.BodyReference.attrib["{%s}href"%namespaces["xlink"]]
