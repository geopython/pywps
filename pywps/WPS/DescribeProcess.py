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
import os
import types

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

        for processName in self.processes.__all__:
            # skip process, if not requested
            if not processName in self.wps.inputs["identifier"]:
                continue

            processData = {}
            try:
                module = __import__(self.processes.__name__,fromlist=[processName])
                process = eval("module."+processName+".Process()")

                processData["processok"] = 1
                processData["identifier"] = process.identifier
                processData["title"] = process.title
                processData["abstract"] = process.abstract
                processData["Metadata"] = 0 #TODO
                processData["Profiles"] = process.profile
                processData["wsdl"] = process.wsdl
                processData["store"] = process.storeSupported
                processData["status"] = process.statusSupported
                processData["version"] = process.version
                processData["Datainputs"] = self.processInputs(process)
                processData["datainpuntslen"] = len(processData["Datainputs"])
            except Exception, e:
                processData["processok"] = 0
                processData["process"] = process
                processData["exception"] = e
            processesData.append(processData)
        return processesData

    def processInputs(self,process):
        """
        Will return Object with process inputs
        """

        processInputs = []
        for identifier in process.inputs:
            processInput = {}
            input = process.inputs[identifier]
            processInput["identifier"] = identifier
            processInput["title"] =     input.title
            processInput["abstract"] =  input.abstract
            processInput["minoccurs"] = input.minOccurs
            processInput["maxoccurs"] = input.maxOccurs
            if input.type == "LiteralValue":
                processInput["literalvalue"] = 1
                self.literalValueInput(input,processInput)
            if input.type == "ComplexValue":
                processInput["complexvalue"] = 1
                self.literalValueInput(input,processInput)
            if input.type == "BoudningBoxValue":
                processInput["boundingboxvalue"] = 1
                self.literalValueInput(input,processInput)
            processInputs.append(processInput)
        return processInputs
    
    def literalValueInput(self,input,processInput):


        # data types
        if input.dataType == types.StringType:
            processInput["dataTypeReference"] = \
                                    "http://www.w3.org/TR/xmlschema-2/#string"
            processInput["dataType"] = "string"
        elif input.dataType == types.FloatType:
            processInput["dataTypeReference"] = \
                                    "http://www.w3.org/TR/xmlschema-2/#float"
            processInput["dataType"] = "float"
        elif input.dataType == types.IntType:
            processInput["dataTypeReference"] =\
                                    "http://www.w3.org/TR/xmlschema-2/#integer"
            processInput["dataType"] = "integer"
        elif input.dataType == types.BooleanType:
            processInput["dataTypeReference"] = \
                                    "http://www.w3.org/TR/xmlschema-2/#boolean"
            processInput["dataType"] = "boolean"
        else:
            # FIXME
            pass
        
        # UOMs
        if len(input.uoms) > 0:
            processInput["UOM"] = 1
            processInput["defaultUOM"] = input.uoms[0]
        if len(input.uoms) > 1:
            supportedUOMS = []
            for uom in input.uoms:
                supportedUOMS.append({"uom":uom})
            processInput["supportedUOMS"] = supportedUOMS
            processInput["UOM"] = 1

        # allowed values
        if "*" in input.values:
            processInput["anyvalue"] = 1
        else:
            processInput["allowedValueslen"] = 1
            processInput["allowedValues"] = []
            for val in input.values:
                valrecord = {}
                if type(val) == type([]):
                    valrecord["minMax"] = 1
                    valercord["minimumValue"] = val[0]
                    valercord["maximumValue"] = val[-1]
                    valercord["spacing"] = input.spacing
                else:
                    valrecord["discrete"] = 1
                    valrecord["value"] = val
        # FIXME
        # value reference

        return

    def complexValueInput(self,bboxData,processInput):
        complexValue = {}
        return complexValue

    def bboxValueInput(self,bboxData,processInput):
        bboxValue = {}
        return bboxValue
