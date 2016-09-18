"""
DummyProcess to check the WPS structure

Author: Jorge de Jesus (jorge.jesus@gmail.com) as suggested by Kor de Jong
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
              identifier = "dummyprocess", # must be same, as filename
              title="Dummy Process",
              version = "0.1",
              storeSupported = "true",
              statusSupported = "true",
              abstract="The Dummy process is used for testing the WPS structure. The process will accept 2 input numbers and will return the XML result with an add one and subtract one operation",
              grassLocation =False)
              
         self.Input1 = self.addLiteralInput(identifier = "input1",
                                            title = "Input1 number", 
                                            default=100)
         self.Input2= self.addLiteralInput(identifier="input2", 
                                           title="Input2 number", 
                                          default=200)
         self.Output1=self.addLiteralOutput(identifier="output1", 
                                            title="Output1 add 1 result")
         self.Output2=self.addLiteralOutput(identifier="output2",title="Output2 subtract 1 result" )                                   
     def execute(self):
         
        self.Output1.setValue(self.Input1.getValue()+1)
        self.Output2.setValue(self.Input1.getValue()-1)
        return
