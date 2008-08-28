"""This is an example process, which calculates buffer around given vector
file. 

This process uses for its purpose GRASS GIS (http://grass.osgeo.org), and
so it demonstrates the way, how configure GRASS with it as well.

"""
# Author: Luca Casagrande ( luca.casagrande@gmail.com )
# Rewritten by: Jachym Cepicky <jachym les-ejk cz> 
#               According to new process definition style

import os,time,string,sys
from pywps.Process.Process import WPSProcess


class Process(WPSProcess):
    """Main process class"""
    def __init__(self):
        """Process initialization"""

        # init process
        WPSProcess.__init__(self,
            identifier = "buffer",
            title="Buffer",
            version = "0.2",
            storeSupported = "true",
            statusSupported = "true",
            abstract="Create a buffer around an input vector file",
            grassLocation = True)

        # define inputs
        self.dataIn = self.addComplexInput(identifier="data",
                             title = "Input data")

        self.widthIn = self.addLiteralInput(identifier = "width",
                             title = "Width")

        self.bufferOut = self.addComplexOutput(identifier="buffer",
                                title="Output buffer file")

        # define outputs
        self.textOut = self.addLiteralOutput(identifier="text",
                                title="just some text")
        
    def execute(self):
        """Execute process.
        
        Each command will be executed and output values will be set
        """

        # run some command from the command line
        self.cmd("g.region -d")

        # set status value
        self.status.set("Importing data",20)
	self.cmd("v.in.ogr dsn=%s output=data" %\
                (self.getInputValue('data')))
            
        self.status.set("Buffering",50)
	self.cmd("v.buffer input=data output=data_buff buffer=%s scale=1.0 tolerance=0.01" %\
                (self.getInputValue('width')))

        self.status.set("Exporting data",90)

	self.cmd("v.out.ogr type=area format=GML input=data_buff dsn=out.xml  olayer=path.xml")
        
        # controll
        if "out.xml" in os.listdir(os.curdir):

            # set output values at the end
            self.bufferOut.setValue("out.xml")
            self.textOut.setValue("ahoj, svete")

            # everything was all right, return None
            return
        else:
                
            # in case, something went wrong, return string
            return "Output file not created"
