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

class FirstProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,identifier="complexVector",
                            title="First Process",
                            abstract="Get vector imput and return it to output",
                            statusSupported=True,
                            storeSupported=True)

        self.indata = self.addComplexInput(identifier="indata",title="Complex in")
        self.outdata = self.addComplexOutput(identifier="outdata", title="Compex out")
        self.outdata2 = self.addComplexOutput(identifier="outdata2", title="Compex out")
    def execute(self):
        self.outdata.setValue(self.indata.getValue())
        self.outdata2.setValue(self.indata.getValue())


class SecondProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,identifier="complexRaster",
                            version="2.0",
                            title="Second Process")

        self.indata = self.addComplexInput(identifier="indata",title="Complex in",
                formats=[{"mimeType":"image/tiff"}])
        self.outdata = self.addComplexOutput(identifier="outdata",
                title="Compex out",
                formats=[{"mimeType":"image/tiff"}])

    def execute(self):
        self.outdata.setValue(self.indata.getValue())

class ThridProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,identifier="noOutput",
                            title="No output given")
    def execute(self):
        pass
    