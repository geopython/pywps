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
import pywps
from pywps.Parser.Post import Post as PostParser
from pywps.Parser.Get import Get as GetParser

import string,re,urllib

class Post(PostParser):
    """ HTTP POST XML request encoding parser.  """

    nameSpace = None # WPS namespace
    owsNameSpace = None # OWS namespace
    xlinkNameSpace = None # OWS namespace

    def __init__(self,wps):
        PostParser.__init__(self,wps)

    def parse(self,document, initInputs=None):
        """ Parse given XML document """


        if initInputs:
            self.inputs = initInputs

        self.document = document  # input DOM
        firstChild = self.isSoapFirstChild(self.document)  # no comments or
                                                            # white spaces

        self.nameSpace = firstChild.namespaceURI    # document namespace
        self.nameSpace = pywps.WPS_NAMESPACE
        self.owsNameSpace = pywps.OWS_NAMESPACE
        self.xlinkNameSpace = pywps.XLINK_NAMESPACE
        language  = None
        identifiers = []
        identifierNode = None
        dataInputs = []
       

        #
        # Mandatory options
        #

        # service & Request are already controlled

        # version
        self.checkVersion(firstChild)

        # identifier
        try:
            self.inputs["identifier"] = [
            firstChild.getElementsByTagNameNS(self.owsNameSpace,"Identifier")[0].firstChild.nodeValue
            ]
        except IndexError:
                raise pywps.MissingParameterValue("Identifier")

        #
        # Optional options
        #

        # language
        self.checkLanguage(firstChild)

        # dataInputs
        try:
            inputsNode = firstChild.getElementsByTagNameNS(
                                            self.nameSpace,"DataInputs")[0]
            self.inputs["datainputs"] = self.parseDataInputs(inputsNode)
        except IndexError:
            self.inputs["datainputs"] = None

        # responseForm
        try:
            responseFormNode = \
                firstChild.getElementsByTagNameNS(self.nameSpace,
                                                        "ResponseForm")[0]
            self.inputs["responseform"] = self.parseResponseForm(
                                                        responseFormNode)
        except IndexError:
            self.inputs["responseform"] = {}

        # OGC 05-007r7 page 36, Table 49
        # Either responseDocument or rawDataOutput should be specified, not both
        if self.inputs.has_key('responseform') and \
           (self.inputs["responseform"].has_key("rawdataoutput") and \
            self.inputs["responseform"].has_key("responsedocument")) and \
            self.inputs["responseform"]["responsedocument"] and \
            self.inputs["responseform"]["rawdataoutput"]:
            raise pywps.InvalidParameterValue("responseDocument",
                "Either responseDocument or rawDataOutput should be specified, but not both")
        if not self.inputs["responseform"].has_key("rawdataoutput"):
               self.inputs["responseform"]["rawdataoutput"] = {}
        if not self.inputs["responseform"].has_key("responsedocument"):
               self.inputs["responseform"]["responsedocument"] = {}
        return self.inputs

    def parseResponseForm(self,responseFormNode):
        """ Parse requested response form node """

        form = {}

        # ResponseDocument
        try:
            form["responsedocument"] = {}
            responseDocumentNode = responseFormNode.getElementsByTagNameNS(
                                    self.nameSpace, "ResponseDocument")[0]

            # store
            store = False
            if responseDocumentNode.hasAttribute("storeExecuteResponse"):
                if responseDocumentNode.getAttribute("storeExecuteResponse").lower() == "true":
                    form["responsedocument"]["storeexecuteresponse"]=True
                else:
                    form["responsedocument"]["storeexecuteresponse"]=False

            # lineage
            lineage = False
            if responseDocumentNode.hasAttribute("lineage"):
                if responseDocumentNode.getAttribute("lineage").lower() == "true":
                    form["responsedocument"]["lineage"]=True
                else:
                    form["responsedocument"]["lineage"]=False

            # status
            status = False
            if responseDocumentNode.hasAttribute("status"):
                if responseDocumentNode.getAttribute(
                        "status").lower() == "true":
                    form["responsedocument"]["status"]=True
                else:
                    form["responsedocument"]["status"]=False

            form["responsedocument"]["outputs"] = {}
            outputs = []
            for outputNode in responseDocumentNode.getElementsByTagNameNS(
                                                self.nameSpace, "Output"):

                try:
                    # identifier
                    identifier = outputNode.getElementsByTagNameNS(
                                    self.owsNameSpace,
                                    "Identifier")[0].firstChild.nodeValue
                    outputs.append({"identifier": identifier})
                except IndexError:
                    continue
                    # raise pywps.MissingParameterValue("Identifier")
                # Abstract, Title are not supported yet
                # is it necessary ?

                outputs[-1]["mimetype"] = \
                    outputNode.getAttribute("mimeType")
                outputs[-1]["encoding"] = \
                    outputNode.getAttribute("encoding")
                outputs[-1]["schema"] = \
                    outputNode.getAttribute("schema")
                outputs[-1]["uom"] = \
                    outputNode.getAttributeNS(self.nameSpace,"uom")

                outputs[-1]["asreference"] = False
                if outputNode.getAttribute("asReference").lower() == "true":
                    outputs[-1]["asreference"] = True

            form["responsedocument"]["outputs"] = outputs

        # RawDataOutput
        except IndexError:
            responseFormNode.getElementsByTagNameNS(self.nameSpace,
                                                    "RawDataOutput")
            form["rawdataoutput"] = {}
            identifier = None
            try:
                # identifier
                identifier = responseFormNode.getElementsByTagNameNS(
                                self.owsNameSpace,
                                "Identifier")[0].firstChild.nodeValue
                form["rawdataoutput"][identifier] = {}

                form["rawdataoutput"][identifier]["mimetype"] = \
                        responseFormNode.getAttribute("mimeType")
                form["rawdataoutput"][identifier]["encoding"] = \
                        responseFormNode.getAttribute("encoding")
                form["rawdataoutput"][identifier]["schema"] = \
                        responseFormNode.getAttribute("schema")
                form["rawdataoutput"][identifier]["uom"] = \
                        responseFormNode.getAttributeNS(self.nameSpace,"uom")
            except IndexError:
                 #raise pywps.MissingParameterValue("Identifier")
                 pass
        return form

    def parseDataInputs(self,inputsNode):
        """ Parse input data from given node """

        parsedDataInputs = []

        for inputNode in inputsNode.getElementsByTagNameNS(self.nameSpace,
                                                                "Input"):
            # input Identifier
            try:
                identifier = inputNode.getElementsByTagNameNS(
                     self.owsNameSpace,"Identifier")[0].firstChild.nodeValue
            except (IndexError, AttributeError):
                raise pywps.NoApplicableCode(
                                              "Identifier for input not set")
            parsedDataInputs.append({"identifier":identifier,"value":None,
                "attributes":{}})

            # Title and Abstract are only mandatory and not necessary:
            # skipping, not supported yet
            # formchoice
            try:
                dataTypeNode = inputNode.getElementsByTagNameNS(
                                            self.nameSpace,"Reference")[0]
                attributes = self.parseReferenceDataInput(dataTypeNode)
                attributes["identifier"] = identifier
                parsedDataInputs[-1] = attributes
            except IndexError,e:

                dataTypeNode = inputNode.getElementsByTagNameNS(
                                                self.nameSpace,"Data")[0]
                attributes =self.parseDataInput(dataTypeNode)
                attributes["identifier"] = identifier
                parsedDataInputs[-1] = attributes
            try:
                parsedDataInputs[-1]
            except KeyError:
                raise pywps.InvalidParameterValue(identifier)


        return parsedDataInputs

    def parseReferenceDataInput(self,dataTypeNode):
        """ Parse given complex value reference node """

        attributes = {}

        #
        # mandatory attributes
        #
        attributes["value"] =\
                    dataTypeNode.getAttributeNS(self.xlinkNameSpace,"href")
        if attributes["value"] == "":
            raise pywps.MissingParameterValue("'href'")

        #
        # optional attributes
        #

        # mimeType, encoding, schema - are now supportd supported ^_^ #jmdj
        
        attributes["mimetype"]=dataTypeNode.getAttribute("mimeType")
        attributes["encoding"]=dataTypeNode.getAttribute("encoding")
        attributes["schema"]=dataTypeNode.getAttribute("schema")
        
       #jmdj GET method doesn't have a namespace
        attributes["method"] = dataTypeNode.getAttribute("method")
        if attributes["method"] == "":
            attributes["method"] = "GET"

        # header
        try:
            attributes["header"] = self.parseHeaderDataInput(
                                        dataTypeNode.getElementsByTagNameNS(
                                            self.nameSpace, "Header")[0])
        except IndexError:
            attributes["header"] = None

        # body
        try:
            attributes["body"] = \
                        dataTypeNode.getElementsByTagNameNS(self.nameSpace,
                        "Body")[0].firstChild

            # get node value, if node type is Text or CDATA
            if attributes["body"].nodeType == \
                                    xml.dom.minidom.Text.nodeType or\
            attributes["body"].nodeType ==\
                                    xml.dom.minidom.CDATASection.nodeType:
                attributes["body"] = attributes["body"].nodeValue
        except IndexError:
            attributes["body"] = None

        # bodyreference
        try:
            bodyReferenceNode = dataTypeNode.getElementsByTagNameNS(
                                        self.nameSpace,"BodyReference")[0]
            attributes["bodyreference"] = bodyReferenceNode.getAttributeNS(
                                                self.xlinkNameSpace,"href")
        except IndexError:
            attributes["bodyreference"] = None

        attributes["type"] = "ComplexValue"
        attributes["asReference"] = True
        return attributes

    def parseHeaderDataInput(self,headerNode):
        """ Parse header node """

        header = {}

        if headerNode:
            header[headerNode.getAttributeNS(self.nameSpace,"key")] =\
                        headerNode.getAttributeNS(self.nameSpace,"value")

            if len(header.keys()) == 0:
                raise pywps.MissingParameterValue("Header")

        return header

    def parseDataInput(self,dataTypeNode):
        """Parse attributes of given data type node """

        attributes = {}

        # complexData
        if len(dataTypeNode.getElementsByTagNameNS(
                                    self.nameSpace,"ComplexData")) > 0:
            attributes = self.parseComplexData(
                                dataTypeNode.getElementsByTagNameNS(
                                           self.nameSpace,"ComplexData")[0])

        # literalData
        elif len(dataTypeNode.getElementsByTagNameNS(
                                    self.nameSpace,"LiteralData")) > 0:
            attributes = self.parseLiteralData(
                                dataTypeNode.getElementsByTagNameNS(
                                           self.nameSpace,"LiteralData")[0])
        # bboxData
        elif len(dataTypeNode.getElementsByTagNameNS(
                                    self.nameSpace,"BoundingBoxData")) > 0:
            attributes = self.parseBBoxData(
                                dataTypeNode.getElementsByTagNameNS(
                                       self.nameSpace,"BoundingBoxData")[0])

        # if attributes are still None, exception will
        # be called in parent method

        return attributes

    def parseComplexData(self,complexDataNode):
        """Parse complex data node"""

        attributes = {}
        attributes["mimetype"] = complexDataNode.getAttribute("mimeType")
        attributes["encoding"] = complexDataNode.getAttribute("encoding")
        attributes["schema"] = complexDataNode.getAttribute("schema")
        attributes["value"] = None
        for complexDataChildNode in complexDataNode.childNodes:
            # CDATA or text and the input value is empty and the Text or
            # CDATA is not empty
            if (complexDataChildNode.nodeType == xml.dom.minidom.Text.nodeType or \
                complexDataChildNode.nodeType == xml.dom.minidom.CDATASection.nodeType) and\
                complexDataChildNode.nodeValue and not attributes["value"]:
                attributes["value"] = complexDataChildNode.nodeValue
            # xml input
            elif complexDataChildNode.nodeType == \
                    xml.dom.minidom.Element.nodeType:
                attributes["value"] = complexDataChildNode.toxml()

        attributes["type"] = "ComplexValue"

        return attributes

    def parseLiteralData(self,literalDataNode):
        """Parse literal data node"""

        attributes = {}
        attributes["dataType"] = literalDataNode.getAttributeNS(
                                        "*","dataType")
        attributes["uom"] = literalDataNode.getAttributeNS(
                                        "*","uom")
        try:
            attributes["value"] = self._trueOrFalse((literalDataNode.firstChild.nodeValue).encode("utf-8"))
        except:
            attributes["value"] = None

        return attributes

    def parseBBoxData(self,bboxDataNode):
        """Parse bbox data node"""

        attributes = {}
        attributes["value"] = []
        attributes["crs"] = bboxDataNode.getAttributeNS(self.owsNameSpace,
                                                                    "crs")
        attributes["dimensions"] = int(bboxDataNode.getAttributeNS(
                                        self.owsNameSpace, "dimensions"))

        for coord in bboxDataNode.getElementsByTagNameNS(
                self.owsNameSpace,"LowerCorner")[0].firstChild.nodeValue.split():
            attributes["value"].append(float(coord))
        for coord in bboxDataNode.getElementsByTagNameNS(
                self.owsNameSpace,"UpperCorner")[0].firstChild.nodeValue.split():
            attributes["value"].append(float(coord))

        # reset everything, if there are not 4 coordinates
        if len(attributes["value"]) != 4:
            attributes = None
        return attributes


class Get(GetParser):
    """
    Parses input request obtained via HTTP GET encoding.
    """

    def __init__(self,wps):
        GetParser.__init__(self,wps)


    def parse(self,unparsedInputs, initInputs=None):
        """ Parse given inputs """

        if initInputs:
            self.inputs = initInputs

        self.unparsedInputs = unparsedInputs

        #
        # Mandatory options
        #

        # service & Request are already controlled

        # version
        self.checkVersion()

        # identifier
        if "identifier" in self.unparsedInputs:
            self.inputs["identifier"] = [self.unparsedInputs["identifier"]]
        else:
            raise pywps.MissingParameterValue("identifier")

        #
        # Optional options
        #

        # Language
        self.checkLanguage()

        # dataInputs
        try:
            self.inputs["datainputs"] = self.parseDataInputs(
                        self.unparsedInputs["datainputs"])
        
        except KeyError:
            self.inputs["datainputs"] = None
        # ResponseForm

        self.inputs["responseform"] = {}

        # ResponseDocument
        try:
            self.inputs["responseform"]["responsedocument"] = \
                    {"outputs":  self.parseDataInputs(self.unparsedInputs["responsedocument"])}  
        except KeyError:
            self.inputs["responseform"]["responsedocument"] = {}

        # RawDataOutput
        try:
            preparsed = self.parseDataInputs(self.unparsedInputs["rawdataoutput"])
            self.inputs["responseform"]["rawdataoutput"] = self._parseRawDataOutput(preparsed[0])
        except KeyError:
            self.inputs["responseform"]["rawdataoutput"] = {}

        # storeExecuteResponse
        if "storeexecuteresponse" in self.unparsedInputs:
            if self.unparsedInputs["storeexecuteresponse"].lower() ==\
                                                                    "true":
                self.inputs["responseform"]["responsedocument"]["storeexecuteresponse"] = True
            else:
                self.inputs["responseform"]["responsedocument"]["storeexecuteresponse"] = False

        # lineage
        if "lineage" in self.unparsedInputs:
            if self.unparsedInputs["lineage"].lower() == "true":
                self.inputs["responseform"]["responsedocument"]["lineage"]=\
                                                                        True
            else:
                self.inputs["responseform"]["responsedocument"]["lineage"]=\
                                                                       False

        # status
        if "status" in self.unparsedInputs:
            if self.unparsedInputs["status"].lower() == "true":
                self.inputs["responseform"]["responsedocument"]["status"]=\
                                                                        True
            else:
                self.inputs["responseform"]["responsedocument"]["status"]=\
                                                                      False

        # OGC 05-007r7 page 36, Table 49
        # Either responseDocument or rawDataOutput should be specified, not both
        if len(self.inputs["responseform"]["rawdataoutput"])>0 and \
            len(self.inputs["responseform"]["responsedocument"])>0:
            raise pywps.InvalidParameterValue("responseDocument",
                "Either responseDocument or rawDataOutput should be specified, but not both")
        return self.inputs

    def _parseRawDataOutput(self, dataInput):
        """Parser RawDataOutput parameter according to Table 52"""
        dataOut = {dataInput["identifier"]: {"mimetype":'', "uom":'', "encoding":'',"schema":''}}

        if dataInput.has_key("mimetype"):
            dataOut[dataInput["identifier"]]["mimetype"] = dataInput["mimetype"]
        if dataInput.has_key("schema"):
            dataOut[dataInput["identifier"]]["schema"] = dataInput["schema"]
        if dataInput.has_key("uom"):
            dataOut[dataInput["identifier"]]["uom"] = dataInput["uom"]
        if dataInput.has_key("encoding"):
            dataOut[dataInput["identifier"]]["encoding"] = dataInput["encoding"]
        return dataOut

    def _parseBBoxInput(self,dataInput):
        """Parser of Bounding Box data input"""
        print dataInput
            

    def parseDataInputs(self,dataInputs):
        """Parse DataInputs parameter

        This is described in OGC WPS 1.0.0,  05-007, page 38

        """

        parsedDataInputs = []

        # Parameters are separated by ";"
        for dataInput in dataInputs.split(";"):
            try:
                # key is separated by "=" from value
                key,valueAndAttrs = string.split(dataInput,"=",maxsplit=1)
            except ValueError,e:
                key = dataInput
                valueAndAttrs = ""

            if not key and not valueAndAttrs:
                continue
          
            # initial value
            parsed={"identifier":key, "value":None}
            # additional input attributes are separated by "@"
            attributes = []
            if valueAndAttrs.find("@") > 0:
                encodedValue=valueAndAttrs.split("@")[0]
                parsed["value"]=urllib.unquote(encodedValue)
                attributes=valueAndAttrs.split("@")[1:]
                    
            elif valueAndAttrs.find("@") == 0:
                #example: @xlink:href=http://rsg.pml.ac.uk/wps/testdata/elev_srtm_30m.img
                if ("@xlink:href" in valueAndAttrs):
                    #This attribute is actually a value
                    valueAndAttrs=valueAndAttrs.replace("@xlink:href=","")
                    encodedValue=valueAndAttrs.split("@")[0]
                    parsed["value"]=urllib.unquote(encodedValue)
                    attributes=valueAndAttrs.split("@")[1:]
                else:
                    attributes=valueAndAttrs.split("@")[1:]
                    #just passing the attributes
                    parsed["value"]=None
            else:
                #needs to be checked for trueOrFalse
                encodedValue=valueAndAttrs
                parsed["value"]=self._trueOrFalse(urllib.unquote(valueAndAttrs))
                attributes = []
           
            
            # additional attribute key is separated by "=" from it's value
            for attribute in attributes:
                attributeKey, attributeValue = attribute.split("=")
                parsed[attributeKey.lower()]=self._trueOrFalse(urllib.unquote(attributeValue))
            parsedDataInputs.append(parsed)
        return parsedDataInputs
    
    #Moved to Parser class
    #def _trueOrFalse(self,str):
    #    """Return True or False, if input is "true" or "false" """
    #    if str.lower() == "false":
    #        return False
    #    elif str.lower() == "true":
    #        return True
    #    else:
    #        return str
