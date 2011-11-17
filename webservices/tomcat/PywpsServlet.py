"""PyWPS Jython (Java) servlet implementation

.. moduleauthor: Jachym Cepicky 
"""

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


