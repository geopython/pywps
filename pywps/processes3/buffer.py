# Author: Luca Casagrande ( luca.casagrande@gmail.com )
# Rewritten by: Jachym Cepicky <jachym les-ejk cz> 
#               According to new process definition style

import os,time,string,sys
from pywps.Process import WPSProcess


class Process(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "buffer",
            title="Buffer",
            version = "0.2",
            storeSupported = "true",
            statusSupported = "true",
            abstract="Create a buffer around an input vector file")


        self.addComplexInput(identifier="data",
                             title = "Input data")

        self.addLiteralInput(identifier = "width",
                             title = "Width")

        self.addComplexOutput(identifier="buffer",
                                title="Output buffer file")

        self.addLiteralOutput(identifier="text",
                                title="just some text")
        
    def execute(self):

        self.GCmd("g.region -d")
	    	
        self.SetStatus("Importing data",20)
	self.GCmd("v.in.ogr dsn=%s output=data" %\
                (self.GetInputValue('data')))
            
        self.SetStatus("Buffering",50)
	self.GCmd("v.buffer input=data output=data_buff buffer=%s scale=1.0 tolerance=0.01" %\
                (self.GetInputValue('width')))
            	
        self.SetStatus("Exporting data",90)
	self.GCmd("v.out.ogr type=area format=GML input=data_buff dsn=out.xml  olayer=path.xml")

        
        if "out.xml" in os.listdir(os.curdir):
            self.SetOutputValue('buffer', "out.xml")
            return
        else:
            return "Output file not created"

