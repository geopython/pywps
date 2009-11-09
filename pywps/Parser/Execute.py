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
from pywps.Parser.Get import Get

import string,re

class Post(Post):
    """ HTTP POST XML request encoding parser.  """

    nameSpace = None # WPS namespace
    owsNameSpace = None # OWS namespace
    xlinkNameSpace = None # OWS namespace

    def parse(self,document):
        """ Parse given XML document """
        self.document = document  # input DOM

        firstChild = self.getFirstChildNode(self.document)  # no comments or
                                                            # white spaces
        self.nameSpace = firstChild.namespaceURI    # document namespace
        self.nameSpace = self.wps.WPS_NAMESPACE
        self.owsNameSpace = self.wps.OWS_NAMESPACE
        self.xlinkNameSpace = self.wps.XLINK_NAMESPACE
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
            self.wps.inputs["identifier"] =\
            firstChild.getElementsByTagNameNS(self.owsNameSpace,"Identifier")[0].firstChild.nodeValue
        except IndexError:
                raise self.wps.exceptions.MissingParameterValue("Identifier")

        #
        # Optional options
        #

        # language
        self.checkLanguage(firstChild)

        # dataInputs
        try:
            inputsNode = firstChild.getElementsByTagNameNS(
                                            self.nameSpace,"DataInputs")[0]
            self.wps.inputs["datainputs"] = self.parseDataInputs(inputsNode)
        except IndexError:
            self.wps.inputs["datainputs"] = None

        # responseForm
        try:
            responseFormNode = \
                firstChild.getElementsByTagNameNS(self.nameSpace,
                                                        "ResponseForm")[0]
            self.wps.inputs["responseform"] = self.parseResponseForm(
                                                        responseFormNode)
        except IndexError:
            self.wps.inputs["responseform"] = {}

        # OGC 05-007r7 page 36, Table 49
        # Either responseDocument or rawDataOutput should be specified, not both
        if self.wps.inputs.has_key('responseform') and \
           (self.wps.inputs["responseform"].has_key("rawdataoutput") and \
            self.wps.inputs["responseform"].has_key("responsedocument")):
            raise self.wps.exceptions.InvalidParameterValue(
                "Either responseDocument or rawDataOutput should be specified, but not both")
        if not self.wps.inputs["responseform"].has_key("rawdataoutput"):
               self.wps.inputs["responseform"]["rawdataoutput"] = {}
        if not self.wps.inputs["responseform"].has_key("responsedocument"):
               self.wps.inputs["responseform"]["responsedocument"] = {}
        return

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
                    raise self.wps.exceptions.MissingParameterValue("Identifier")
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
            try:
                # identifier
                identifier = responseFormNode.getElementsByTagNameNS(
                                self.owsNameSpace,
                                "Identifier")[0].firstChild.nodeValue
                form["rawdataoutput"][identifier] = {}
            except IndexError:
                raise self.wps.exceptions.MissingParameterValue("Identifier")
            form["rawdataoutput"][identifier]["mimetype"] = \
                    responseFormNode.getAttribute("mimeType")
            form["rawdataoutput"][identifier]["encoding"] = \
                    responseFormNode.getAttribute("encoding")
            form["rawdataoutput"][identifier]["schema"] = \
                    responseFormNode.getAttribute("schema")
            form["rawdataoutput"][identifier]["uom"] = \
                    responseFormNode.getAttributeNS(self.nameSpace,"uom")
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
                raise self.wps.exceptions.NoApplicableCode(
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
                raise self.wps.exceptions.InvalidParameterValue(identifier)


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
            raise self.wps.exceptions.MissingParameterValue("'href'")

        #
        # optional attributes
        #

        # mimeType, encoding, schema - not yet supported

        # method
        attributes["method"] = \
                   dataTypeNode.getAttributeNS(self.nameSpace,"method")
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
                raise self.wps.exceptions.MissingParameterValue("Header")

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
        attributes["mimetype"] = complexDataNode.getAttributeNS(
                                        "*","mimeType")
        attributes["encoding"] = complexDataNode.getAttributeNS(
                                        "*","encoding")
        attributes["schema"] = complexDataNode.getAttributeNS(
                                        "*","schema")
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
            attributes["value"] = literalDataNode.firstChild.nodeValue
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
                self.owsNameSpace,"LowerCorner")[0].nodeValue.split():
            attributes["value"].append(coord)
        for coord in bboxDataNode.getElementsByTagNameNS(
                self.owsNameSpace,"UpperCorner")[0].nodeValue.split():
            attributes["value"].append(coord)

        # reset everything, if there are not 4 coordinates
        if len(attributes["value"]) != 4:
            attributes = None
        return attributes


class Get(Get):
    """
    Parses input request obtained via HTTP GET encoding.
    """

    def parse(self,unparsedInputs):
        """ Parse given inputs """

        self.unparsedInputs = unparsedInputs

        #
        # Mandatory options
        #

        # service & Request are already controlled

        # version
        self.checkVersion()

        # identifier
        if "identifier" in self.unparsedInputs:
            self.wps.inputs["identifier"] = self.unparsedInputs["identifier"]
        else:
            raise self.wps.exceptions.MissingParameterValue("identifier")

        #
        # Optional options
        #

        # Language
        self.checkLanguage()

        # dataInputs
        try:
            self.wps.inputs["datainputs"] = self.parseDataInputs(
                        self.unparsedInputs["datainputs"])
        except KeyError:
            self.wps.inputs["datainputs"] = {}

        # ResponseForm

        self.wps.inputs["responseform"] = {}

        # ResponseDocument
        try:
            self.wps.inputs["responseform"]["responsedocument"] = \
                    {"outputs":  self.parseDataInputs(
                                self.unparsedInputs["responsedocument"])}
        except KeyError:
            self.wps.inputs["responseform"]["responsedocument"] = {}

        # RawDataOutput
        try:
            self.wps.inputs["responseform"]["rawdataoutput"] = \
                                    self.parseDataInputs(
                                    self.unparsedInputs["rawdataoutput"])
        except KeyError:
            self.wps.inputs["responseform"]["rawdataoutput"] = {}

        # storeExecuteResponse
        if "storeexecuteresponse" in self.unparsedInputs:
            if self.unparsedInputs["storeexecuteresponse"].lower() ==\
                                                                    "true":
                self.wps.inputs["responseform"]["responsedocument"]["storeexecuteresponse"] = True
            else:
                self.wps.inputs["responseform"]["responsedocument"]["storeexecuteresponse"] = False

        # lineage
        if "lineage" in self.unparsedInputs:
            if self.unparsedInputs["lineage"].lower() == "true":
                self.wps.inputs["responseform"]["responsedocument"]["lineage"]=\
                                                                        True
            else:
                self.wps.inputs["responseform"]["responsedocument"]["lineage"]=\
                                                                       False

        # status
        if "status" in self.unparsedInputs:
            if self.unparsedInputs["status"].lower() == "true":
                self.wps.inputs["responseform"]["responsedocument"]["status"]=\
                                                                        True
            else:
                self.wps.inputs["responseform"]["responsedocument"]["status"]=\
                                                                      False

        # OGC 05-007r7 page 36, Table 49
        # Either responseDocument or rawDataOutput should be specified, not both
        if len(self.wps.inputs["responseform"]["rawdataoutput"])>0 and \
            len(self.wps.inputs["responseform"]["responsedocument"])>0:
            raise self.wps.exceptions.InvalidParameterValue(
                "Either responseDocument or rawDataOutput should be specified, but not both")

    def parseDataInputs(self,dataInputs):
        """Parse DataInputs parameter

        This is described in OGC WPS 1.0.0,  05-007, page 38

        """

        parsedDataInputs = []

        # Parameters are separated by ";"
        for dataInput in dataInputs.split(";"):
            try:
                # key is separated by "=" from value
                key,value = string.split(dataInput,"=",maxsplit=1)
            except ValueError,e:
                key = dataInput
                value = ""

            if not key and not value:
                continue

            # initial value
            parsedDataInputs.append({"identifier":key, "value":None})

            # additional input attributes are separated by "@"
            attributes = []
            if value.find("@") > 0:
                parsedDataInputs[-1]["value"]=value.split("@")[0]
                attributes=value.split("@")[1:]
            elif value.find("@") == 0:
                parsedDataInputs[-1]["value"]=None
                attributes=value.split("@")[1:]
            else:
                parsedDataInputs[-1]["value"]=value
                attributes = []

            # additional attribute key is separated by "=" from it's value
            for attribute in attributes:
                attributeKey, attributeValue = attribute.split("=")
                parsedDataInputs[-1][attributeKey.lower()] =\
                                                    self._trueOrFalse(attributeValue)
        return parsedDataInputs

    def _trueOrFalse(self,str):
        """Return True or False, if input is "true" or "false" """

        if str.lower() == "false":
            return False
        elif str.lower() == "true":
            return True
        else:
            return str
