"""
The ultimate process to test the status and update capabilities of the server
The processes shoul be requested as follows:
../wps.py?request=execute
&service=wps
&version=1.0.0
&identifier=ultimatequestionprocess
&status=true
&storeExecuteResponse=true

Done by Jorge de Jesus (jorge.mendesdejesus@wur.nl) as suggested by Kor de Jong

"""

from pywps.Process.Process import WPSProcess                                
class Process(WPSProcess):
     def __init__(self):
         # init process
         WPSProcess.__init__(self,
                             identifier="ultimatequestionprocess", #the same as the file name
                             version = "2.0",
                             title="Answer to Life, the Universe and Everything",
                             storeSupported = "false",
                             statusSupported = "false",
                             abstract="Numerical solution that is the answer to Life, Universe and Everything. The process is an improvement to Deep Tought computer (therefore version 2.0) since it no longer takes 7.5 milion years, but only a few seconds to give a response, with an update of status every 10 seconds.",
                             grassLocation =False)
            #No need for inputs since Execute will start the process
         self.Answer=self.addLiteralOutput(identifier = "answer",
                                            title = "The numerical answer to Life, Universe and Everything")

                                           
     def execute(self):
         import time
         
         self.status.set("Preparing....", 0)
         for i in xrange(1, 11):
             time.sleep(5)
             self.status.set("Thinking.....", float(i*10)) 
         #The final answer    
         self.Answer.setValue("42")
        
