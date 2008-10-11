"""
Request handler - prototype class
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
# make sure, that the package python-htmltmpl is installed on your system!
from htmltmpl import TemplateManager, TemplateProcessor
import os
from sys import stdout as STDOUT
import types
from pywps import Templates
import re

class Response:
    response = None # Output document
    wps = None # Parent WPS object
    templateManager = None # HTML TemplateManager
    templateProcessor = TemplateProcessor(html_escape=0) # HTML TemplateProcessor
    template = None # HTML Template
    templateFile = None # File with template
    processDir = None # Directory with processes
    statusFiles = STDOUT
    emptyParamRegex = re.compile('( \w+="")|( \w+="None")')
    templateVersionDirectory = None # directory with templates for specified version

    def __init__(self,wps):
        self.wps = wps

        self.templateVersionDirectory = self.wps.inputs["version"].replace(".","_")

        self.templateManager = TemplateManager(precompile = 1,
            debug = self.wps.config.getboolean("server","debug"))

        if self.wps.inputs["request"] == "getcapabilities":
            self.templateFile = os.path.join(
                                os.path.join(Templates.__path__)[0],
                                self.templateVersionDirectory,
                                    "GetCapabilities.tmpl")
        elif self.wps.inputs["request"] == "describeprocess":
            self.templateFile = os.path.join(
                                os.path.join(Templates.__path__)[0],
                                self.templateVersionDirectory,
                                    "DescribeProcess.tmpl")
        elif self.wps.inputs["request"] == "execute":
            self.templateFile = os.path.join(
                                os.path.join(Templates.__path__)[0],
                                self.templateVersionDirectory,
                                    "Execute.tmpl")

        self.processDir = os.getenv("PYWPS_PROCESSES")
        if not self.processDir:
            try: self.processDir = self.wps.getConfigValue("server", "processesPath")
            except: pass

        if self.processDir:
            import sys
            if self.processDir[-1] == os.path.sep:
                self.processDir = self.processDir[:-1]


            sys.path.append(os.path.split(self.processDir)[0])
            processes = __import__(os.path.split(self.processDir)[-1])
            self.processes = processes
        else:
            import pywps
            from pywps import processes
            self.processes = pywps.processes

    def getDataTypeReference(self,inoutput):
        """
        Returns data type reference according to W3C
        """

        dataType = {"type": None, "reference": None}
        if inoutput.dataType == types.StringType:
            dataType["type"] = "string"
            dataType["reference"] = "http://www.w3.org/TR/xmlschema-2/#string"
        elif inoutput.dataType == types.FloatType:
            dataType["type"] = "float"
            dataType["reference"] = "http://www.w3.org/TR/xmlschema-2/#float"
        elif inoutput.dataType == types.IntType:
            dataType["type"] = "integer"
            dataType["reference"] = "http://www.w3.org/TR/xmlschema-2/#integer"
        elif inoutput.dataType == types.BooleanType:
            dataType["type"] = "boolean"
            dataType["reference"] = "http://www.w3.org/TR/xmlschema-2/#boolean"
        else:
            # TODO To be continued...
            dataType["type"] = "string"
            dataType["reference"] = "http://www.w3.org/TR/xmlschema-2/#string"
            pass

        return dataType

    def printResponse(self,fileDes):
        """
        print response to file descriptor file descriptor
        can be of type list or file
        """

        if type(fileDes) != type([]):
            fileDes = [fileDes]

        for f in fileDes:

            # open file
            if f != STDOUT and f.closed:
                f = open(f.name,"w")

            # '""' and '"None"'s will be removed
            f.write(re.sub(self.emptyParamRegex,"",self.response))
            f.flush()

            if (f != STDOUT):
                f.close()

    def cleanEnv(self):
        """Clean possible temporary files etc. created by this request
        type"""

