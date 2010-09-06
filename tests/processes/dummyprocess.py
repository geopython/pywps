"""
DummyProcess to check the WPS structure

Author: Jorge de Jesus (jorge.de-jesus@jrc.it) as suggested by Kor de Jong
"""
from pywps.Process import WPSProcess                                
class Process(WPSProcess):
     def __init__(self):
          # init process
         WPSProcess.__init__(self,
              identifier = "dummyprocess", # must be same, as filename
              title="Dummy Process",
              version = "0.1",
              storeSupported = "true",
              statusSupported = "true",
              abstract="The Dummy process is used for testing the WPS structure. The process will accept 2 input numbers and will return the XML result with an add one and subtract one operation",
              grassLocation =False)
              
         self.Input1 = self.addLiteralInput(identifier = "input1",
                                            title = "Input1 number", 
                                            default="100")
         self.Input2= self.addLiteralInput(identifier="input2", 
                                           title="Input2 number", 
                                          default="200")
         self.Output1=self.addLiteralOutput(identifier="output1", 
                                            title="Output1 add 1 result")
         self.Output2=self.addLiteralOutput(identifier="output2",title="Output2 subtract 1 result" )                                   
     def execute(self):
         
        self.Output1.setValue(self.Input1.getValue()+1)
        self.Output2.setValue(self.Input1.getValue()-1)
        return
