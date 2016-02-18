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
# along with this program; if not, write to the Free Software Foundation, Inc.
# , 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
__all__ = ["GetCapabilities", "DescribeProcess", "Execute", "Wsdl"]

# make sure, that the package python-htmltmpl is installed on your system!
from pywps import config
import pywps.Exceptions
from pywps.Template import TemplateProcessor
import os
from pywps import Templates
import types
import traceback
import logging

LOGGER = logging.getLogger(__name__)

class Request:
    """WPS Request performing, and response formating

    :param wps: instance of :class:`Pywps`
http://wiki.rsg.pml.ac.uk/pywps/Introduction
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

    response = None  # Output document
    respSize = None  # Size of the ouput document
    wps = None  # Parent WPS object
    templateFile = None  # File with template
    processDir = None  # Directory with processes
    templateVersionDirectory = None  # templates for specified version
    precompile = 1
    stdOutClosed = False
    templateProcessor = None
    processes = None
    processSources = None
    contentType = "application/xml"

    def __init__(self, wps, processes=None):
        """Class constructor"""
        self.wps = wps

        self.templateVersionDirectory = self.wps.inputs["version"].replace(
            ".", "_")

        if os.name == "nt" or os.name == "java":
            self.precompile = 0

        # Templates can be stored in other directory
        templates = Templates.__path__[0]
        if os.getenv("PYWPS_TEMPLATES"):
            templates = os.path.abspath(os.getenv("PYWPS_TEMPLATES"))

        if "request" in self.wps.inputs.keys():
            if self.wps.inputs["request"] == "getcapabilities":
                self.templateFile = os.path.join(
                    templates, self.templateVersionDirectory,
                    "GetCapabilities.tmpl"
                )
            elif self.wps.inputs["request"] == "describeprocess":
                self.templateFile = os.path.join(
                    templates, self.templateVersionDirectory,
                    "DescribeProcess.tmpl"
                )
            elif self.wps.inputs["request"] == "execute":
                self.templateFile = os.path.join(
                    templates, self.templateVersionDirectory, "Execute.tmpl")
        try:
            self.templateProcessor = TemplateProcessor(self.templateFile,
                                                       compile=True)
        except pywps.Template.TemplateError, e:
            raise pywps.Exceptions.NoApplicableCode(
                "TemplateError: %s" % repr(e))
        # set self.processes from various inputs
        #
        # process are string -- it means the directory
        if not processes:
            processes = os.getenv("PYWPS_PROCESSES")
        self.initProcesses(processes)

    def _init_from_directory(self, dirname):

        import sys
        processes = []
        # remove last "/" from the path
        if dirname[-1] == os.path.sep:
            dirname = dirname[:-1]
        proc_module = None
        # try to import process from python package (directory)
        try:
            sys.path.insert(0, os.path.split(dirname)[0])
            sys.path.insert(0, dirname)
            # import the main directory for processes
            try:
                processSources = __import__(os.path.split(dirname)[-1])
            except ImportError, e:
                raise pywps.Exceptions.NoApplicableCode(e)

            # for each file within the directory - module within the
            # package, try to import it as well
            for proc_module in processSources.__all__:

                # try to identify every class, based on
                # pywps.Process.WPSProcess
                try:
                    proc_module = __import__(proc_module, globals(), locals(),
                                             [processSources.__name__])
                except Exception, e:
                    # async process has problems reporting missing modules.
                    traceback.print_exc(file=pywps.logFile)
                    LOGGER.warning("Could not import processes from "
                                    "%s: %s" % (repr(processSources.__name__),
                                                repr(e))
                                    )
                for member in dir(proc_module):
                    member = eval("proc_module." + member)

                    # check, if the module is Class, make instance of it
                    # and import it
                    if isinstance(member, types.ClassType):
                        if issubclass(member, pywps.Process.WPSProcess) and \
                                not member == pywps.Process.WPSProcess:

                            # create instance of the member and append it to
                            # self.processes
                            try:
                                processes.append(member())
                            except Exception, e:
                                LOGGER.warning(
                                    "Could not import process "
                                    "[%s]: %s" % (repr(member), repr(e))
                                )
                    # if the member is Istance, check, if it is istnace of
                    # WPSProcess class and import it
                    elif isinstance(member, types.InstanceType):
                        if isinstance(member, pywps.Process.WPSProcess):
                                processes.append(member)
        except ImportError, e:
            traceback.print_exc(file=pywps.logFile)
            processes.append("Could not import process "
                             "[%s]: %s" % (repr(proc_module), repr(e)))
        return processes

    def _init_from_code(self, processes):

        out_processes = []
        for process in processes:
            if isinstance(process, types.InstanceType):
                out_processes.append(process)
            elif isinstance(process, types.ClassType):
                out_processes.append(process())
        return out_processes

    def checkProcess(self, identifiers):
        """check, if given identifiers are available as processes"""

        # string to [string]
        if isinstance(identifiers, str):
            identifiers = [identifiers]

        # for each process
        for prc in self.wps.inputs["identifier"]:
            try:
                if prc not in self.processes.__add__:
                    raise pywps.Exceptions.InvalidParameterValue(
                        prc, "Process %s not available" % prc)
            except AttributeError:
                invalidParameterValue = True
                for proc in self.processes:
                    if type(proc) == types.ClassType:
                        proc = proc()
                    if proc.identifier == prc:
                        invalidParameterValue = False
                if invalidParameterValue:
                    raise pywps.Exceptions.InvalidParameterValue(prc)

    def getDataTypeReference(self, inoutput):
        """Returns data type reference according to W3C

        :param inoutput: :class:`pywps.Process.InAndOutputs.Input`
            or :class:`pywps.Process.InAndOutputs.Output`

        :rtype: string
        :returns: url to w3.org
        """

        import types
        data_type = {"type": None, "reference": None}
        if inoutput.dataType == types.StringType:
            data_type["type"] = "string"
            data_type["reference"] = "http://www.w3.org/TR/xmlschema-2/#string"
        elif inoutput.dataType == types.FloatType:
            data_type["type"] = "float"
            data_type["reference"] = "http://www.w3.org/TR/xmlschema-2/#float"
        elif inoutput.dataType == types.IntType:
            data_type["type"] = "integer"
            data_type["reference"] = \
                "http://www.w3.org/TR/xmlschema-2/#integer"
        elif inoutput.dataType == types.BooleanType:
            data_type["type"] = "boolean"
            data_type["reference"] = \
                "http://www.w3.org/TR/xmlschema-2/#boolean"
        else:
            # TODO To be continued...
            data_type["type"] = "string"
            data_type["reference"] = "http://www.w3.org/TR/xmlschema-2/#string"
            pass

        return data_type

    def cleanEnv(self):
        """Clean possible temporary files etc. created by this request
        type

        .. note:: this method is empty and should be redefined by particula
            instances
        """
        pass

    def initProcesses(self, processes=None):
        """Initialize list of :attr:`processes`

        :param processes: processes input processes. If none, environment
            and default settings will be used.
        :type processes: list of :class:`pywps.Process.WPSProcess`, list of
            it's instances, string with directory, where processes are
            located, ..."""
        global pywps

        if processes and isinstance(processes, str):
            LOGGER.info("Reading processes from directory [%s]" % processes)
            self.processes = self._init_from_directory(processes)

        # processes are some list -- use them directly
        elif processes and type(processes) in [type(()), type([])]:

            LOGGER.info("Setting PYWPS_PROCESSES not set, we are using "
                         "the processes array directly")
            self.processes = self._init_from_code(processes)

        # processes will be set from configuration file
        elif config.getConfigValue("server", "processesPath"):
            LOGGER.info(
                "Setting PYWPS_PROCESSES from configuration file "
                "to %s" % config.getConfigValue("server", "processesPath")
            )
            self.processes = self._init_from_directory(
                config.getConfigValue("server", "processesPath"))

        # processes will be set from default directory
        else:
            LOGGER.info("Importing the processes from default "
                         "(pywps/processes) location")
            from pywps import processes as pywpsprocesses
            self.processes = self._init_from_directory(
                os.path.abspath(pywpsprocesses.__path__[-1]))

        if len(self.processes) == 0:
            LOGGER.warning("No processes found in any place. Continuing, "
                            "but you can not execute anything.")

        LOGGER.info("Following processes are imported: "
                     "%s" % map(lambda p: p.identifier, self.processes))
        return self.processes

    def getProcess(self, identifier):
        """Get single processes based on it's identifier"""

        if isinstance(identifier, list):
            identifier = identifier[0]

        for process in self.processes:
            if isinstance(process, str):
                continue
            if process.identifier == identifier:
                return process
        raise pywps.Exceptions.InvalidParameterValue("identifier",
            "Unknown identifier '%s'" % identifier)

    def getProcesses(self, identifiers=None):
        """Get list of processes identified by list of identifiers

        :param identifiers: List of identifiers. Either list of strings,
            or 'all'
        :returns: list of process instances or none
        """
        if not identifiers:
            raise pywps.Exceptions.MissingParameterValue("Identifier")

        if isinstance(identifiers, str):
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
                raise pywps.Exceptions.InvalidParameterValue("identifier")
            else:
                return processes

    def formatMetadata(self, process):
        """Create structure suitble for template form process.metadata

        :param process: :attr:`pywps.Process`
        :returns: hash with formated metadata
        """

        metadata = process.metadata
        if isinstance(metadata, dict):
            metadata = [metadata]

        metadatas = []
        for metad in metadata:
            meta_structure = {}

            if "title" in metad.keys():
                meta_structure["title"] = metad["title"]
            else:
                meta_structure["title"] = process.title

            if "href" in metad.keys():
                meta_structure["href"] = metad["href"]
            else:
                meta_structure["href"] = (
                    config.getConfigValue("wps", "serveraddress") +
                    "?service=WPS&amp;request=DescribeProcess&amp;version=" +
                    config.getConfigValue("wps", "version") +
                    "&amp;identifier=" +
                    process.identifier
                )

            metadatas.append(meta_structure)

        return metadatas
