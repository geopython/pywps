"""
This module parses OGC Web Processing Service (WPS) DescribeProcess request.
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

class Post(Post):
    """
    Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """
    wps = None # main WPS instance
    document = None # input DOM object
    inputs = {} # resulting parsed inputs


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
        nameSpace = self.document.firstChild.namespaceURI
        owsNameSpace = self.wps.OWS_NAMESPACE
        language  = None
        identifiers = []
        identifierNode = None

        #
        # Mandatory options
        
        # service
        self.wps.inputs["service"] = "wps"
        
        # request 
        self.wps.inputs["request"] = "describeprocess"

        # version
        self.wps.inputs["version"] = firstChild.getAttribute("version")
        if not self.wps.inputs["version"]:
            raise self.wps.exceptions.MissingParameterValue("version")

        # identifiers
        for identifierNode in self.document.getElementsByTagNameNS(
                owsNameSpace,"Identifier"):
            identifiers.append(identifierNode.firstChild.nodeValue)
        self.wps.inputs["identifier"] = identifiers

        #
        # Optional options
            
        # language
        language = firstChild.getAttribute("language")
        if not language:
            language = self.wps.defaultLanguage

        self.wps.inputs["language"] = language

        return

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
        """ Parse given raw inputs"""

        self.unparsedInputs = unparsedInputs

        #
        # Mandatory options

        # service (is allready controled)
        if self.unparsedInputs["service"].lower() == "wps":
            self.wps.inputs["service"] = self.unparsedInputs["service"].lower()

        # Request (is allready controled)
        if self.unparsedInputs["request"].lower() == "describeprocess":
            self.wps.inputs["request"] = self.unparsedInputs["request"].lower()

        # version
        self.wps.inputs["version"] = self.unparsedInputs["version"]

        # identifier
        self.wps.inputs["identifier"] = self.unparsedInputs["identifier"].split(",")

        # 
        # Optional options

        # Language
        try:
            self.wps.inputs["language"] =\
                                    self.unparsedInputs["language"].lower()
        except KeyError,e:
            self.wps.inputs["language"] = self.wps.defaultLanguage

