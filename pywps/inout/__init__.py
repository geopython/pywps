class Inout:
    """Basic input-outpu class
    """
    identifier = None
    title = None
    abstract = None
    value = None
    language = None
    maxoccures = 1

    def __init__(self,identifier=None,value=None, title=None, abstract=None):
        if identifier:
            self.identifier = identifier
        if value:
            self.set_value(value)

        if title:
            self.set_title(title)

        if abstract:
            self.set_abstract(abstract)

    def set_title(self,title):
        self.title = title

    def set_abstract(self,abstract, language=None):
        self.abstract = abstract

    def set_value(self,value):
        self.value = value


    def get_value(self):
        """Returns self.value
        """
        return self.value


class Input(Inout):

    default = None

    def parse_url(self,inpt_str):
        """Set value from url
        """
        pass

    def parse_xml(self,node):
        """Set value from xml node
        """
        pass

class Output(Inout):
    pass
