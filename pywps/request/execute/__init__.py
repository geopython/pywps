from pywps.request import Request
from pywps import namespaces
from pywps.inout import Input as InoutInput

class Execute(Request):
    """Parser of Execute request
    """

    request="execute"
    identifier=None
    inputs = None

    def __init__(self):

        self.inputs = {}

    def parse_url(self,pairs):
        """Set local values from key-value-pairs
        """
        Request.set_from_url(self,pairs)

        self.identifier = pairs["identifier"]

        self.set_proces(self.get_process(self.identifier))

        if "datainputs" in pairs.keys():
            self.inputs = self.__get_inputs_url(pairs["datainputs"])
        else:
            self.inputs = {}

    def get_process(self, identifier):
        """returns Process object registered to PyWPS
        this process than has inputs and outputs and so it can be use as helper
        for parsing
        """
        pass
        # FIXME TODO

        

    def __get_inputs_url(self,datainputs):
        """Create list of inputs based on datainputs parameter strings
        """

        inputs = {}

        for inpt in datainputs.split(";"):
            (identifier,val) = inpt.split("=")

            # get input type
            intype = self.process.get_input_type(identifier)

            # get parser
            parser = self.process.get_input_parser(intype)

            # create Input
            if not identifier in inputs.keys():
                inputs[identifier] = parser(identifier)

            # add input to Inputs
            inputs[identifier].parse_url(inpt)

        return inputs


    def parse_xml(self,root):
        """Set local values from key-value-pairs
        """

        global namespaces
        Request.parse_xml(self,root)

class Input(InoutInput):

    max_occurs = None
    inputs = []
    value = None

    def __init__(self,identifier=None,value=None, title=None, abstract=None):
        super().__init__(identifier=identifier , value=value, title=title, abstract= abstract)

    def append(self,inpt):
        self.inputs.append(inpt)

    def get_value(self,idx=0):
        """Get one (or first) value of this input
        """
        return self.inputs[idx].get_value()

    def get_values(self):
        """Get all inputs
        """
        
        return map(lambda item: item.get_value(), self)

    def get_input(self,idx=0):

        return self.inputs[idx]

    def check_maxoccurs(self):
        """Check, if the max_occurs parameter was reached
        """

        if self.max_occurs == None:
            return True
        elif self.max_occurs > len(self):
            logging.info("max_occurs %d for input %s reached" % \
                   (self.max_occurs, self.identifier))
            return True
        else: 
            return False

    def __len__(self):
        return len(self.inputs)

    def __iter__(self):
        return self.inputs.__iter__()
