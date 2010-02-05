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

        self.intOut = self.addLiteralOutput(identifier="int",
                                                 title="Integer data out")
        self.stringOut = self.addLiteralOutput(identifier="string",
                                                 title="String data out",
                                                 type = type(""))
        self.floatOut = self.addLiteralOutput(identifier="float",
                                                 title="Float data out",
                                                 type = type(0.0))
    def execute(self):
        self.intOut.setValue(self.intIn.getValue())
        self.stringOut.setValue(self.stringIn.getValue())
        self.floatOut.setValue(self.floatIn.getValue())

class ComplexProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self, identifier = "complexprocess",
            title="Complex process",
            storeSupported=True)

        self.vectorin = self.addComplexInput(identifier="vectorin",
                                                 title="Vector file")

        self.rasterin = self.addComplexInput(identifier="rasterin",
                                                 title="Raster file",
                                                 formats = [{"mimeType":"image/tiff"}])

        self.pausein = self.addLiteralInput(identifier="pause",
                                                 title="Pause the process",
                                                 abstract="Pause the process for several seconds, so that status=true can be tested",
                                                 default = False,
                                                 type = type(True))

        self.vectorout = self.addComplexOutput(identifier="vectorout",
                                                 title="Vector file")
        self.rasterout = self.addComplexOutput(identifier="rasterout",
                                                 title="Raster file",
                                                 formats = [{"mimeType":"image/tiff"}])
    def execute(self):
        self.vectorout.setValue(self.vectorin.getValue())
        self.rasterout.setValue(self.rasterin.getValue())

        if self.pausein.getValue():
            import time
            for i in range(5):
                self.status.set("Processing process",i*20)
                time.sleep(5)
        return
