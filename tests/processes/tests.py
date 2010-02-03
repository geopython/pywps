from pywps.Process import WPSProcess
class NoInputsProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self, identifier = "noinputsprocess",title="No inputs")

class LiteralProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self, identifier = "literalprocess",
            title="Literal process")

        self.intIn = self.addLiteralInput(identifier="int",
                                                 title="Integer data in")

        self.stringIn = self.addLiteralInput(identifier="string",
                                                 title="String data in",
                                                 type = type(""))

        self.floatIn = self.addLiteralInput(identifier="float",
                                                 title="Float data in",
                                                 type = type(0.0))

        self.intOut = self.addLiteralInput(identifier="int",
                                                 title="Integer data out")
        self.stringOut = self.addLiteralInput(identifier="int",
                                                 title="String data out",
                                                 type = type(""))
        self.floatOut = self.addLiteralInput(identifier="int",
                                                 title="Float data out",
                                                 type = type(0.0))
    def execute(self):
        self.intOut.setValue(self.intIn.getValue())
        self.stringOut.setValue(self.stringIn.getValue())
        self.floatOut.setValue(self.floatIn.getValue())
