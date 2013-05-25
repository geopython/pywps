class Process:
    identifier = None
    title = None
    abstract = None
    language = None
    inputs = {}
    outputs = {}

    __inputs_defs__ = {}
    __outputs_defs__ = {}

    def __init__(self, identifier,
            title = None,
            abstract = None,
            inputs = None,
            outputs = None):

        self.identifier = identifier
        self.title = title
        self.abstract = abstract

    def add_input(self,inpt):
        """Register new input type. 

        inpt - pywps.process.Input
        """

        self.__inputs_defs__[inpt.identifier] = inpt

    def add_output(self,output):
        """Register new output type
        """

        self.__outputs_defs__[output.identifier] = output

    def get_input_type(self, identifier):
        """Returns input type of input registered under given identifier

        identifier - String

        returns "literal", "bbox", "complex" or None
        """

        if identifier in self.__inputs_defs__.keys():
            inpt = self.__inputs_defs__[identifier]

            return inpt.type

        else:
            return None
