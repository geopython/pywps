"""
Wps Request
-----------
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
    """WPS Request performing, and response formating

    :param wps: instance of :class:`Pywps`

    .. attribute:: response
        
        formated response output

    .. attribute:: wps

        instance of :class:`pywps.PyWPS`

    .. attribute:: templateFile

        name of the template file (based on WPS version and request type)

    .. attribute:: processDir

        temporary created directory, where the process is running

    .. attribute:: templateVersionDirectory

        directory, where templates are stored (based on WPS version)
        
    .. attribute:: precompile

        indicates, if the template shuld be precompiled for later usage or
        not

    .. attribute:: stdOutClosed

        indicates, if we can write to standard output or not (usualy it is
        opend, it is closed only while the process is running in
        assynchronous mode)
        
    .. attribute:: templateProcessor

        instance of :class:`pywps.Template.TemplateProcessor`

    .. attribute:: processes

        list of processes :`class:`pywps.Process.WPSProcess`
    """

    response = None # Output document
    respSize = None # Size of the ouput document
    wps = None # Parent WPS object
    templateFile = None # File with template
    processDir = None # Directory with processes
    templateVersionDirectory = None # directory with templates for specified version
    precompile = 1
    stdOutClosed = False
    templateProcessor = None
    processes = None

    def __init__(self,wps,processes=None):
        """Class constructor"""
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

        # processes are set while Request is initialized
        if processes and type(processes) == type(""):
            self.wps.debug("Setting PYWPS_PROCESSES from the program itself to %s" % processes)
            self.processes = self.setFromDirectory(processes)
        elif os.getenv("PYWPS_PROCESSES"):
            self.wps.debug("Setting PYWPS_PROCESSES from the environment variable to %s" % os.getenv("PYWPS_PROCESSES"))
            self.processes = self.setFromDirectory(os.getenv("PYWPS_PROCESSES"))
        elif processes and type(processes) in [type(()), type([])]:

            self.wps.debug("Setting PYWPS_PROCESSES not set, we are using the processes array directly")
        elif self.wps.getConfigValue("server","processesPath"):
            self.wps.debug("Setting PYWPS_PROCESSES from configuration file to %s" %\
                        self.wps.getConfigValue("server","processesPath"))
            self.processes = self.setFromDirectory(self.wps.getConfigValue("server","processesPath"))
        else:
            self.wps.debug("Importing the processes from default (pywps/processes) location")
            import pywps
            from pywps import processes as pywpsprocesses
            self.processes = self.setFromDirectory(os.path.abspath(pywpsprocesses.__path__[-1]))

        # check the availbility of the process
        if self.wps.inputs.has_key("identifier"):
                self.checkProcess(self.wps.inputs["identifier"])

    def setFromDirectory(self,dirname):

        import sys
        # remove last "/" from the path
        if dirname[-1] == os.path.sep:
            dirname = dirname[:-1]

        try:
            sys.path.insert(0,os.path.split(dirname)[0])
            return __import__(os.path.split(dirname)[-1])
        except ImportError,e:
            traceback.print_exc(file=self.logFile)
            raise self.wps.exceptions.NoApplicableCode("Could not import processes from the dir [%s]: %s! __init__.py file missing?" % (dirname,e))

            sys.path.append(dirname)

    def checkProcess(self,identifiers):
        """check, if given identifiers are available as processes"""

        # string to [string]
        if type(identifieres) == type(""):
            identifieres = [identifieres]

        # for each process
        for prc in self.wps.inputs["identifier"]:
            if not prc in self.processes.__all__:
                raise self.wps.exceptions.InvalidParameterValue(prc,"Process %s not available" % prc)


    def getDataTypeReference(self,inoutput):
        """Returns data type reference according to W3C

        :param inoutput: :class:`pywps.Process.InAndOutputs.Input`
            or :class:`pywps.Process.InAndOutputs.Output`

        :rtype: string
        :returns: url to w3.org
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
        type
        
        .. note:: this method is empty and should be redefined by particula
            instances
        """


