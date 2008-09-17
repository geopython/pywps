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
from pywps.Parser.Get import Get

class Post(Post):
    """
    Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """

    def parse(self,document):
        self.document = document  # input DOM

        firstChild = self.getFirstChildNode(self.document)
        nameSpace = self.document.firstChild.namespaceURI
        owsNameSpace = self.wps.OWS_NAMESPACE
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
            raise self.wps.exceptions.MissingParameterValue("Identifier")
        self.wps.inputs["identifier"] = identifiers

        #
        # Optional options

        # language
        self.checkLanguage(firstChild)

        return

class Get(Get):
    """
    Parses input request obtained via HTTP GET encoding.
    """

    def parse(self,unparsedInputs):
        """ Parse given raw inputs"""

        self.unparsedInputs = unparsedInputs

        #
        # Mandatory options

        # service & Request are already controlled

        # version
        self.checkVersion()

        # identifier
        if "identifier" in self.unparsedInputs:
            self.wps.inputs["identifier"] = self.unparsedInputs["identifier"].split(",")
        else:
            raise self.wps.exceptions.MissingParameterValue("identifier")

        #
        # Optional options

        # Language
        self.checkLanguage()
