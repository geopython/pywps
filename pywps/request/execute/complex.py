from pywps.request.execute import Input
from pywps.inout.complex import Complex
from pywps import namespaces
from pywps.inout.reference import Reference
from lxml import etree

import logging

class ComplexInput(Input):
    """Complex input object"""


    def __init__(self,identifier=None,value=None, title=None, abstract=None):
        super(Input,self).__init__(identifier=identifier , value=value, title=title, abstract= abstract)

    def parse_url(self, inpt_str):
        """Parse reference input from KVP http GET
        """

        # check for max occurs
        if self.check_maxoccurs():

            ( identifier,attribs ) = inpt_str.split("=",1)
            attribs = attribs.split("@")

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

                (k,v) = a.split("=",1)

                if k.lower() == "href" or\
                   k.lower() == "xlink:href":
                    parsed_vals["href"] = v

                else:
                    parsed_vals[k.lower()] = v

            parsed_keys = parsed_vals.keys()

            single_complex = ComplexInputSingle()
            # check for reference
            if "href" in parsed_keys:
                single_complex.reference = Reference(parsed_vals["href"])

            if "schema" in parsed_keys:
                single_complex.schema = parsed_vals["schema"]

            if "encoding" in parsed_keys:
                single_complex.encoding = parsed_vals["encoding"]

            if "mimetype" in parsed_keys:
                single_complex.set_mimetype(parsed_vals["mimetype"])

            if "value" in parsed_keys:
                single_complex.set_value(parsed_vals["value"])
            

            self.append(single_complex)

    def parse_xml(self, node):
        """Parse complex input node
        """

        mimetype = None
        schema = None
        encoding = None
        reference = None
        value = None

        # check for max occurs
        if self.check_maxoccurs():
            attribs = node.attrib.keys()

            single_complex = ComplexInputSingle()

            if "mimeType" in attribs:
                mimetype = node.attrib["mimeType"]

            if "schema" in attribs:
                schema = node.attrib["schema"]

            if "encoding" in attribs:
                encoding = node.attrib["encoding"]

            # parse reference
            if node.tag == "{%s}Reference"%namespaces["wps"]:
                reference = self._parse_xml_reference(node)
            # parse complex input
            elif node.tag == "ComplexValue":
                value = self._parse_xml_complex(node)

            single_complex.set_mimetype(mimetype)
            single_complex.set_encoding(encoding)
            single_complex.set_schema(schema)
            single_complex.set_reference(reference)
            single_complex.set_value(value)

            self.append(single_complex)

    def _parse_xml_complex(self, node):
        pass

    def _parse_xml_reference(self, node):
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

        return Reference(href, method, header, body,bodyref)

    def get_reference(self,idx=0):

        return self.inputs[idx].get_reference()

    def get_encoding(self,idx=0):

        return self.inputs[idx].encoding

    def get_schema(self,idx=0):

        return self.inputs[idx].schema

    def get_mimetype(self,idx=0):

        return self.inputs[idx].mimetype

class ComplexInputSingle(Complex):
    reference = None

    def set_reference(self, reference):

        self.reference = reference

    def get_reference(self):

        return self.reference

    def get_reference(self):

        return self.reference



