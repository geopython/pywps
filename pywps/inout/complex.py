from pywps.inout import *
from urllib.parse import unquote

class Complex:
    """Basic complex input or output object"""
    type = "complex"
    value = None
    mimetype = None
    encoding = None
    schema = None

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype

    def set_value(self, value):
        self.value = unquote(value)

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

    def get_value(self):
        """Return raw data value
        """
        return self.value

    def get_asfile(self):
        """Return as opened file-like object
        """

        # it's already file
        if hasattr(self.value,"read"):
            return self.value
        # it's file name, open it
        elif os.path.exists(self.value):
            return open(self.value)
        # it's normal string
        else:
            from StringIO import StringIO
            return StringIO(self.value)

class ComplexOutput(Complex,Output):
    """Complex output object"""
    pass
