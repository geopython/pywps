# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# Lince:
#
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import types,sys
import xml
from xml.dom.minidom import parseString
from pywps.Parser.Parser import Parser
from pywps.Process.Lang import Lang

class Post(Parser):
    """Main class for parsing of HTTP POST request types"""

    document = None # Document Object Model
    requestParser = None

    GET_CAPABILITIES = "GetCapabilities"
    DESCRIBE_PROCESS = "DescribeProcess"
    EXECUTE = "Execute"

    def parse(self,file):
        """
        Parse parameters stored as XML file
        """

        maxFileSize = None
        inputXml = None

        # get the maximal input file size from configuration
        maxFileSize = self.getMaxFileSize(
                self.wps.config.get("server","maxFileSize").lower())

        # read the document
        if maxFileSize > 0:
            inputXml = file.read(maxFileSize)
            if file.read() != "":
                raise self.wps.exceptions.FileSizeExceeded()
        else:
            inputXml = file.read()

        # make DOM from XML
        try:
            self.document = parseString(inputXml)
        except xml.parsers.expat.ExpatError,e:
            raise self.wps.exceptions.NoApplicableCode(e.message)

        # get first child
        firstChild = self.getFirstChildNode(self.document)

        # check service name
        self.checkService(firstChild)

        # find request type
        self.checkRequestType(firstChild)

        # parse the document
        self.requestParser.parse(self.document)

    def checkService(self, node):
        """ Check mandatory service name parameter.  """

        # service name is mandatory for all requests (OWS_1-1-0 p.14 tab.3 +
        # p.46 tab.26); service must be "WPS" (WPS_1-0-0 p.17 tab.13 + p.32 tab.39)
        if node.hasAttribute("service"):
            value=node.getAttribute("service").upper()
            if value != "WPS":
                raise self.wps.exceptions.InvalidParameterValue("service")
            else:
                self.wps.inputs["service"] = "WPS"
        else:
            raise self.wps.exceptions.MissingParameterValue("service")

    def checkLanguage(self, node):
        """ Check optional language parameter.  """

        if node.hasAttribute("language"):
            value=Lang.getCode(node.getAttribute("language").lower())
            if value not in self.wps.languages:
                raise self.wps.exceptions.InvalidParameterValue("language")
            else:
                self.wps.inputs["language"] = value
        else:
            self.wps.inputs["language"] = self.wps.defaultLanguage

    def checkVersion(self, node):
        """ Check optional language parameter.  """

        if node.hasAttribute("version"):
            value=node.getAttribute("version")
            if value not in self.wps.versions:
                raise self.wps.exceptions.VersionNegotiationFailed(
                    'The requested version "' + value + \
                    '" is not supported by this server.')
            else:
                self.wps.inputs["version"] = value
        else:
            raise self.wps.exceptions.MissingParameterValue("version")

    def checkRequestType(self, node):
        """Find requested request type and import given request parser."""

        firstTagName = node.tagName

        if firstTagName.find(self.GET_CAPABILITIES) > -1:
            import GetCapabilities
            self.requestParser = GetCapabilities.Post(self.wps)
            self.wps.inputs["request"] = "getcapabilities"
        elif firstTagName.find(self.DESCRIBE_PROCESS) > -1:
            import DescribeProcess
            self.requestParser = DescribeProcess.Post(self.wps)
            self.wps.inputs["request"] = "describeprocess"
        elif firstTagName.find(self.EXECUTE) > -1:
            import Execute
            self.requestParser = Execute.Post(self.wps)
            self.wps.inputs["request"] = "execute"
        else:
            raise self.wps.Exceptions.InvalidParameterValue("request")

    def getFirstChildNode(self,document):
        """Find first usable child node of the document (no comments)"""

        node = None

        # get the first child (omit comments)
        for node in document.childNodes:
            if node.nodeType == xml.dom.minidom.Element.nodeType:
                firstChild = node
        if firstChild == None:
            raise self.wps.exceptions.NoApplicableCode(
                                        "No root Element found!")
        return firstChild

    def getMaxFileSize(self,maxFileSize):
        """ Convert given filesize string to number of bytes.

        This is used mainly for the parsing of the value from the
        configuration file.

        """

        if maxFileSize.find("kb") > 0:
            maxFileSize = float(maxFileSize[:maxFileSize.find("gb")])
            maxFileSize = int(maxFileSize*1024)
        elif maxFileSize.find("mb") > 0:
            maxFileSize = float(maxFileSize[:maxFileSize.find("mb")])
            maxFileSize = int(maxFileSize*1024*1024)
        elif maxFileSize.find("gb") > 0:
            maxFileSize = float(maxFileSize[:maxFileSize.find("gb")])
            maxFileSize = int(maxFileSize*1024*1024*1024)
        elif maxFileSize.find("b") > 0:
            maxFileSize = int(maxFileSize[:maxFileSize.find("b")])
        else:
            maxFileSize = int(maxFileSize)
        return maxFileSize

