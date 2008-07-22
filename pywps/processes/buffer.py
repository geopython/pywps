# Author: Luca Casagrande ( luca.casagrande@gmail.com )
# Rewritten by: Jachym Cepicky <jachym les-ejk cz> 
#               According to new process definition style

import os,time,string,sys
from pywps.Process.Process import WPSProcess


class Process(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "buffer",
            title="Buffer",
            version = "0.2",
            storeSupported = "true",
            statusSupported = "true",
            abstract="Create a buffer around an input vector file",
            grassLocation = True)


        self.dataIn = self.addComplexInput(identifier="data",
                             title = "Input data")

        self.widthIn = self.addLiteralInput(identifier = "width",
                             title = "Width")

        self.bufferOut = self.addComplexOutput(identifier="buffer",
                                title="Output buffer file",asReference=True)

        self.textOut = self.addLiteralOutput(identifier="text",
                                title="just some text")
        
    def execute(self):

        self.cmd("g.region -d")

        self.status.set("Importing data",20)
	self.cmd("v.in.ogr dsn=%s output=data" %\
                (self.getInputValue('data')))
            
        self.status.set("Buffering",50)
	self.cmd("v.buffer input=data output=data_buff buffer=%s scale=1.0 tolerance=0.01" %\
                (self.getInputValue('width')))

        self.status.set("Exporting data",90)

	self.cmd("v.out.ogr type=area format=GML input=data_buff dsn=out.xml  olayer=path.xml")
        
        if "out.xml" in os.listdir(os.curdir):
            self.bufferOut.setValue("out.xml")
            self.textOut.setValue("ahoj, svete")
            return
        else:
            return "Output file not created"
