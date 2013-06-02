from pywps.inout import *
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
            #logging.debug("Literal value [%s] set to [%s] (integer)" %(self.identifier, self.value))
        elif self.datatype == "float":
            self.value = float(value)
            #logging.debug("Literal value [%s] set to [%s] (float)" %(self.identifier, self.value))
        elif self.datatype == "string":
            self.value = str(value)
            #logging.debug("Literal value [%s] set to [%s] (string)" %(self.identifier, self.value))
        else:
            self.value = None
            #logging.debug("Literal value set to None due to unmatched data type")
        return self.value

    def get_value(self):
        """Return value of the input
        """
        return self.value

    def set_datatype(self,datatype):
        """Set data type and convert current value to it"""

        if datatype in ["int","float","string"] and self.value is not None:
            self.datatype = datatype
            self.set_value(self.value)


class LiteralOutput(Literal,Output):
    """Literal output object"""
    pass
