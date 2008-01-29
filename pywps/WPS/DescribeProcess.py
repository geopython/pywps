"""
WPS DescribeProcess request handler
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
#               jachym at les-ejk dot cz
# Lince: 
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

from Request import Request
from pywps import processes
from pywps.processes import *

class DescribeProcess(Request):
    """
    Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """

    def __init__(self,wps):
        """
        Arguments:
           self
           wps   - parent WPS instance
        """
        Request.__init__(self,wps)

        self.template = self.templateManager.prepare(self.templateFile)

        #
        # HEAD
        #
        self.templateProcessor.set("encoding",
                                    self.wps.getConfigValue("wps","encoding"))
        self.templateProcessor.set("lang",
                                    self.wps.getConfigValue("wps","lang"))
        self.templateProcessor.set("version",
                                    self.wps.getConfigValue("wps","version"))

        #
        # Processes
        #
        self.templateProcessor.set("Processes",self.processesDescription())

        self.response = self.templateProcessor.process(self.template)

        return

    def processesDescription(self):
        """
        Will return Object with processes description
        """

        processesData = []

        for processName in processes.__all__:
            # skip process, if not requested
            if not processName in self.wps.inputs["identifier"]:
                continue
            process = eval(processName+".Process()")
            processData = {}
            try:
                processData["processok"] = 1
                processData["identifier"] = process.Identifier
                processData["title"] = process.Title
                processData["abstract"] = process.Abstract
                processData["Metadata"] = 0 #TODO
                processData["Profiles"] = process.Profile
                processData["wsdl"] = process.WSDL
                processData["store"] = process.storeSupported
                processData["status"] = process.statusSupported
                processData["version"] = process.processVersion
                processData["Datainputs"] = self.processInputs(process)
                processData["datainpuntslen"] = len(processData["Datainputs"])
            except (Exception,KeyError), e:
                processData["processok",0]
                processData["process",process]
                processData["exception",e]
            processesData.append(processData)
        return processesData

    def processInputs(self,process):
        """
        Will return Object with process inputs
        """

        processInputs = []
        for input in process.Inputs:
            processInput = {}
            processInput["identifier"] = input["Identifier"]
            processInput["title"] = input["Title"]
            processInput["abstract"] = input["Abstract"]
            print input
            processInput["minoccurs"] = input["MinimumOccurs"]
            #processInput["maxoccurs"] = input["MaximumOccurs"]
            #if input["LiteralValue"]:
            #    processInput["literalvalue"] = self.literalValueInput(input["LiteralValue"])
            #if input["ComplexValue"]:
            #    processInput["complexvalue"] = self.complexValueInput(input["ComplexValue"])
            #if input["BoudningBoxValue"]:
            #    processInput["boundingboxvalue"] = self.bboxValueInput(input["BoudningBoxValue"])
            processInputs.append(processInput)
        return processInputs
    
    def literalValueInput(self,literalData):

        literalValue = {}
        literalValue
        return  literalValue

    def complexValueInput(self,bboxData):
        complexValue = {}
        return complexValue

    def bboxValueInput(self,bboxData):
        bboxValue = {}
        return bboxValue
