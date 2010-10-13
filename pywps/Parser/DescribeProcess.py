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
