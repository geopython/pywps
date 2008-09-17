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

        # complex raster output
        self.bufferRasterOut = self.addComplexOutput(identifier="bufferRaster",
                                title="Output buffer as Raster",
                                formats=[{"mimeType":"image/tiff"},
                                         {"mimeType":"image/png"}])

        # input as png
        self.asPNG = self.addComplexOutput(identifier="asPNG",
                                title="Input file as PNG raster",
                                formats=[{"mimeType":"image/png"}])

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
        self.cmd("g.region -d")

        # import data
        self.status.set("Importing data",20)
	out = self.cmd("v.in.ogr dsn=%s output=data" %\
                (self.getInputValue('data')))
	self.cmd("g.region vect=data")

        # creating output with GRASS PNG driver
        self.cmd("d.mon start=PNG",stdout=False)
        self.cmd("d.vect data")
        self.cmd("d.mon stop=PNG")
        self.asPNG.setValue("map.png")

        # buffer
        self.status.set("Buffering",50)
	self.cmd("v.buffer input=data output=data_buff buffer=%s scale=1.0 tolerance=0.01" %\
                (self.getInputValue('width'))[0])

        # vector -> raster
        self.status.set("Vector to raster conversion",70)
        if self.bboxIn.minx == None:
            self.cmd("g.region vect=data_buff")
        else:
            self.cmd("g.region e=%s s=%s w=%s n=%s" % (self.bboxIn.value))
	self.cmd("v.to.rast use=cat input=data_buff output=buff type=area") 

        # export
        self.status.set("Exporting data",90)
	self.cmd("v.out.ogr type=area format=GML input=data_buff dsn=out.xml  olayer=path.xml")

        # deside, if the user wants PNG or GeoTIFF format
        bufffile = "buffer.png"
        if self.bufferRasterOut.format["mimeType"] == "image/tiff":
            losfile = "buffer.tif"
            self.cmd("r.out.gdal in=buff out=buffer.tif type=Byte")
        else:
            self.cmd("r.out.png in=buff out=buffer.png")
        
        # setting output values
        self.bufferOut.setValue("out.xml")
        self.bufferRasterOut.setValue(bufffile)
        self.textOut.setValue("hallo, world")
