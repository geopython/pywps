"""
This module parses OGC Web Processing Service (WPS) Execute request.
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

import xml.dom.minidom
from pywps.Parser.Post import Post

import string

class Post(Post):
    """
    Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """
    wps = None # main WPS instance
    document = None # input DOM object
    inputs = {} # resulting parsed inputs
    nameSpace = None # WPS namespace
    owsNameSpace = None # OWS namespace
    xlinkNameSpace = None # OWS namespace


    def __init__(self,wps):
        """
        Arguments:
           self
           wps   - parent WPS instance
        """
        self.wps = wps

    def parse(self,document):
        self.document = document  # input DOM

        firstChild = self.getFirstChildNode(self.document)
        self.nameSpace = self.document.firstChild.namespaceURI
        self.owsNameSpace = self.wps.OWS_NAMESPACE
        self.owsNameSpace = self.wps.XLINK_NAMESPACE
        language  = None
        identifiers = []
        identifierNode = None
        dataInputs = None

        #
        # Mandatory options
        #
        
        # service
        self.inputs["service"] = "wps"
        
        # request 
        self.inputs["request"] = "describeprocess"

        # version
        self.inputs["version"] = firstChild.getAttribute("version")
        if not self.inputs["version"]:
            raise self.wps.exceptions.MissingParameterValue("version")

        # identifier
        self.inputs["identifier"] =\
          document.getElementsByTagNameNS(self.owsNameSpace,"Identifier")[0]
        if not self.inputs["identifier"]:
            raise self.wps.exceptions.MissingParameterValue("identifier")

        #
        # Optional options
        #
            
        # language
        language = firstChild.getAttribute("language")
        if not language:
            language = self.wps.DEFAULT_LANGUAGE

        self.inputs["language"] = language

        # dataInputs
        inputsNode = \
             document.getElementsByTagNameNS(self.nameSpace,"DataInputs")[0]
        if inputsNode:
            self.inputs["dataInputs"] = self.parseDataInputs(inputsNode) 
        else:
            self.inputs["dataInputs"] = {}

        # responseForm

        print self.inputs

    #def parseDataInputs(self,inputsNode):

        parsedDataInputs = {}
        
        for inputNode in inputsNode.getElementsByTagNameNS(self.nameSpace,
                                                                "Input":
            # input Identifier
            identifier = inputNode.getElementsByTagNameNS(self.nameSpace,
                                    "Identifier")[0].firstChild.nodeValue
            if identifier == "":
                raise self.wps.exeptions.NoApplicableCode(
                                              "Identifer for input not set")

            else:
                parseDataInputs[identifier] = {"value":None,attributes:{}}
            # Title and Abstract are only mandatory and not necessary
            
            # formchoice
            dataTypeNode = inputNode.lastChild
            if dataTypeNode.nodeName.find("Reference") > -1:
                self.parsedDataInputs[identifier] =\
                            self.parseReferenceDataInput(dataTypeNode)
            elif dataTypeNode.nodeName.find("Data") > -1:
                self.parsedDataInputs[identifier] =\
                            self.parseDataDataInput(dataTypeNode)
                
        return parsedDataInputs

    def parseReferenceDataInput(self,dataTypeNode):
        
        attributes = {}

        #
        # mandatrory attributes
        #
        attributes["href"] =\
                    dataTypeNode.getAttributeNS(self.xlinkNameSpace,"href")
        if attributes == "":
            raise self.wps.exceptions.MissingParameterValue("'href'")

        #
        # optional attributes
        #

        # FIXME mimeType, encoding, schema - not yet supported
        
        # method
        attributes["method"] = \
                   dataTypeNode.getAttributeNS(self.nameSpace,"method")
        if attributes["method"] == "":
            attributes["method"] = "GET"
        
        # FIXME Header, Body, BodyReference - not yest supported
        
        return attributes

    def parseDataDataInput(self,dataTypeNode):
        attributes = {}

        # FIXME Here I am


        return attributes

    def parseComplexData(self,complexDataNode):
        pass
    
    def parseLiteralData(self,literalDataNode):
        pass

    def parseBBoxData(self,bboxDataNode):
        pass


class Get:
    """
    Parses input request obtained via HTTP GET encoding.
    """

    wps = None  # main WPS instance
    unparsedInputs = {} # input arguments
    inputs = {} # resulting parsed inputs

    def __init__(self,wps):
        """
        Arguments:
           self
           wps   - parent WPS instance
        """
        self.wps = wps

    def parse(self,unparsedInputs):
        self.unparsedInputs = unparsedInputs

        #
        # Mandatory options
        #

        # service (is allready controled)
        if self.unparsedInputs["service"].lower() == "wps":
            self.inputs["service"] = self.unparsedInputs["service"].lower()

        # Request (is allready controled)
        if self.unparsedInputs["request"].lower() == "execute":
            self.inputs["request"] = self.unparsedInputs["request"].lower()

        # version
        self.inputs["version"] = self.unparsedInputs["version"]

        # identifier
        self.inputs["identifier"] = self.unparsedInputs["identifier"]

        # 
        # Optional options
        #

        # Language
        try:
            self.inputs["language"] =\
                                    self.unparsedInputs["language"].lower()
        except KeyError,e:
            self.inputs["language"] = self.wps.DEFAULT_LANGUAGE


        # dataInputs
        try:
            self.inputs["dataInputs"] = self.parseDataInputs(
                        self.unparsedInputs["datainputs"])
        except KeyError:
            self.inputs["dataInputs"] = {}

        # ResponseDocument
        try:
            self.inputs["responseDocument"] = self.parseDataInputs(
                    self.unparsedInputs["responsedocument"])
        except KeyError:
            self.inputs["responseDocument"] = {}

        # RawDataOutput
        try:
            self.inputs["rawDataOutput"] = self.parseDataInputs(
                    self.unparsedInputs["rawdataoutput"])
        except KeyError:
            self.inputs["rawdataoutput"] = {}

        # storeExecuteResponse
        try:
            if self.unparsedInputs["storeexecuteresponse"].lower() ==\
                                                                    "true":
                self.inputs["storeExecuteResponse"] = True
            else:
                self.inputs["storeExecuteResponse"] = False

        except KeyError:
            self.inputs["storeExecuteResponse"] = False

        # lineage
        try:
            if self.unparsedInputs["lineage"].lower() == "true":
                self.inputs["lineage"] = True
            else:
                self.inputs["lineage"] = False

        except KeyError:
            self.inputs["lineage"] = False

        # status
        try:
            if self.unparsedInputs["status"].lower() == "true":
                self.inputs["status"] = True
            else:
                self.inputs["status"] = False

        except KeyError:
            self.inputs["status"] = False

        print self.inputs

    def parseDataInputs(self,dataInputs):
        """
        See OGC WPS 1.0.0,  05-007, page 38
        """

        parsedDataInputs = {}

        for dataInput in dataInputs.split(";"):
            try:
                key,value = string.split(dataInput,"=",maxsplit=1)
            except ValueError,e:
                key = dataInput
                value = ""
            parsedDataInputs[key] = {"value":None,"attributes":{}}
            attributes = []
            if value.find("@") > 0:
                parsedDataInputs[key]["value"]=value.split("@")[0]
                attributes=value.split("@")[1:]
            elif value.find("@") == 0:
                parsedDataInputs[key]["value"]=None
                attributes=value.split("@")[1:]
            else:
                parsedDataInputs[key]["value"]=value
                attributes = []

            for attribute in attributes:
                attributeKey, attributeValue = attribute.split("=")
                parsedDataInputs[key]["attributes"][attributeKey] =\
                                                            attributeValue

        return parsedDataInputs
