from pywps.request import Request
from pywps import namespaces

class Execute(Request):
    """Parser of Execute
    """

    request="execute"
    identifier=None
    inputs = None

    def __init__(self):

        self.inputs = {}

    def set_from_url(self,pairs):
        """Set local values from key-value-pairs
        """
        Request.set_from_url(self,pairs)

        self.identifier = pairs["identifier"]
        if "datainputs" in pairs.keys():
            self.inputs = self.__get_inputs_url(pairs["datainputs"])
        else:
            self.inputs = {}

    def __get_inputs_url(self,datainputs):
        """Create list of inputs based on datainputs parameter strings
        """

        inputs = {}

        for inpt in datainputs.split(";"):
            (identifier,val) = inpt.split("=")

            # get input type
            intype = self.process.get_input_type(identifier)

            # get parser
            parsed_input = self.process.get_input_parser(intype)
            parsed_input.set_from_url(val)

            # create Input
            if not parsed_input.identifier in inputs.keys():
                inputs[parsed_input.identifier] = Input()

            # add input to Inputs
            # TODO: check for maxOccurs
            inputs[parsed_input.identifier].append(parsed_input)

        return inputs


    def set_from_xml(self,root):
        """Set local values from key-value-pairs
        """

        global namespaces
        Request.set_from_xml(self,root)

class Input():

    identifier = None
    inputs = None

    def __init__(self,identifier, inputs=[])

        self.inputs = inputs

    def append(self, inpt):
        self.inpts.append(self.inpts)
    
    def __len__():
        return len(self.inputs)

    def __getitem__(self,key):
        return self.inputs[key]

    def __setitem__(self,key,val):
        self.inputs[key] = val

    def __iter__():
        return self.inputs
