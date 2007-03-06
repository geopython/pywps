from pywps.Wps.process import WPSProcess

class Process(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self)
        self.Identifier = "inputsoutputs"
        self.processVersion = "0.1"
        self.Title="Test input and output structures"
        self.statusSupported="false"
        self.storeSupported="false"
        #self.grassLocation = None

        self.AddLiteralInput("literal","Literal Value","Literal Value",
                    allowedvalues=[[1,10],[20,40],100],MinimumOccurs=3, type=type(0))
        self.AddComplexInput("complexref", "Literal Value Reference", 
                "Complex Value Reference", Formats="image/jpeg",value="http://les-ejk.cz/img/jaja.jpg")
        self.AddBBoxInput("bbox", "Bounding Box Value",value=[0,0,10,10])
        self.AddComplexInput("xml")

        self.AddLiteralOutput("literal", UOMs=["cm"])
        self.AddComplexValueOutput("complexref", Formats="image/jpeg")
        self.AddBBoxOutput("bbox", value=[11,11,14,14.4])
        
    def execute(self):
        self.Outputs[1]['value'] = self.Inputs[1]['value']
        self.Outputs[2]['value'] = [self.Inputs[2]['value'][0],
                                    self.Inputs[2]['value'][1],
                                    self.Inputs[2]['value'][2],
                                    self.Inputs[2]['value'][3]]

        self.Outputs[3]['value'] = self.Inputs[3]['value']
        return 
