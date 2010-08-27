from pywps.Process import WPSProcess                                
class Process(WPSProcess):
     def __init__(self):
          # init process
         WPSProcess.__init__(self,
              identifier = "krigingprocess", # must be same, as filename
              title="Automatic Kriging process",
              version = "0.1",
              storeSupported = "true",
              statusSupported = "true",
              abstract="GML buffer generator according to distance",
              grassLocation =False)
              
         self.InputGML = self.addComplexInput(identifier = "GMLinput points",
                                            title = "GML input points")
         
         self.OutputTiff=self.addComplexOutput(identifier="GMLOutput", 
                                            title="Interpolated grid")
         
        
     def execute(self):
        pass
     
        return