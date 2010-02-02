from pywps.Process import WPSProcess                                
class Process(WPSProcess):


    def __init__(self):

        ##
        # Process initialization
        WPSProcess.__init__(self,
            identifier = "returner",
            title="Return process",
            abstract="""This is demonstration process of PyWPS, returns
            the same file, it gets on input, as the output.""",
            version = "1.0",
            storeSupported = "true",
            statusSupported = "true")

        ##
        # Adding process inputs
        
        self.dataIn = self.addComplexInput(identifier="data",
                    title="Input vector data",
                    formats = [{'mimeType':'text/xml'}])

        self.textIn = self.addLiteralInput(identifier="text",
                    title = "Some width")

        ##
        # Adding process outputs

        self.dataOut = self.addComplexOutput(identifier="output",
                title="Output vector data",
                formats =  [{'mimeType':'text/xml'}])

        self.textOut = self.addLiteralOutput(identifier = "text",
                title="Output literal data")

    ##
    # Execution part of the process
    def execute(self):

        # just copy the input values to output values
        self.dataOut.setValue( self.dataIn.getValue() )
        self.textOut.setValue( self.textIn.getValue() )

        return
