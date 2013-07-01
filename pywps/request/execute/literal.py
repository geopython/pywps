from pywps.request.execute import Input
from pywps.inout.literal import Literal
from pywps import namespaces

import logging

class LiteralInput(Input):

    datatype = "int"
    uom = None

    def __init__(self,identifier=None,value=None, title=None, abstract=None):
        super(LiteralInput,self).__init__(identifier=identifier , value=value, title=title, abstract= abstract)

    def parse_url(self,inpt_str):
        """Set input value based on input string
        """
        # identifier=value[@uom=m[@datatype=int]]

        # check for max occurs
        if self.check_maxoccurs():
            # continue with parsing
            

            # [identifier, value[@uom=m[@datatype=int]]
            (identifier, value) = inpt_str.split("=",1)

            if self.identifier != identifier:
                raise Exception("Identifiers do not match") # TODO custom exception
            single_literal = Literal()
            single_literal.datatype = self.datatype

            # [value, @uom=m[@datatype=int]]
            attributes = {}
            if inpt_str.find("@") > -1:
                (value, attributes) = value.split("@",1)

            if attributes:
                attributes = dict(a.split("=") for a in attributes.split("@"))

                if "uom" in attributes:
                    single_literal.uom = attributes["uom"]

                # TODO: datatype should be set by process author - not by the client
                # if "datatype" in attributes:
                #     single_literal.set_datatype(attributes["datatype"])

            single_literal.set_value(value)

            self.append(single_literal)

    def get_uom(self,idx=0):
        """Get uom value for specified input
        """
        return self.inputs[idx].uom

    def parse_xml(self,node):
        """Set input value based on input node
        """

        if self.check_maxoccurs():
            value = node.Data.LiteralData
            identifier = node.xpath("ows:Identifier",
                    namespaces=namespaces)[0].text
            if self.identifier != identifier:
                raise Exception("Identifiers do not match") # TODO custom exception
            single_literal = Literal()
            single_literal.datatype = self.datatype
            if "uom" in node.Data.LiteralData.attrib:
                single_literal.uom = node.Data.LiteralData.attrib["uom"]

            # TODO: datatype should be set by process author - not by the client
            #if "dataType" in node.Data.LiteralData.attrib:
            #    single_literal.dataType = node.Data.LiteralData.attrib["dataType"]

            single_literal.set_value(value)

            self.append(single_literal)

    def set_datatype(self,datatype):
        """(re)set data type
        """

        if datatype in ["int","float","string"]:
            self.datatype = datatype
            map(lambda i: i.set_datatype(datatype), self.inputs)
