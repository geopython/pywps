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

from pywps.Wps import Request
from pywps import config
from pywps.Template import TemplateError
import os,types,traceback
import logging

LOGGER = logging.getLogger(__name__)

class DescribeProcess(Request):
    """
    Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """

    def __init__(self,wps,processes=None):
        """
        Arguments:
           self
           wps   - parent WPS instance
        """
        Request.__init__(self,wps,processes)

        #
        # HEAD
        #
        self.templateProcessor.set("encoding",
                                    config.getConfigValue("wps","encoding"))
        self.templateProcessor.set("lang",
                                    self.wps.inputs["language"])

        #
        # Processes
        #

        self.templateProcessor.set("Processes",self.processesDescription())
        self.response = self.templateProcessor.__str__()

        return

    def processesDescription(self):
        """Format process description block

        :return: dictionary, which is to be used for
            :func:`pywps.Template.TemplateProcessor.set`
        """

        processesData = []

        # Import processes
        for process in self.getProcesses(self.wps.inputs["identifier"]):
            processData = {}
            process.lang.setCode(self.wps.inputs["language"])

            processData["processok"] = 1
            processData["identifier"] = process.identifier
            processData["title"] = process.i18n(process.title)
            if process.abstract:
                processData["abstract"] = process.i18n(process.abstract)
            if process.metadata:
                processData["Metadata"] = self.formatMetadata(process)
            if process.profile:
                profiles=[]
                if type(process.profile) == types.ListType:
                    for profile in process.profile:
                        profiles.append({"profile":profile})
                else:
                    profiles.append({"profile":process.profile})
                processData["Profiles"] = profiles
            if process.wsdl:
                processData["wsdl"] = process.wsdl
            if process.storeSupported == True:
                processData["store"] = 'true'
            else:
                processData["store"] = 'false'
            if process.statusSupported == True:
                processData["status"] = 'true'
            else:
                processData["status"] = 'false'
            if process.version:
                processData["processversion"] = process.version

            processData["Datainputs"] = self.processInputs(process)
            processData["datainputslen"] = len(processData["Datainputs"])

            processData["Dataoutputs"] = self.processOutputs(process)
            processData["dataoutputslen"] = len(processData["Dataoutputs"])
            processesData.append(processData)
        return processesData

    def processInputs(self,process):
        """Format process inputs block

        :return: dictionary, which is to be used for
            :func:`pywps.Template.TemplateProcessor.set`
        """
        
        processInputs = []
        for identifier in process.inputs:
            processInput = {}
            input = process.inputs[identifier]
            processInput["identifier"] = identifier
            processInput["title"] =  process.i18n(input.title)
            processInput["abstract"] = process.i18n(input.abstract)
            processInput["minoccurs"] = input.minOccurs
            if input.metadata:
                processInput["metadata"]=input.metadata
            try:
                if input.default:
                    processInput["minoccurs"] = 0
            except Exception:
                pass
            processInput["maxoccurs"] = input.maxOccurs
            if input.type == "LiteralValue":
                processInput["literalvalue"] = 1
                self.literalValue(input,processInput)
            if input.type == "ComplexValue":
                processInput["complexvalue"] = 1
                self.complexValue(input,processInput)
            if input.type == "BoundingBoxValue":
                processInput["boundingboxvalue"] = 1
                self.bboxValue(input,processInput)
            processInputs.append(processInput)
        return processInputs

    def processOutputs(self,process):
        """Format process outputs block

        :return: dictionary, which is to be used for
            :func:`pywps.Template.TemplateProcessor.set`
        """

        processOutputs = []
        for identifier in process.outputs:
            processOutput = {}
            output = process.outputs[identifier]
            processOutput["identifier"] = identifier
            processOutput["title"] =     process.i18n(output.title)
            processOutput["abstract"] =  process.i18n(output.abstract)
            if output.metadata:
                processOutput["metadata"]=output.metadata
            if output.type == "LiteralValue":
                processOutput["literalvalue"] = 1
                self.literalValue(output,processOutput)
            if output.type == "ComplexValue":
                processOutput["complexvalue"] = 1
                self.complexValue(output,processOutput)
            if output.type == "BoundingBoxValue":
                processOutput["boundingboxvalue"] = 1
                self.bboxValue(output,processOutput)
            processOutputs.append(processOutput)
        return processOutputs

    def literalValue(self,inoutput,processInOutput):
        """Format literal value attributes

        :param inoutput: :class:`pywps.Process.InAndOutputs.Input` or 
            :class:`pywps.Process.InAndOutputs.Output`

        :param processInOutput: dictionary, where to store the parameters
            in 
        """

        # data types
        dataTypeReference = self.getDataTypeReference(inoutput)
        processInOutput["dataType"] = dataTypeReference["type"]
        processInOutput["dataTypeReference"] = dataTypeReference["reference"]

        # UOMs
        if inoutput.uom:
            processInOutput["UOM"] = 1
            processInOutput["defaultUOM"] = inoutput.uom

        if len(inoutput.uoms) > 0:
            supportedUOMS = []
            for uom in inoutput.uoms:
                supportedUOMS.append({"uom":uom})
            processInOutput["supportedUOMS"] = supportedUOMS
            processInOutput["UOM"] = 1

        # default values
        if type(inoutput.default)!=type(None):
            processInOutput["isDefaultValue"] = 1
            processInOutput["defaultValue"] = inoutput.default
            
        # allowed values
        # NOTE: only for inputs, but does not matter
        try:
            if "*" in inoutput.values:
                processInOutput["anyvalue"] = 1
            else:
                processInOutput["allowedValueslen"] = 1
                processInOutput["allowedValues"] = []
                for val in inoutput.values:
                    valrecord = {}
                    if type(val) == type([]):
                        valrecord["minMax"] = 1
                        valrecord["minimumValue"] = val[0]
                        valrecord["maximumValue"] = val[-1]
                        valrecord["spacing"] = inoutput.spacing
                    else:
                        valrecord["discrete"] = 1
                        valrecord["value"] = val
                    processInOutput["allowedValues"].append(valrecord)
                    LOGGER.debug(str(processInOutput["allowedValues"]))
        except AttributeError:
            pass

        return

    def complexValue(self,inoutput,processInOutput):
        """Format complex value attributes, it also changes None format to application/x-empty

        :param inoutput: :class:`pywps.Process.InAndOutputs.Input` or 
            :class:`pywps.Process.InAndOutputs.Output`

        :param processInOutput: dictionary, where to store the parameters
            in 
        """

        processInOutput["mimetype"] = inoutput.formats[0]["mimeType"]
        processInOutput["encoding"] = inoutput.formats[0]["encoding"]
        processInOutput["schema"] = inoutput.formats[0]["schema"]

        processInOutput["Formats"] = []
        for format in inoutput.formats:
            processInOutput["Formats"].append({
                                        "mimetype":format["mimeType"],
                                        "encoding":format["encoding"],
                                        "schema":format["schema"]
                                            })
        #Check for None values, that are replaces by application/x-empty
        if processInOutput["mimetype"] is None:
            processInOutput["mimetype"]="application/x-empty"
        
        #Jmdj: format["mimetype"] is None --> FILTER ; for format in processInOutput["Formats"] --> INTERACTOR
        #format.__setitem__("mimetype","application/x-empty") --> SETTING KEY,VALUE (it cant'be format["mimetype"]="foo")
        [format.__setitem__("mimetype","application/x-empty") for format in processInOutput["Formats"] if format["mimetype"] is None]
        
        return

    def bboxValue(self,input,processInput):
        """Format bboxValue value attributes

        :param inoutput: :class:`pywps.Process.InAndOutputs.Input` or 
            :class:`pywps.Process.InAndOutputs.Output`

        :param processInOutput: dictionary, where to store the parameters
            in 
        """
        processInput["crs"] = input.crss[0]

        processInput["CRSs"] = []
        for crs in input.crss:
            processInput["CRSs"].append({"crs":crs})

        return


