from pywps.process.inout import *
from pywps.process.inout.reference import Reference

from lxml import etree
from pywps import namespaces

class Complex:
    """Basic complex input or output object"""
    type = "complex"
    pass

class ComplexInput(Complex,Input):
    """Complex input object"""

    reference = None

    mimetype = None
    encoding = None
    schema = None

    value = None

    def set_value(self,value):
        """Set complex value

        value = fileObject
        value = String
        value = Bytes
        """

        self.value = value

    def set_from_url(self, inpt_str):
        """Parse reference input from KVP http GET
        """

        attribs = inpt_str.split("@")

        parsed_vals = {}

        # identify, if the input value is not URL by chance
        idx = 0
        if not inpt_str.find("@") == 0:
            idx = 1
            if attribs[0].find("http://") == 0:
                parsed_vals["href"] = attribs[0]
            else:
                parsed_vals["value"] = attribs[0]

        # parse attributes
        for a in attribs[idx:]:

            if not a: continue # there might be empty value

            (k,v) = a.split("=")

            if k.lower() == "href" or\
               k.lower() == "xlink:href":
                parsed_vals["href"] = v

            else:
                parsed_vals[k.lower()] = v

        parsed_keys = parsed_vals.keys()

        # check for reference
        if "href" in parsed_keys:
            self.reference = Reference(parsed_vals["href"])

        if "schema" in parsed_keys:
            self.schema = parsed_vals["schema"]

        if "encoding" in parsed_keys:
            self.encoding = parsed_vals["encoding"]

        if "mimetype" in parsed_keys:
            self.mimetype = parsed_vals["mimetype"]
        
        if "value" in parsed_keys:
            self.setValue(parsed_vals["value"])

    def set_from_xml(self, node):
        """Parse complex input node
        """

        attribs = node.attrib.keys()

        if "mimeType" in attribs:
            self.mimetype = node.attrib["mimeType"]

        if "schema" in attribs:
            self.schema = node.attrib["schema"]

        if "encoding" in attribs:
            self.encoding = node.attrib["encoding"]

        # parse reference
        if node.tag == "{%s}Reference"%namespaces["wps"]:
            self._set_from_xml_reference(node)
        # parse complex input
        elif node.tag == "ComplexValue":
            self._set_from_xml_complex(node)

    def _set_from_xml_complex(self, node):
        pass

    def _set_from_xml_reference(self, node):
        """Set reference value from xml node
        """
        href = None
        method = "GET"
        header = None
        body = None
        bodyref = None
        
        #
        # Attributes
        #

        # href is mandatory, so no check
        href = node.attrib["{%s}href"%namespaces["xlink"]]

        # anything else
        attribs = node.attrib.keys()

        if "method" in attribs:
            method = node.attrib["method"].upper()

        #
        # Child nodes
        #
        if hasattr(node,"Header"):
            from copy import copy
            header = copy(node.Header.attrib)

        if hasattr(node,"Body"):
            body = etree.tostring(node.Body)

        if hasattr(node,"BodyReference"):
            bodyref = node.BodyReference.attrib["{%s}href"%namespaces["xlink"]]

        self.reference = Reference(href, method, header, body,bodyref)

class ComplexOutput(Complex,Output):
    """Complex output object"""
    pass
