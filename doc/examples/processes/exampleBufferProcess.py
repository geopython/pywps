from pywps.Process.Process import WPSProcess


class Process(WPSProcess):
    """Main process class"""
    def __init__(self):
        """Process initialization"""

        # init process
        WPSProcess.__init__(self,
            identifier = "exampleBufferProcess",
            title="Buffer",
            version = "0.2",
            storeSupported = "true",
            statusSupported = "true",
            abstract="Create a buffer around an input vector file",
            grassLocation = True)

        # process inputs

        # complex input
        self.dataIn = self.addComplexInput(identifier="data",
                            title = "Input data",
                            # some optional parameters
                            abstract="Input data in GML format", # default is empty
                            metadata=[{"foo":"bar"}], # default is empty
                            formats=[{"mimeType":"text/xml"}], # default value
                            maxOccurs=1, # default value
                            maxmegabites="5") # default maximum size

        # string input
        self.widthIn = self.addLiteralInput(identifier = "width",
                             title = "Width",abstract="buffer width",
                             maxOccurs=3)

        # bbox input
        self.bboxIn = self.addBBoxInput(identifier = "bbox",
                             title = "Bounding box for buffering",minOccurs=0)

        # process outputs    

        # complex output
        self.bufferOut = self.addComplexOutput(identifier="buffer",
                                title="Output buffer file")

        # literal output
        self.textOut = self.addLiteralOutput(identifier="text",
                                title="Just some literal output")

        # bbox output
        self.bboxOut = self.addBBoxOutput(identifier="bbox",
                                title="Resulting bbox")
        
    def execute(self):
        """Execute process.
        
        Each command will be executed and output values will be set
        """

        # run some command from the command line
        self.cmd(["g.region","-d"])

        # import data
        self.status.set("Importing data",20)
	out = self.cmd(["v.in.ogr","-o","dsn=%s" % (self.getInputValue('data')),"output=data"])
	self.cmd(["g.region","vect=data"])

        # buffer
        self.status.set("Buffering",50)
	self.cmd(["v.buffer","input=data","output=data_buff","distance=%s"%self.widthIn.getValue()[0],
                "scale=1.0","tolerance=0.01"])

        # vector -> raster
        self.status.set("Vector to raster conversion",70)
        if self.bboxIn.minx == None:
            self.cmd(["g.region","vect=data_buff"])
        else:
            self.cmd(["g.region",
                "e=%s" % self.bboxIn.minx,
                "s=%s" % self.bboxIn.miny,
                "w=%s" % self.bboxIn.maxx,
                "n=%s" % self.bboxIn.maxx])
	self.cmd(["v.to.rast","use=cat","input=data_buff","output=buff","type=area"]) 

        # export
        self.status.set("Exporting data",90)
	self.cmd(["v.out.ogr","type=area","format=GML","input=data_buff","dsn=out.xml","olayer=path.xml"])

        north = south = east = west = 0
        for l in self.cmd(["v.info","-g","data_buff"]).split("\n"):
            coord=l.split("=")
            if coord[0] == "north":
                north = coord[1]
            elif coord[0] == "west":
                west = coord[1]
            elif coord[0] == "east":
                east = coord[1]
            elif coord[0] == "south":
                south = coord[1]

        self.bboxOut.setValue([west,south,east,north])

        # setting output values
        self.bufferOut.setValue("out.xml")
        self.textOut.setValue("hallo, world")
