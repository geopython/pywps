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

import InAndOutputs
import Lang

import subprocess
import time
import types
import sys

class Status:
    """
    Status object for each process

    Attributes:
    creationTime time.time()
    code {String} "processstarted", "processfailed" or anything else
    percentCompleted {Float} how far the calculation is
    value {String} message string to the client
    """
    creationTime = time.time()
    code = None
    percentCompleted = 0
    code = None
    value = None

    def set(self, msg="",percentDone=0, propagate=True):
        """ Set status message

        Parameters:
        msg {String} message for the client
        percentDone {Float} percent > 0
        propagate {Boolean} call onStatusChanged method
        """
        self.code = "processstarted"
        if (type(percentDone) == types.StringType):
            self.percentCompleted += int(percentDone)
        else:
            self.percentCompleted = percentDone

        if not msg:
            msg = "True"

        self.value = msg

        if propagate:
            self.onStatusChanged()

    def onStatusChanged(self):
        """
        To be redefined by other methods
        """
        pass

    def setProcessStatus(self,code,value):
        """
        Sets current status of the process. Calls onStatusChanged method

        Parameters:
        code {String} one of "processaccepted" "processstarted"
                    "processsucceeded" "processpaused" "processfailed"
        value {String} additional message
        """

        self.value = value
        self.code = code.lower()

        if self.code != "processfailed":
            self.onStatusChanged()
        return


class WPSProcess:
    """Base class for any PyWPS Process"""
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

    def __init__(self, identifier, title = None, abstract=None,
            metadata=[],profile=[], version=None,
            statusSupported=True, storeSupported=False, grassLocation=None):
        """Process initialization. All parameters can be set lately

        Mandatory parameters:
        identifier {String} process identifier
        title {String} process title

        Optional parameters:
        abstract {String} process description
                default: None
        metadata List of additional metadata.  See
                    http://www.opengeospatial.org/standards/common, table 32 on page 65
                E.g. ["foo":"bar"]
                default: None
        profile [URN]
                default: None
        version {String} process version
                default: None
        statusSupported {Boolean} this process can be run asynchronously
                default: True
        storeSupported {Boolean} outputs from this process can be stored
                for later download
                default: True
        grassLocation {String} or {Boolean} name of GRASS Location within
                "gisdbase" directory (from pywps.cfg configuration file).
                If set to True, temporary GRASS Location will be created
                and grass environment will be started. If None or False, no
                GRASS environment will be started.
                default: None
        """


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
        self.statusSupported = statusSupported
        self.debug = False

        self.status = Status()
        self.inputs = {}
        self.outputs = {}

        self.lang = Lang.Lang()

        self.grassLocation = grassLocation

    def initProcess(self, title = None, abstract=None,
            metadata=[],profile=[], version=None,
            statusSupported=True, storeSupported=False, grassLocation=None):
        """Can be used for later process re-initialization

        For parameters, see __init__ method options.  """

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
        self.statusSupported = statusSupported

        self.grassLocation = grassLocation

    def addLiteralInput(self, identifier, title, abstract=None,
            uoms=(), minOccurs=1, maxOccurs=1,
            allowedValues=("*"), type=types.IntType ,
            default=None, metadata= []):
        """
        Add new input item of type LiteralValue to this process

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. Default: None
                    default: None
        uoms List of {String} value units
                    default: ()
        minOccurs {Integer} minimum number of occurrences.
                    default: 1
        maxOccurs {Integer} maximum number of occurrences.
                    default: 1
        allowedValues  List of {String} or {List} list of allowed values,
                    which can be used with this input. You can set interval
                    using list with two items, like:

                    (1,2,3,(5,9),10,"a",("d","g"))

                    This will produce allowed values 1,2,3,10, "a" and
                    any value between 5 and 9 or "d" and "g".

                    If "*" is used, it means "any value"
                    default: ("*")
        type {types.TypeType} value type, e.g. Integer, String, etc. you
                    can uses the "types" module of python.
                    default: types.IntType
        default {Any} default value.
                    default: None
        metadata List of {Dict} Additional metadata. E.g. {"foo":"bar"}
                    default: None
        """

        self.inputs[identifier] = InAndOutputs.LiteralInput(identifier=identifier,
                title=title, abstract=abstract, metadata=metadata,
                minOccurs=minOccurs,maxOccurs=maxOccurs,
                dataType=type, uoms=uoms, values=allowedValues,
                default=default)

        return self.inputs[identifier]

    def addComplexInput(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                formats=[{"mimeType":"text/xml"}],maxmegabites=5):
        """Add complex input to this process

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description.
                default: None
        metadata List of {Dict} {key:value} pairs.
                default: None
        minOccurs {Integer} minimum number of occurrences.
                default: 1
        maxOccurs {Integer} maximum number of occurrences.
                default: 1
        formats List of {Dict} according to table 23 (page 25). E.g.
                    [
                        {"mimeType": "image/tiff"},
                        {
                            "mimeType": "text/xml",
                            "encoding": "utf-8",
                            "schema":"http://foo/bar"
                        }
                    ]
                default: [{"mimeType":"text/xml"}]
        maxmegabites {Float} Maximum input file size. Can not be bigger, as
                defined in global configuration file.
                default: 5
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

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description.
                default: None
        metadata List of {Dict} {key:value} pairs.
                default: None
        minOccurs {Integer} minimum number of occurrences.
                default: 1
        maxOccurs {Integer} maximum number of occurrences.
                default: 1
        crss List of {String} supported coordinate systems.
                default: ["EPSG:4326"]
        """
        self.inputs[identifier] = InAndOutputs.BoundingBoxInput(identifier,
                title, abstract=abstract, metadata=metadata,
                minOccurs=minOccurs, maxOccurs=maxOccurs, crss=crss)

        return self.inputs[identifier]

    # --------------------------------------------------------------------

    def addComplexOutput(self,identifier,title,abstract=None,
            metadata=[],formats=[{"mimeType":"text/xml"}]):
        """Add complex output to this process

        Mandatory parameters:
        identifier {String} output identifier
        title {String} output title

        Optional parameters:
        metadata List of {Dict} {key:value} pairs.
                default: None
        formats List of {Dict} according to table 23 (page 25). E.g.
                    [
                        {"mimeType": "image/tiff"},
                        {
                            "mimeType": "text/xml",
                            "encoding": "utf-8",
                            "schema":"http://foo/bar"
                        }
                    ]
                default: [{"mimeType":"text/xml"}]
        """

        self.outputs[identifier] = InAndOutputs.ComplexOutput(identifier=identifier,
                title=title,abstract=abstract, metadata=metadata, formats=formats)

        return self.outputs[identifier]

    def addLiteralOutput(self, identifier, title, abstract=None,
            uoms=(), type=types.IntType, default=None):
        """
        Add new output item of type LiteralValue to this process

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. Default: None
                    default: None
        uoms List of {String} value units
                    default: ()
        type {types.TypeType} value type, e.g. Integer, String, etc. you
                    can uses the "types" module of python.
                    default: types.IntType
        default {Any} default value.
                    default: None
        """

        self.outputs[identifier] = InAndOutputs.LiteralOutput(identifier=identifier,
                title=title, abstract=abstract, dataType=type, uoms=uoms)

        return self.outputs[identifier]

    def addBBoxOutput(self, identifier, title, abstract=None,
            crs="EPSG:4326", dimensions=2):
        """Add new output item of type BoundingBoxValue to this process

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description.
                default: None
        crss List of {String} supported coordinate systems.
                default: ["EPSG:4326"]
        dimensions {Integer} number of dimensions
                default: 2
        """

        self.outputs[identifier] = InAndOutputs.BoundingBoxOutput(identifier=identifier,
                title=title, abstract=abstract, crss=[crs], dimensions=dimensions)

        return self.outputs[identifier]

    # --------------------------------------------------------------------
    def cmd(self,cmd,stdin=None,stdout=True):
        """Runs GRASS command, fetches all GRASS_MESSAGE and
        GRASS_PERCENT messages and sets self.status according to them, so
        the client application can track the progress information, when
        running with Status=True

        This module is supposed to be used instead of 'os.system()', while
        running GRASS modules

        Parameters:
        cmd {String} the command
        stdin {String} string to be send into the command via standard in
        stdout {Boolean}  give stdout and stderror from the command back

        Example Usage:
            self.cmd("r.los in=elevation.dem out=los coord=1000,1000")

            self.cmd("v.net.path network afcol=forward abcol=backward \
            out=mypath nlayer=1","1 9 12")

            self.cmd("d.mon start=PNG",stdout=False)
            """

        self.message("PyWPS Cmd: %s\n" % (cmd.strip()))

        try:
            subprocessstdin = None
            if stdin:
                subprocessstdin = subprocess.PIPE

            subprocessstdout = None
            subprocessstderr = None
            if stdout:
                subprocessstdout = subprocess.PIPE
                subprocessstderr = subprocess.PIPE

            p = subprocess.Popen(cmd,shell=True,
                stdin=subprocessstdin, stdout=subprocessstdout,
                stderr=subprocessstderr)
        except Exception,e :
            self.failed = True
            raise Exception("Could not perform command [%s]: %s" % (cmd,e))

        (stdout, stderr) = p.communicate(stdin)

        retcode = p.wait()

        if retcode != 0:
           self.status.setProcessStatus("processFailed", True)
           self.message("PyWPS stderr: %s\n" % (stderr),True)
           raise Exception("PyWPS could not perform command [%s]:\n%s" % (cmd,stderr))

        return stdout

    def message(self,msg,force=False):
        """Print some message to standard error

        Parameters:
        msg {String} print this string to standard error
        force {Boolean} if self.debug or force == True, the message will be
                printed. nothing happen otherwise.
        """

        if self.debug or force:
            sys.stderr.write(msg)
        return

    def getInput(self,identifier):
        """Get input defined by identifier

        Returns: None or Input
        """
        try:
            return self.inputs[identifier]
        except:
            return None

    def getInputValue(self,identifier):
        """Get input value according to identifier

        Returns: None or self.inputs[identifier].value
        """

        try:
            return self.inputs[identifier].getValue()
        except:
            return None

    def setOutputValue(self,identifier,value):
        """Set output value

        Returns: None
        """
        try:
            return self.outputs[identifier].setValue(value)
        except:
            return None

    def i18n(self,key):
        """Give back translation of defined key

        Returns: {String} translated string
        """
        return self.lang.get(key)

