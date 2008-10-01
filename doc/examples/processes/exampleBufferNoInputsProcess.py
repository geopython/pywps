from pywps.Process.Process import WPSProcess
 
 
class Process(WPSProcess):
    """Main process class"""
    def __init__(self):
        """Process initialization"""
 
        # init process
        WPSProcess.__init__(self,
            identifier = "exampleBufferNoInputsProcess",
            title="BufferNoInputs",
            version = "0.1",
            storeSupported = "true",
            statusSupported = "true",
            abstract="Create a buffer around a fixed vector file",
            grassLocation = "spearfish60")
            #grassLocation = True)
 
        self.bufferOut = self.addComplexOutput(identifier="buffer",
                                title="Output buffer file")
 
    def execute(self):
        """Execute process.
 
        Each command will be executed and output values will be set
        """
 
        # run some command from the command line
        self.cmd("g.region -d")
 
        # set status value
 
        self.status.set("Buffering",50)
        self.cmd("v.buffer input=roads output=roads_buff buffer=100 scale=1.0 tolerance=0.01")
 
        self.status.set("Exporting data",90)
        self.cmd("v.out.ogr type=area format=GML input=roads_buff dsn=out.xml  olayer=path.xml")
 
        # set output values at the end
        self.bufferOut.setValue("out.xml")

        # everything was all right, return None
        return
