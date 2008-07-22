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
    def __init__(self):
        self.creationTime = time.time()
        self.code = None
        self.percentCompleted = 0
        self.exceptionReport = None
        self.code = None
        self.value = None

    def set(self, msg="",percentDone=0, propagate=True):
        """
        propagate - call onStatusChanged method
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
        """

        self.value = value
        self.code = code.lower()

        if self.code != "processfailed":
            self.onStatusChanged()
        return


class WPSProcess:
    """
    """
    def __init__(self, identifier, title = None, abstract=None,
            metadata=[],profile=[], version=None,
            statusSupported=True, storeSupported=False, grassLocation=None):

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
        """
        Can be used for later process re-initialization
        """

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

    def addMetadata(self,Identifier, type, textContent):
        """Add new metadata to this process"""
        self.Metadata.append({
            "Identifier": Identifier,
            "type":type,
            "textContent":textContent})

    def addLiteralInput(self, identifier, title, abstract=None,
            uoms=(), minOccurs=1, maxOccurs=1, 
            allowedValues=("*"), type=types.IntType ,
            default=None, metadata= []):
        """
        Add new input item of type LiteralValue to this process
        """

        self.inputs[identifier] = InAndOutputs.LiteralInput(identifier=identifier,
                title=title, abstract=abstract, metadata=[],
                minOccurs=minOccurs,maxOccurs=maxOccurs,
                dataType=type, uoms=uoms, values=allowedValues, default=None)

        return self.inputs[identifier]

    def addComplexInput(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                formats=[{"mimeType":"text/xml"}],maxmegabites=5):

        self.inputs[identifier] = InAndOutputs.ComplexInput(identifier=identifier,
                title=title,abstract=abstract,
                metadata=[],minOccurs=minOccurs,maxOccurs=maxOccurs,
                formats=formats, maxmegabites=maxmegabites)

        return self.inputs[identifier]


    def addBBoxInput(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                crss=[""]): #FIXME some default crss
        self.inputs[identifier] = InAndOutputs.BoundingBoxInput(self,
                identifier,title,abtract=abstract,
                metadata=metadata,minOccurs=minOccurs,maxOccurs=maxOccurs,
                crss=crss)

        return self.inputs[identifier]
 
    # --------------------------------------------------------------------

    def addComplexOutput(self,identifier,title,abstract=None,
            metadata=[],formats=[{"mimeType":"text/xml"}],
            asReference=False):

        self.outputs[identifier] = InAndOutputs.ComplexOutput(identifier=identifier,
                title=title,abstract=abstract,
                metadata=[], formats=formats, asReference=asReference)

        return self.outputs[identifier]

    def addLiteralOutput(self, identifier, title, abstract=None,
            uoms=(), type=types.IntType, default=None,
           asReference=False):
        """
        Add new output item of type LiteralValue to this process
        """

        self.outputs[identifier] = InAndOutputs.LiteralOutput(identifier=identifier,
                title=title, abstract=abstract, dataType=type, uoms=uoms, 
                default=None, asReference=asReference)

        return self.outputs[identifier]

    # --------------------------------------------------------------------
    def cmd(self,cmd,stdin=None):
        """Runs GRASS command, fetches all GRASS_MESSAGE and
        GRASS_PERCENT messages and sets self.status according to them, so
        the client application can track the progress information, when
        runing with Status=True

        This module is supposed to be used instead of 'os.system()', while
        running GRASS modules
        
        Example Usage:
            self.Gcmd("r.los in=elevation.dem out=los coord=1000,1000")

            self.Gcmd("v.net.path network afcol=forward abcol=backward \
            out=mypath nlayer=1","1 9 12")
            """

        self.message("PyWPS Cmd: %s\n" % (cmd.strip()))

        try:
            p = subprocess.Popen(cmd,shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,)
        except Exception,e :
            self.failed = True
            raise Exception("Could not perform command [%s]: %s" % (cmd,e))

        (stdout, stderr) = p.communicate(stdin)

        retcode = p.wait()

        if retcode != 0:
           self.status.setProcessStatus("processFailed", True)
           self.message("PyWPS stderr: %s\n" % (stderr),True)
           raise Exception("PyWPS could not perform command [%s]:\n%s" % (cmd,stderr))

        return stdout.splitlines()

    def message(self,msg,force=False):
        if self.debug or force:
            sys.stderr.write(msg)
        return

    def getInput(self,identifier):
        try:
            return self.inputs[identifier]
        except:
            return None

    def getInputValue(self,identifier):
        try:
            return self.inputs[identifier].value
        except:
            return None

    def setOutputValue(self,identifier,value):
        try:
            return self.outputs[identifier].setValue(value)
        except:
            return None

    def i18n(self,key):
        return self.lang.get(key)

