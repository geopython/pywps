from pywps.process.inout import *
import logging

class Literal:
    """Basic literal input or output object"""

    # allowed values: integer, float, string
    datatype = "int"
    uom = None

    type = "literal"

    def set_value(self,value):
        """Set local value
        datatype is taken into account
        """

        # safe way of converting into proper type
        if self.datatype == "int":
            self.value = int(value)
            logging.debug("Literal input value [%s] set to [%s] (integer)" %(self.identifier, self.value))
        elif self.datatype == "float":
            self.value = float(value)
            logging.debug("Literal input value [%s] set to [%s] (float)" %(self.identifier, self.value))
        elif self.datatype == "string":
            self.value = str(value)
            logging.debug("Literal input value [%s] set to [%s] (string)" %(self.identifier, self.value))
        else:
            self.value = None
            logging.debug("Literal input value set to None due to unmatched data type")
        return self.value

    def set_datatype(self,datatype):
        """Set data type and convert current value to it"""

        if datatype in ["int","float","string"] and self.value is not None:
            self.datatype = datatype
            self.set_value(self.value)


class LiteralInput(Literal,Input):
    """Literal input object"""

    def set_from_url(self,inpt_str):
        """Set input value based on input string
        """
        # identifier=value[@uom=m[@datatype=int]]


        # [identifier, value[@uom=m[@datatype=int]]
        (identifier, value) = inpt_str.split("=",1)

        # [value, @uom=m[@datatype=int]]
        attributes = {}
        if inpt_str.find("@") > -1:
            (value, attributes) = value.split("@",1)

        if attributes:
            attributes = dict(a.split("=") for a in attributes.split("@"))

            if "uom" in attributes:
                self.uom = attributes["uom"]

            # TODO: datatype should be set by process author - not by the client
            # if "datatype" in attributes:
            #     self.set_datatype(attributes["datatype"])

        self.set_value(value)

    def set_from_xml(self,node):
        """Set input value based on input node
        """
        value = node.Data.LiteralData
        if "uom" in node.Data.LiteralData.attrib:
            self.uom = node.Data.LiteralData.attrib["uom"]

        # TODO: datatype should be set by process author - not by the client
        #if "dataType" in node.Data.LiteralData.attrib:
        #    self.dataType = node.Data.LiteralData.attrib["dataType"]

        self.set_value(value)

class LiteralOutput(Literal,Output):
    """Literal output object"""
    pass
