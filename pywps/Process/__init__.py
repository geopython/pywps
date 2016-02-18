"""
Process
-------
Package for creating (Py)WPS Process classes
"""
# Author:       Jachym Cepicky
#               http://les-ejk.cz
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

__all__ = ["Lang","InAndOutputs"]

import InAndOutputs
import Lang

import subprocess
import time
import types
import sys,os
import traceback

from collections import OrderedDict

class Status:
    """Status object for each process

    .. attribute:: creationTime 
    
        :func:`time.time()`

    .. attribute:: code 
    
        "processstarted", "processfailed" or anything else

    .. attribute:: percentCompleted 
    
        how far the calculation is

    .. attribute:: value 
            
        message string to the client
    """
    creationTime = time.time()
    code = None
    percentCompleted = 0
    code = None
    value = None

    def set(self, msg="",percentDone=0, propagate=True):
        """ Set status message

        :param msg: message for the client
        :type msg: string
        :param percentDone: percent > 0 [0-99]
        :type percentDone: int
        :param propagate: call onStatusChanged method
        :type propagate: boolean
        """
        self.code = "processstarted"
        #percentageDone has to be int. The trick below will cast str-->float-->int
        
        self.percentCompleted=int(float(percentDone))
        #if (type(percentDone) == types.StringType):
        #    self.percentCompleted += int(percentDone)
        #else:
        #    self.percentCompleted = percentDone

        if not msg:
            msg = "True"

        self.value = msg

        if propagate:
            self.onStatusChanged()

    def onStatusChanged(self):
        """Redefine this method in your functions
        """
        pass

    def setProcessStatus(self,code,value):
        """Sets current status of the process. Calls onStatusChanged method

        :param code: one of "processaccepted" "processstarted"
                    "processsucceeded" "processpaused" "processfailed"
        :type code: string
        :param value: additional message
        :type value: string
        """

        self.value = value
        self.code = code.lower()

        if self.code != "processfailed":
            self.onStatusChanged()
        return


class WPSProcess:
    """Base class for any PyWPS Process

    :param identifier: process identifier
    :type identifier: string
    :param title: process title
    :type title: string
    :param abstract: process description
    :type abstract: string
    :param metadata: List of additional metadata references. See http://www.opengeospatial.org/standards/common, table 32 on page 65, http://schemas.opengis.net/xlink/1.0.0/xlinks.xsd

           Example::
            
                [
                    {
                     "title": "Title",
                     "href": "http://bnhelp.cz/metadata/micka_main.php?ak=detail&uuid=32e80880-c3b0-11dc-8641-873e117140a9",
                     ... : ...
                     }
                ]

    :param profile: profile URN
    :type profile: [string]
    :param version:  process version
    :param statusSupported: this process can be run asynchronously
    :type statusSupported: boolean
    :param storeSupported: outputs from this process can be stored
           for later download
    :type storeSupported: boolean
    :param grassLocation: name of GRASS Location within
            "gisdbase" directory (from pywps.cfg configuration file).
            If set to True, temporary GRASS Location will be created
            and grass environment will be started. If None or False, no
            GRASS environment will be started.

    .. attribute:: identifier
    
        Process identifier
        
    .. attribute:: version
    
        Process version
        
    .. attribute:: metadata
    
        List of references to metadata resources
        
    .. attribute:: title
        
        Process title 
        
    .. attribute:: abstract
    
        Process abstract
        
    .. attribute:: wsdl

        Not implemented

    .. attribute:: profile

        Process profile

    .. attribute:: storeSupported

        Indicates, whether the process supports storing of it's results for
        later usage

    .. attribute:: statusSupported

        Indicates, whether assynchronous running of the process is possible

    .. attribute:: debug
        
        Print some information to log file

    .. attribute:: status

        Instance of :class:`Status`

    .. attribute:: inputs

        List of process inputs, :class:`pywps.Process.InAndOutputs.Input`

    .. attribute:: outputs

        List of process outputs, :class:`pywps.Process.InAndOutputs.Output`

    .. attribute:: lang

        instance of :class:`pywps.Process.Lang.Lang` class

    .. attribute:: grassLocation

        Indicates, if and how `GRASS GIS <http://grass.osgeo.org>`_ should be used

        None/False
            GRASS GIS is not used in any way. No location/mapset is
            created, no GRASS environment is initialized.

        True
            Temporary GRASS location is created. It is in XY reference
            coordinate system

            .. note:: In the future, location should have the same
                coordinate system, as the input dataset is.

        String
            Name of existing GRASS Location (location name or full path),
            with existing PERMANENT mapset, where your Process can take
            input data from (or store results to). Temporary mapset within
            this location is created.
    
    .. attribute:: logFile

        File object, where to print log in.

    .. attribute:: pywps
    
        copy of the :class:`pywps.Pywps` instance

    """
    identifier = None
    version = None
    metadata = None
    title = None
    abstract = None
    wsdl  = None
    profile = None
    storeSupported = None
    statusSupported = None
    debug = None
    status = None
    inputs = None
    outputs = None
    lang = None
    grassLocation = None
    grassMapset = None
    logFile = None
    pywps = None

    def __init__(self, identifier, title=None, abstract=None,
            metadata=[],profile=[],version="None",
            statusSupported=True, storeSupported=False, grassLocation=None,
            logFile = sys.stderr):
        """Contructor"""

        self.identifier = identifier
        self.version = version
        self.metadata = metadata
        self.title = title
        self.abstract = abstract
        self.wsdl  = None
        self.profile = profile
        # "true" or "True" -> True
        if type(storeSupported) == type(""):
            if storeSupported.find("t") == 0 or\
                storeSupported.find("T") == 0:
                storeSupported = True
            else:
                storeSupported = False
        self.storeSupported = storeSupported
        if type(statusSupported) == type(""):
            if statusSupported.find("t") == 0 or\
                statusSupported.find("T") == 0:
                statusSupported = True
            else:
                statusSupported = False
        self.statusSupported = statusSupported

        # status not supported on windows
        if os.name == "nt":
                self.statusSupported = False

        self.debug = False

        self.status = Status()
        self.inputs = OrderedDict()
        self.outputs = {}

        self.lang = Lang.Lang()

        self.grassLocation = grassLocation

    def initProcess(self, title = None, abstract=None,
            metadata=[],profile=[], version=None,
            statusSupported=True, storeSupported=False, grassLocation=None):
        """Can be used for later process re-initialization

        For parameters, see constructor :class:`WPSProcess` parameters.  """

        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.profile = profile
        self.version = version
        if type(storeSupported) == type(""):
            if storeSupported.find("t") == 0 or\
                storeSupported.find("T") == 0:
                storeSupported = True
            else:
                storeSupported = False
        self.storeSupported = storeSupported
        if type(statusSupported) == type(""):
            if statusSupported.find("t") == 0 or\
                statusSupported.find("T") == 0:
                statusSupported = True
            else:
                statusSupported = False
        self.statusSupported = statusSupported

        self.grassLocation = grassLocation

    def addLiteralInput(self, identifier, title, abstract=None,
            uoms=(), minOccurs=1, maxOccurs=1,
            allowedValues=("*"), type=types.IntType ,
            default=None, metadata=[]):
        """
        Add new input item of type LiteralValue to this process

        :param identifier: input identifier
        :param title: input title
        :param abstract: input description. 
        :param uoms: List of value units
        :type uoms: [string]
        :param minOccurs: minimum number of occurrences, default 1
        :param maxOccurs: maximum number of occurrences, default 1
        :param allowedValues:  List of of allowed values,
                    which can be used with this input. You can set interval
                    using list with two items, like::

                        (1,2,3,(5,9),10,"a",("d","g"))

                    This will produce allowed values 1,2,3,10, "a" and
                    any value between 5 and 9 or "d" and "g".

                    If `*` is used, it means "any value"
                    default ("*")
        :param type: value type, e.g. Integer, String, etc. you
                    can uses the :mod:`types` module of python.
                    default: types.IntType
        :type type: `types.TypeType`
        :param default: default value of this input
        :param metadata: List of additional metadata references. See http://www.opengeospatial.org/standards/common, table 32 on page 65, http://schemas.opengis.net/xlink/1.0.0/xlinks.xsd

            Example::
                
                    [
                        {
                        "title": "Title",
                        "href": "http://bnhelp.cz/metadata/micka_main.php?ak=detail&uuid=32e80880-c3b0-11dc-8641-873e117140a9",
                        ... : ...
                        }
                    ]
        
            default: None

        :returns: :class:`pywps.Process.InAndOutputs.LiteralInput`
        """

        self.inputs[identifier] = InAndOutputs.LiteralInput(identifier=identifier,
                title=title, abstract=abstract, metadata=metadata,
                minOccurs=minOccurs,maxOccurs=maxOccurs,
                dataType=type, uoms=uoms, values=allowedValues,
                default=default)
        return self.inputs[identifier]

    def addComplexInput(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                formats=[{"mimeType":None}],maxmegabites=None):
        """Add complex input to this process

        :param identifier: input identifier
        :param title: input title
        :param abstract: input description. 
        :param minOccurs: minimum number of occurrences, default 1
        :param maxOccurs: maximum number of occurrences, default 1
        :param formats: List of dictionary according to table 23 (page 25)
            OGC WPS. 

            Example::

                    [
                        {"mimeType": "image/tiff"},
                        {
                            "mimeType": "text/xml",
                            "encoding": "utf-8",
                            "schema":"http://foo/bar"
                        }
                    ]

        :param maxmegabites: Maximum input file size. Can not be bigger, as
                defined in global configuration file.

        :param metadata: List of additional metadata references. See http://www.opengeospatial.org/standards/common, table 32 on page 65, http://schemas.opengis.net/xlink/1.0.0/xlinks.xsd

            Example::
                
                    [
                        {
                        "title": "Title",
                        "href": "http://bnhelp.cz/metadata/micka_main.php?ak=detail&uuid=32e80880-c3b0-11dc-8641-873e117140a9",
                        ... : ...
                        }
                    ]

            default: None
        
        :returns: :class:`pywps.Process.InAndOutputs.ComplexInput`
        """

        self.inputs[identifier] = InAndOutputs.ComplexInput(identifier=identifier,
                title=title,abstract=abstract,
                metadata=metadata,minOccurs=minOccurs,maxOccurs=maxOccurs,
                formats=formats, maxmegabites=maxmegabites)

        return self.inputs[identifier]


    def addBBoxInput(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                crss=["EPSG:4326"]):
        """Add BoundingBox input

        :param identifier: input identifier
        :type identifier: string
        :param title: input title
        :type title: string
        :param abstract: input description.
        :type abstract: string
        :param metadata: List of metadata references.
        :type metadata: list
        :param minOccurs: minimum number of occurrences.
        :type maxOccurs: integer
        :param maxOccurs: maximum number of occurrences.
        :type maxOccurs: integer
        :param crss: of supported coordinate systems.
        :type crss: list
        :returns: :class:`pywps.Process.InAndOutputs.BoundingBoxInput`
        """
        self.inputs[identifier] = InAndOutputs.BoundingBoxInput(identifier,
                title, abstract=abstract, metadata=metadata,
                minOccurs=minOccurs, maxOccurs=maxOccurs, crss=crss)

        return self.inputs[identifier]

    # --------------------------------------------------------------------

    def addComplexOutput(self,identifier,title,abstract=None,
            metadata=[],formats=[{"mimeType":None}],
            useMapscript=False,asReference=False):
        """Add complex output to this process

        :param identifier: output identifier
        :param title: output title
        :param metadata: List of additional metadata references. See http://www.opengeospatial.org/standards/common, table 32 on page 65, http://schemas.opengis.net/xlink/1.0.0/xlinks.xsd

            Example::
                
                    [
                        {
                        "title": "Title",
                        "href": "http://bnhelp.cz/metadata/micka_main.php?ak=detail&uuid=32e80880-c3b0-11dc-8641-873e117140a9",
                        ... : ...
                        }
                    ]

            default: None

        :param formats: List of dictionaries according to table 23 (page
            25) of the standard
            
            ::
        
                    [
                        {"mimeType": "image/tiff"},
                        {
                            "mimeType": "text/xml",
                            "encoding": "utf-8",
                            "schema":"http://foo/bar"
                        }
                    ]

        :param asReference: output default asReference
        :returns: :class:`pywps.Process.InAndOutputs.ComplexOutput`
        """

        self.outputs[identifier] = InAndOutputs.ComplexOutput(identifier=identifier,
                title=title,abstract=abstract, metadata=metadata,
                formats=formats,useMapscript = useMapscript,asReference=asReference)

        return self.outputs[identifier]

    def addLiteralOutput(self, identifier, title, abstract=None,metadata=[],
            uoms=(), type=types.IntType, default=None,asReference=False):
        """
        Add new output item of type LiteralValue to this process

        :param identifier: input identifier
        :param title: input title
        :param abstract: input description. 
        :param uoms: List of string  value units
        :param type: :class:`types.TypeType` value type, e.g. Integer, String, etc. you
                    can uses the :mod:`types` module of python.
        :param default: default value, if any
        :param metadata: List of additional metadata references. See http://www.opengeospatial.org/standards/common, table 32 on page 65, http://schemas.opengis.net/xlink/1.0.0/xlinks.xsd
        :param asReference: output default asReference
        :returns: :class:`pywps.Process.InAndOutputs.LiteralOutput`
        """



        self.outputs[identifier] = InAndOutputs.LiteralOutput(identifier=identifier,
                title=title, abstract=abstract, metadata=metadata,dataType=type, uoms=uoms,asReference=asReference)

        return self.outputs[identifier]

    def addBBoxOutput(self, identifier, title, abstract=None,
            crs="EPSG:4326", dimensions=2,asReference=False):
        """Add new output item of type BoundingBoxValue to this process

        :param identifier: input identifier
        :param title: input title
        :param abstract: input description.
        :param crss: List of strings supported coordinate systems.
        :param dimensions: number of dimensions
        :param asReference: output default asReference
        :returns: :class:`pywps.Process.InAndOutputs.BoundingBoxOutput`
        """

        self.outputs[identifier] = InAndOutputs.BoundingBoxOutput(identifier=identifier,
                title=title, abstract=abstract, crss=[crs], dimensions=dimensions,asReference=asReference)

        return self.outputs[identifier]

    # --------------------------------------------------------------------
    def cmd(self,cmd,stdin=None,stdout=True):
        """Command line commands (including GRASS modules)

        .. note:: This module is supposed to be used instead of 'os.system()', while
            running GRASS modules

        :param cmd: the command, as list of parameters
        :type cmd: [string]
        :param stdin:  string to be send into the command via standard in
        :param stdout:  give stdout and stderror from the command back
        :type stdout: boolean

        :rtype: string
        :returns: standard ouput from the command

        Example Usage::

            self.cmd(["r.los","in=elevation.dem","out=los","coord=1000,1000"])

            self.cmd(["v.net.path","network","afcol=forward","abcol=backward",
            "out=mypath",'''nlayer=1","1 9 12"'''])

            self.cmd(["d.mon","start=PNG"],stdout=False)
            """

        # splitting the command, if not already done
        if (type(cmd) == types.StringType):
            cmd = cmd.strip().split()

        if stdin:
            idx = stdin.find("\n")
            if 0 < idx <= 60:
                stdinOut = " "+stdin[:idx]
            else:
                stdinOut = " "+stdin[:60]
        else:
            stdinOut = ""

        self.message("PyWPS Cmd: %s\n" % (" ".join(cmd)+stdinOut))

        try:
            subprocessstdin = None
            if stdin:
                subprocessstdin = subprocess.PIPE

            subprocessstdout = None
            subprocessstderr = None
            if stdout:
                subprocessstdout = subprocess.PIPE
                subprocessstderr = subprocess.PIPE

            p = subprocess.Popen(cmd,
                stdin=subprocessstdin, stdout=subprocessstdout,
                stderr=subprocessstderr)
        except Exception,e :
            traceback.print_exc(file=sys.stderr)
            self.failed = True
            raise Exception("Could not perform command [%s]: %s" % (cmd,e))

        (stdout, stderr) = p.communicate(stdin)
        self.message(stderr)
        self.message(stdout)
        retcode = p.wait()

        if retcode != 0:
           self.status.setProcessStatus("processFailed", True)
           self.message("PyWPS stderr: %s\n" % (stderr),True)
           raise Exception("PyWPS could not perform command [%s]:\n%s" % (cmd,stderr))

        return stdout

    def message(self,msg,force=False):
        """Print some message to logfile

        :param msg: print this string to logfile
        :param force: if self.debug or force == True, the message will be
                printed. nothing happen otherwise.
        """

        if (self.debug or force) and self.logFile:
            if type(self.logFile) == type(""):
                try:
                    f = open(self.logFile,"w")
                    f.write("DEBUG: " + msg + "\n")
                    f.close()
                except:
                    print >>sys.stderr, "PyWPS WARNING: Could not write to logfile [%s]" % self.logFile
            else:
                self.logFile.write("DEBUG: " + msg + "\n")
        return

    def getInput(self,identifier):
        """Get input defined by identifier

        :param identifier: input identifier
        :return: :class:`pywps.Process.InAndOutputs.Input`
        """
        try:
            return self.inputs[identifier]
        except:
            return None

    def getInputValue(self,identifier):
        """Get input value according to identifier

        :param identifier: input identifier
        :return: None or `self.inputs[identifier].value`
        """

        try:
            return self.inputs[identifier].getValue()
        except:
            return None

    def getInputValues(self, identifier):
        """Get input values according to identifier
        :param identifier: input identifier
        :return: a list of input values
        """
        values = self.getInputValue(identifier)
        if values is None:
            values = []
        elif type(values) != types.ListType:
            values = [values]
        return values
        
    def setOutputValue(self,identifier,value):
        """Set output value

        :param identifier: output identifier
        :param value: value to be set
        """
        try:
            return self.outputs[identifier].setValue(value)
        except:
            return None

    def i18n(self,key):
        """Give back translation of defined key

        :param key: key value to be translated
        :return: translated string
        """
        return self.lang.get(key)

    def execute(self):
        """This method will be called by :class:`pywps.Wps.Execute.Execute`. Please
        redefine this in your process instance
        
        :returns: None if succeeded, error message otherwise."""
        pass
