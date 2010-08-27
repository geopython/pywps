from pywps.Process import WPSProcess                                
class Process(WPSProcess):
     def __init__(self):
          # init process
         WPSProcess.__init__(self,
              identifier = "GMLBuffer", # must be same, as filename
              title="GMBufferPolygon",
              version = "0.1",
              storeSupported = "true",
              statusSupported = "true",
              abstract="GML buffer generator according to distance",
              grassLocation =False)
              
         self.Input1 = self.addComplexInput(identifier = "GmlUrlResource",
                                            title = "URL with GML content")
         self.Input2= self.addLiteralInput(identifier="Distance", 
                                           title="Distance of buffer", 
                                          default="10")
         self.Output1=self.addComplexOutput(identifier="GMLOutput", 
                                            title="buffered output")
        
     def execute(self):
        pass
     
        return