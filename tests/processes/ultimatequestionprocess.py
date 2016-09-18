"""
The ultimate process to test the status and update capabilities of the server
The processes shoul be requested as follows:
../wps.py?request=execute
&service=wps
&version=1.0.0
&identifier=ultimatequestionprocess
&status=true
&storeExecuteResponse=true

Done by Jorge de Jesus (jorge.jesus@gmail.com) as suggested by Kor de Jong

"""

# Author:    Jachym Cepicky
#            http://les-ejk.cz
# License: 
#
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from pywps.Process import WPSProcess                               
class Process(WPSProcess):
     def __init__(self):
         # init process
         WPSProcess.__init__(self,
                             identifier="ultimatequestionprocess", #the same as the file name
                             title="Answer to Life, the Universe and Everything",
                             version = "2.0",
                             storeSupported = True,
                             statusSupported = True,
                            abstract="Numerical solution that is the answer to Life, Universe and Everything. The process is an improvement to Deep Tought computer (therefore version 2.0) since it no longer takes 7.5 milion years, but only a few seconds to give a response, with an update of status every 10 seconds.",
                            grassLocation =False)
            #No need for inputs since Execute will start the process
         self.Answer=self.addLiteralOutput(identifier = "answer",
                                            title = "The numerical answer to Life, Universe and Everything")

                                           
     def execute(self):
         import time
         self.status.set("Preparing....", 0)
         for i in xrange(1, 11):
             time.sleep(2)
             self.status.set("Thinking.....", i*10) 
         #The final answer    
         self.Answer.setValue("42")
        
