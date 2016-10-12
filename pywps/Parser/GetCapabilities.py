##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################
"""
This module parses OGC Web Processing Service (WPS) GetCapabilities request.
"""

import xml.dom.minidom

import pywps
from pywps.Parser.Post import Post as PostParser
from pywps.Parser.Get import Get as GetParser

class Post(PostParser):
    """Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """

    def __init__(self,wps):
        PostParser.__init__(self,wps)


    def parse(self,document, initInputs = None):
        """ Parse the requested XML document"""
        self.document = document  # input DOM

        if initInputs:
            self.inputs = initInputs

        versions = []   # accepted versions
        acceptedVersionsNodes = None
        versionNode = None

        firstChild = self.isSoapFirstChild(self.document)  # no comments or
        owsNameSpace = pywps.OWS_NAMESPACE
        wpsNameSpace = pywps.WPS_NAMESPACE

        #
        # Mandatory options

        # service & Request are already controlled

        #
        # Optional options

        # acceptVersions
        acceptedVersionsNodes = self.document.getElementsByTagNameNS(
                                                wpsNameSpace,"AcceptVersions")
        if len(acceptedVersionsNodes) > 0:
            for versionNode in\
                acceptedVersionsNodes[-1].getElementsByTagNameNS(owsNameSpace,"Version"):
                versions.append(versionNode.firstChild.nodeValue)
        if len(versions) == 0:
            versions = self.wps.versions
        self.inputs["acceptversions"] = versions
        for version in self.inputs["acceptversions"]:
            if version in self.wps.versions:
                self.inputs["version"]=version
        if not "version" in self.inputs:
            raise pywps.VersionNegotiationFailed(
                                "There's no version in AcceptVersions parameter " +
                                "that is supported by this server.")

        # language
        self.checkLanguage(firstChild)

        return self.inputs

class Get(GetParser):
    """ Parses input request obtained via HTTP GET encoding.  """
    
    def __init__(self,wps):
        GetParser.__init__(self,wps)

    def parse(self,unparsedInputs, initInputs = None):
        """ Parse rawly parsed inputs """

        if initInputs:
            self.inputs = initInputs

        self.unparsedInputs = unparsedInputs

        #
        # Mandatory options

        # service & Request are already controlled

        #
        # Optional options

        # AcceptVersions
        try:
            self.inputs["acceptversions"] = \
                               self.unparsedInputs["acceptversions"].split(",")
        except KeyError,e:
            self.inputs["acceptversions"] = self.wps.versions
        for version in self.inputs["acceptversions"]:
            if version in self.wps.versions:
                self.inputs["version"]=version
        if not "version" in self.inputs:
            raise pywps.VersionNegotiationFailed(
                                "There's no version in AcceptVersions parameter " +
                                "that is supported by this server.")

        # Language
        self.checkLanguage()

        return self.inputs
