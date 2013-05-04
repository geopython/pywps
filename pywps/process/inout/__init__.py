class Inout:
    """Basic input-outpu class
    """
    identifier = None
    title = None
    abstract = None
    value = None

    def __init__(self,identifier):
        self.identifier = identifier

    def set_title(self,title):
        self.title =  title

    def set_abstract(self,abstract):
        self.abstract =  abstract

    def set_value(self,value):
        self.value = value

    def set_from_url(self,inpt_str):
        """Set value from url key-value pairs
        """
        pass

    def get_value(self):
        """Returns self.value
        """
        return self.value

    def set_from_xml(self,node):
        """Set value from xml node
        """
        pass

class Input(Inout):
    pass

    def set_from_url(self,inpt_str):
        pass

    def set_from_xml(self,node):
        pass

class Output(Inout):
    pass
