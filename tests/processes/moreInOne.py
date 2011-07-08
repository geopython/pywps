from pywps.Process import WPSProcess

class FirstProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,identifier="complexVector",
                            title="First Process",
                            abstract="Get vector imput and return it to output",
                            statusSupported=True,
                            storeSupported=True)

        self.indata = self.addComplexInput(identifier="indata",title="Complex in",formats=[{"mimeType":"text/xml"},{"mimeType":"application/xml"}],minOccurs=0,maxOccurs=1024)
        self.outdata = self.addComplexOutput(identifier="outdata", title="Complex out",formats=[{"mimeType":"text/xml"}])
        self.outdata2 = self.addComplexOutput(identifier="outdata2", title="Complex out",formats=[{"mimeType":"application/xml"}])
    def execute(self):
        #tmp=self.indata.getValue()
       # import pydevd;pydevd.settrace()
        #self.outdata.setValue(tmp)
       
        #import pydevd;pydevd.settrace()
        self.outdata.setValue(self.indata.getValue()[0])
        self.outdata2.setValue(self.indata.getValue()[0])



class SecondProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,identifier="complexRaster",
                            title="Second Process")

        self.indata = self.addComplexInput(identifier="indata",title="Complex in",
                formats=[{"mimeType":"image/tiff"}],maxmegabites=2)
        self.outdata = self.addComplexOutput(identifier="outdata",
                title="Complex out",formats=[{"mimeType":"image/tiff"}])

    def execute(self):
        self.outdata.setValue(self.indata.getValue())
