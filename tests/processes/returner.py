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

        ##
        # Process initialization
        WPSProcess.__init__(self,
            identifier = "returner",
            title="Return process",
            abstract="""This is demonstration process of PyWPS, returns the same file, it gets on input, as the output.""",
            version = "1.0",
            storeSupported = True,
            statusSupported = True)

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
