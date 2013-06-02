from pywps.inout import *

class Complex:
    """Basic complex input or output object"""
    type = "complex"
    value = None
    mimetype = None
    encoding = None
    schema = None

    def set_value(self, value):
        self.value = value

    def get_encoding(self):

        return self.encoding

    def get_schema(self):

        return self.schema

    def get_mimetype(self):

        return self.mimetype

    def set_encoding(self,encoding):

        self.encoding = encoding

    def set_schema(self, schema):

        self.schema = schema

    def set_mimetype(self,mimetype):

        self.mimetype = mimetype


class ComplexOutput(Complex,Output):
    """Complex output object"""
    pass
