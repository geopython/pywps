from pywps.Process import WPSProcess

class FirstProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,identifier="complexVector",
                            title="First Process",
                            abstract="Get vector imput and return it to output",
                            statusSupported=True,
                            storeSupported=True)

        self.indata = self.addComplexInput(identifier="indata",title="Complex in")
        self.outdata = self.addComplexOutput(identifier="outdata", title="Compex out")

    def execute(self):
        self.outdata.setValue(self.indata.getValue())



class SecondProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,identifier="second_process",
                            title="Second Process")
