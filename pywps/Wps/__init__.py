"""
Wps Request
-----------
"""
# Author:       Jachym Cepicky
#               http://les-ejk.cz
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
import pywps
from pywps import config
from pywps.Exceptions import *
from pywps.Template import TemplateProcessor
import os
from sys import stdout as STDOUT
from sys import stderr as STDERR
from pywps import Templates
from pywps import Soap
import types
import traceback
import logging

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

        list of instances of :`class:`pywps.Process.WPSProcess`

    .. attribute:: processSources

        list of sources of processes

    .. attribute :: contentType

        Response content type, text/xml usually
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
    processSources = None
    contentType = "application/xml"

    def __init__(self,wps,processes=None):
        """Class constructor"""
        self.wps = wps

        self.templateVersionDirectory = self.wps.inputs["version"].replace(".","_")

        if os.name == "nt" or os.name == "java":
            self.precompile = 0

        # Templates can be stored in other directory
        templates = Templates.__path__[0]
        if os.getenv("PYWPS_TEMPLATES"):
            templates = os.path.abspath(os.getenv("PYWPS_TEMPLATES"))

        if self.wps.inputs.has_key("request"):
            if self.wps.inputs["request"] == "getcapabilities":
                self.templateFile = os.path.join(templates,
                                    self.templateVersionDirectory,
                                        "GetCapabilities.tmpl")
            elif self.wps.inputs["request"] == "describeprocess":
                self.templateFile = os.path.join(templates,
                                    self.templateVersionDirectory,
                                        "DescribeProcess.tmpl")
            elif self.wps.inputs["request"] == "execute":
                self.templateFile = os.path.join(templates,
                                    self.templateVersionDirectory,
                                        "Execute.tmpl")
        elif self.wps.inputs.has_key("wsdl"):
            self.templateFile = os.path.join(templates,
                                self.templateVersionDirectory,
                                    "Wsdl.tmpl")

        try:
            self.templateProcessor = TemplateProcessor(self.templateFile,compile=True)
        except pywps.Template.TemplateError,e:
            raise NoApplicableCode("TemplateError: %s" % repr(e))
            

        # set self.processes from various inputs
        #
        # process are string -- it means the directory
        if not processes:
            processes = os.getenv("PYWPS_PROCESSES")
        self.initProcesses(processes)

    def _initFromDirectory(self,dirname):

        import sys
        processes = []
        # remove last "/" from the path
        if dirname[-1] == os.path.sep:
            dirname = dirname[:-1]


        procModule = None
        # try to import process from python package (directory)
        try:
            sys.path.insert(0,os.path.split(dirname)[0])
            sys.path.insert(0,dirname)
            
            # import the main directory for processes
            try:
                processSources =  __import__(os.path.split(dirname)[-1])
            except ImportError,e:
                raise NoApplicableCode(e)

            # for each file within the directory - module within the
            # package, try to import it as well
            for procModule in processSources.__all__:


                # try to identify every class, based on
                # pywps.Process.WPSProcess
                try:
                    procModule = __import__(procModule, globals(),\
                                    locals(), [processSources.__name__])
                except Exception,e:
                    logging.warning(
                            "Could not import processes from %s: %s" % \
                                    (repr(processSources.__name__), repr(e)))
                
                for member in dir(procModule):
                    member = eval("procModule."+member)

                    # check, if the module is Class, make instance of it
                    # and import it
                    if type(member) == types.ClassType:
                        if issubclass(member, pywps.Process.WPSProcess) and \
                            not member == pywps.Process.WPSProcess:

                            # create instance of the member and append it to
                            # self.processes
                            try:
                                processes.append(member())
                            except Exception,e:
                                logging.warning(
                                        "Could not import process [%s]: %s" % \
                                                (repr(member), repr(e)))
                    # if the member is Istance, check, if it is istnace of
                    # WPSProcess class and import it
                    elif type(member) == types.InstanceType:
                        if isinstance(member, pywps.Process.WPSProcess):
                                processes.append(member)
                        

        except ImportError,e:
            traceback.print_exc(file=pywps.logFile)
            processes.append("Could not import process [%s]: %s" % (repr(procModule), repr(e)))
        return processes

    def _initFromCode(self,processes):

        outProcesses = []
        for process in processes:
            if type(process) == types.InstanceType:
                outProcesses.append(process)
            elif type(process) == types.ClassType:
                outProcesses.append(process())
        return outProcesses

    def checkProcess(self,identifiers):
        """check, if given identifiers are available as processes"""

        # string to [string]
        if type(identifiers) == type(""):
            identifiers = [identifiers]

        # for each process
        for prc in self.wps.inputs["identifier"]:
            try:
                if not prc in self.processes.__all__:
                    raise InvalidParameterValue(prc,"Process %s not available" % prc)
            except AttributeError:
                invalidParameterValue = True
                for proc in self.processes:
                    if type(proc) == types.ClassType:
                        proc = proc()
                    if proc.identifier == prc:
                        invalidParameterValue = False
                if invalidParameterValue:
                    raise InvalidParameterValue(prc)



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
        pass

    def initProcesses(self,processes=None):
        """Initialize list of :attr:`processes`
        
        :param processes: processes input processes. If none, environment and default
            settings will be used.
        :type processes: list of :class:`pywps.Process.WPSProcess`, list of
            it's instances, string with directory, where processes are
            located, ..."""
        global pywps
        
        if processes and type(processes) == type(""):
            logging.info("Reading processes from [%s]" % processes)
            self.processes  = self._initFromDirectory(processes)

        # processes are some list -- use them directly
        elif processes and type(processes) in [type(()), type([])]:

            logging.info("Setting PYWPS_PROCESSES not set, we are using the processes array directly")
            self.processes = self._initFromCode(processes)

        # processes will be set from configuration file
        elif config.getConfigValue("server","processesPath"):
            logging.info("Setting PYWPS_PROCESSES from configuration file to %s" %\
                        config.getConfigValue("server","processesPath"))
            self.processes = self._initFromDirectory(config.getConfigValue("server","processesPath"))

        # processes will be set from default directory
        else:
            logging.info("Importing the processes from default (pywps/processes) location")
            from pywps import processes as pywpsprocesses
            self.processes = self._initFromDirectory(os.path.abspath(pywpsprocesses.__path__[-1]))

        if len(self.processes) == 0:
            logging.warning("No processes found in any place. Continuing, but you can not execute anything.")

        logging.info("Following processes are imported: %s" %\
               map(lambda p: p.identifier, self.processes))
        return self.processes

    def getProcess(self,identifier):
        """Get single processes based on it's identifier"""

        if type(identifier) == type([]):
            identifier = identifier[0]

        for process in self.processes:
            if type(process) == types.StringType:
                continue
            if process.identifier == identifier:
                return process
        raise InvalidParameterValue(identifier)

    def getProcesses(self,identifiers=None):
        """Get list of processes identified by list of identifiers

        :param identifiers: List of identifiers. Either list of strings, or 'all'
        :returns: list of process instances or none
        """

        if not identifiers:
            raise MissingParameterValue("Identifier")

        if type(identifiers) == types.StringType:
            if identifiers.lower() == "all":
                return self.processes
            else:
                return self.getProcess(identifiers)
        else:
            processes = []
            for identifier in identifiers:
                if identifier.lower() == "all":
                    return self.processes
                else:
                    processes.append(self.getProcess(identifier))

            if len(processes) == 0:
                raise InvalidParameterValue(identifier)
            else:
                return processes

    def formatMetadata(self,process):
        """Create structure suitble for template form process.metadata

        :param process: :attr:`pywps.Process`
        :returns: hash with formated metadata
        """

        metadata = process.metadata
        if type(metadata) == type({}):
            metadata = [metadata]

        metadatas = []
        for metad in metadata:
            metaStructure = {}

            if metad.has_key("title"):
                metaStructure["title"] = metad["title"]
            else:
                metaStructure["title"] = process.title

            if metad.has_key("href"):
                metaStructure["href"] = metad["href"]
            else:
                metaStructure["href"] = config.getConfigValue("wps","serveraddress")+\
                        "?service=WPS&amp;request=DescribeProcess&amp;version="+config.getConfigValue("wps","version")+\
                        "&amp;identifier="+ process.identifier

            metadatas.append(metaStructure)

        return metadatas
