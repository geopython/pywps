"""
This module parses OGC Web Processing Service (WPS) GetCapabilities request.
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
    """ Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """

    def parse(self,document):
        """ Parse the requested XML document"""
        self.document = document  # input DOM

        versions = []   # accepted versions
        acceptedVersionsNodes = None
        versionNode = None
        firstChild = self.getFirstChildNode(self.document)
        owsNameSpace = self.wps.OWS_NAMESPACE
        wpsNameSpace = self.wps.WPS_NAMESPACE

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
        self.wps.inputs["acceptversions"] = versions
        for version in self.wps.inputs["acceptversions"]:
            if version in self.wps.versions:
                self.wps.inputs["version"]=version
        if not "version" in self.wps.inputs:
            raise self.wps.exceptions.VersionNegotiationFailed(
                                "There's no version in AcceptVersions parameter " +
                                "that is supported by this server.")

        # language
        self.checkLanguage(firstChild)

        return

class Get(Get):
    """ Parses input request obtained via HTTP GET encoding.  """

    def parse(self,unparsedInputs):
        """ Parse rawly parsed inputs """

        self.unparsedInputs = unparsedInputs

        #
        # Mandatory options

        # service & Request are already controlled

        #
        # Optional options

        # AcceptVersions
        try:
            self.wps.inputs["acceptversions"] = \
                               self.unparsedInputs["acceptversions"].split(",")
        except KeyError,e:
            self.wps.inputs["acceptversions"] = self.wps.versions
        for version in self.wps.inputs["acceptversions"]:
            if version in self.wps.versions:
                self.wps.inputs["version"]=version
        if not "version" in self.wps.inputs:
            raise self.wps.exceptions.VersionNegotiationFailed(
                                "There's no version in AcceptVersions parameter " +
                                "that is supported by this server.")

        # Language
        self.checkLanguage()

