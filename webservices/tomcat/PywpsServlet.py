"""PyWPS Jython (Java) servlet implementation

.. moduleauthor: Jachym Cepicky 
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

from java.io import *
from javax.servlet.http import HttpServlet 

import pywps
from pywps.Exceptions import *
import traceback
import sys

class PywspServlet(HttpServlet):

    def doGet(self,request,response):

        inputQuery = request.getQueryString()
        if not inputQuery:
            e = NoApplicableCode("Missing request value")
            pywps.response.response(e,response)
        self.doPywps(request, response, inputQuery, pywps.METHOD_GET)

    def doPost(self,request,response):

        inputQuery = request.getQueryString()
        self.doPywps(request, response, inputQuery, pywps.METHOD_POST)

    def doPywps(self,request, response, inputQuery,method):

        # create the WPS object
        try:
            wps = pywps.Pywps(method)
            if wps.parseRequest(inputQuery):
                pywps.debug(wps.inputs)
                wpsresponse = wps.performRequest(processes=[self.getProcesses()])
                if wpsresponse:
                    pywps.response.response(wps.response, response, wps.parser.isSoap,self.wps.parser.isSoapExecute)
        except WPSException,e:
            pywps.response.response(e, response)

    def getProcesses(self):
        """Create temporary Process with literal input and output"""

        from  pywps.Process import WPSProcess

        process = WPSProcess(identifier="servletProcess",
                            title="Java Servlet process")
        process.addLiteralInput(identifier="input",
                            title="Literal input")
        process.addLiteralOutput(identifier="output",
                            title="Literal output")

        def execute():
            self.outputs["output"].setValue(self.inputs["input"].getValue())

        process.execute = execute()

        return process


