from pywps.request import *
from pywps.request.execute.input import Input

class Execute(Request):
    """Parser of Execute
    """

    request="execute"
    identifier=None
    inputs = None

    def set_from_url(self,pairs):
        """Set local values from key-value-pairs
        """
        Request.set_from_url(self,pairs)

        self.identifier = pairs["identifier"]
        if "datainputs" in pairs.keys():
            self.inputs = self.__get_inputs(pairs["datainputs"])
        else:
            self.inputs = []

    def __get_inputs(self,datainputs):
        """Create list of inputs based on datainputs parameter strings
        """

        inputs = []

        inputs_in = datainputs.split(";")

        # Create new Input object and use it's 'set_from_url' method
        for inpt_in in inputs_in:
            inpt = Input()
            inpt.set_from_url(inpt_in)
            inputs.append(inpt)

        return inputs


    def set_from_xml(self,root):
        """Set local values from key-value-pairs
        """

        global namespaces
        Request.set_from_xml(self,root)

