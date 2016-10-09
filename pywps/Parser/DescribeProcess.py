##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################
"""
This module parses OGC Web Processing Service (WPS) DescribeProcess request.
"""

import xml.dom.minidom
import pywps
from pywps.Parser.Post import Post as PostParser
from pywps.Parser.Get import Get as GetParser



class Post(PostParser):
    """
    Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """
    def __init__(self,wps):
        PostParser.__init__(self,wps)

    def parse(self,document, initInputs = None):

        if initInputs:
            self.inputs = initInputs

        self.document = document  # input DOM

	firstChild = self.isSoapFirstChild(self.document)
	owsNameSpace = pywps.OWS_NAMESPACE
        identifiers = []
        identifierNode = None

        #
        # Mandatory options

        # service & Request are already controlled

        # version
        self.checkVersion(firstChild)

        # identifiers
        for identifierNode in self.document.getElementsByTagNameNS(
                owsNameSpace,"Identifier"):
            identifiers.append(identifierNode.firstChild.nodeValue)
        if len(identifiers) == 0:
            raise pywps.MissingParameterValue("Identifier")
        self.inputs["identifier"] = identifiers

        #
        # Optional options

        # language
        self.checkLanguage(firstChild)

        return self.inputs

class Get(GetParser):
    """
    Parses input request obtained via HTTP GET encoding.
    """
    def __init__(self,wps):
        GetParser.__init__(self,wps)

    def parse(self,unparsedInputs, initInputs=None):
        """ Parse given raw inputs"""

        if initInputs:
            self.inputs = initInputs

        self.unparsedInputs = unparsedInputs

        #
        # Mandatory options

        # service & Request are already controlled

        # version
        self.checkVersion()

        # identifier
        if "identifier" in self.unparsedInputs:
            self.inputs["identifier"] = self.unparsedInputs["identifier"].split(",")
        else:
            raise pywps.MissingParameterValue("identifier")

        #
        # Optional options

        # Language
        self.checkLanguage()

        return self.inputs
