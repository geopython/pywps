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

class Post:

    document = None # Document Object Model

    GET_CAPABILITIES = "GetCapabilities"
    DESCRIBE_PROCESS = "DescribeProcess"
    EXECUTE = "Execute"

    def __init__(self,wps):
        self.wps = wps

    def parse(self,file):
        
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

        self.findRequestType()

        return

    def findRequestType(self):

        firstChild = self.getFirstChildNode(self.document)

        if firstChild.tagName.find(self.GET_CAPABILITIES) > -1:
            import GetCapabilities 
            self.requestParser = GetCapabilities.Post(self.wps)
        elif firstChild.tagName.find(self.DESCRIBE_PROCESS) > -1:
            import DescribeProcess 
            self.requestParser = DescribeProcess.Post(self.wps)
        elif firstChild.tagName.find(self.EXECUTE) > -1:
            import Execute 
            self.requestParser = Execute.Post(self.wps)
        else:
            raise self.wps.Exceptions.InvalidParameterValue(firstChild.tagName)
        self.requestParser.parse(self.document)

    def getFirstChildNode(self,document):

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

