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
__all__ = ["GetCapabilities","DescribeProcess","Execute","Wsdl"]

import xml.dom.minidom
# make sure, that the package python-htmltmpl is installed on your system!
from pywps.Template import TemplateProcessor
import os
from sys import stdout as STDOUT
from sys import stderr as STDERR
import types
from pywps import Templates
from pywps import Soap

class Request:
    response = None # Output document
    respSize = None # Size of the ouput document
    wps = None # Parent WPS object
    template = None # HTML Template
    templateFile = None # File with template
    processDir = None # Directory with processes
    templateVersionDirectory = None # directory with templates for specified version
    precompile = 1
    stdOutClosed = False

    def __init__(self,wps):
        self.wps = wps

        self.templateVersionDirectory = self.wps.inputs["version"].replace(".","_")

	if os.name == "nt" or os.name == "java":
		self.precompile = 0

        if self.wps.inputs.has_key("request"):
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
        elif self.wps.inputs.has_key("wsdl"):
            self.templateFile = os.path.join(
                                os.path.join(Templates.__path__)[0],
                                self.templateVersionDirectory,
                                    "Wsdl.tmpl")

        self.templateProcessor = TemplateProcessor(self.templateFile,compile=True)


        self.processDir = os.getenv("PYWPS_PROCESSES")
        if self.processDir:
            self.wps.debug("PYWPS_PROCESSES set from environment variable to %s" %self.processDir)
        else:
            self.wps.debug("PYWPS_PROCESSES environment variable not set or empty.  Trying to find something in the configuration file")
            try:
                self.processDir = self.wps.getConfigValue("server", "processesPath")
                self.wps.debug("PYWPS_PROCESSES: set from configuration file to [%s]" %self.processDir)
            except: 
                self.wps.debug("'processesPath' not found in the 'server' section of pywps configuration file")

        if self.processDir:
            import sys
            if self.processDir[-1] == os.path.sep:
                self.processDir = self.processDir[:-1]

            try:
                sys.path.insert(0,os.path.split(self.processDir)[0])
                processes = __import__(os.path.split(self.processDir)[-1])
                self.processes = processes
            except ImportError,e:
                traceback.print_exc(file=self.logFile)
                raise self.wps.exceptions.NoApplicableCode("Could not import processes from the dir [%s]: %s! __init__.py file missing?" % (self.processDir,e))

            sys.path.append(self.processDir)
        else:
            self.wps.debug("Importing the processes from default (pywps/processes) location")
            try:
                import pywps
            except ImportError,e:
                traceback.print_exc(file=self.logFile)
                raise self.wps.exceptions.NoApplicableCode("Could not import pywps module: %s" % (e))
            try:
                from pywps import processes
                self.wps.debug("PYWPS_PROCESSES: %s" %os.path.abspath(pywps.processes.__path__[-1]))
            except Exception,e:
                traceback.print_exc(file=self.logFile)
                raise self.wps.exceptions.NoApplicableCode("Could not import pywps.processes module: %s" % (e))
            self.processes = pywps.processes

        # check, if all required processes are available
        prc = None
        if self.wps.inputs.has_key("identifier"):
            if type(self.wps.inputs["identifier"]) == type(""):
                prc = self.wps.inputs["identifier"]
                if not prc in self.processes.__all__:
                    raise self.wps.exceptions.InvalidParameterValue(prc)
            else:
                for prc in self.wps.inputs["identifier"]:
                    if not prc in self.processes.__all__:
                        raise self.wps.exceptions.InvalidParameterValue(prc)

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

    def cleanEnv(self):
        """Clean possible temporary files etc. created by this request
        type"""

