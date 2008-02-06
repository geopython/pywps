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


import subprocess
import Wps.wpsexceptions
from Wps.wpsexceptions import *
import time
import Inputs
import types

class Status:
    def __init__(self):
        self.creationTime = time.time()
        self.processAccepted = False
        self.processStarted = False
        self.processPaused = False
        self.processSucceeded = False
        self.processFailed = False

        self.processCompleted = 0
        self.exceptionReport = None


class WPSProcess:
    """
    """
    def __init__(self, identifier, title, abstract=None,
            metadata=[],profile=[], version=None,
            statusSupported=True, storeSupported=False):

        self.identifier = identifier
        self.version = version
        self.metadata = metadata
        self.title = title
        self.abstract = abstract
        self.wsdl  = None
        self.profile = profile
        self.storeSupported = storeSupported
        self.statusSupported = statusSupported

        self.status = Status()
        self.inputs = {}
        self.outputs = {}

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

        self.inputs[identifier] = Inputs.LiteralInput(identifier=identifier,
                title=title, abstract=abstract, metadata=[],
                minOccurs=minOccurs,maxOccurs=maxOccurs,
                dataType=type, uoms=uoms, values=allowedValues, default=None)

        return self.inputs[identifier]

    def addComplexInput(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                formats=[{"mimetype":"text/xml"}],maxmegabites=0.1):

        self.inputs[identifier] = Inputs.ComplexInput(identifier=identifier,
                title=title,abstract=abstract,
                metadata=[],minOccurs=minOccurs,maxOccurs=maxOccurs,
                formats=formats, maxmegabites=maxmegabites)

        return self.inputs[identifier]


    def addBBoxInput(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                crss=[""]): #FIXME some default crss
        self.inputs[identifier] = Inputs.BoundingBoxInput(self,
                identifier,title,abtract=abstract,
                metadata=metadata,minOccurs=minOccurs,maxOccurs=maxOccurs,
                crss=crss)

        return self.inputs[identifier]
 
    # --------------------------------------------------------------------

    def addComplexOutput(self,identifier,title,abstract=None,
            metadata=[],formats=[{"mimetype":"text/xml"}]):

        self.outputs[identifier] = Inputs.ComplexOutput(identifier=identifier,
                title=title,abstract=abstract,
                metadata=[], formats=formats)

        return self.outputs[identifier]

    def addLiteralOutput(self, identifier, title, abstract=None,
            uoms=(), type=types.IntType, default=None):
        """
        Add new output item of type LiteralValue to this process
        """

        self.outputs[identifier] = Inputs.LiteralOutput(identifier=identifier,
                title=title, abstract=abstract, dataType=type, uoms=uoms, 
                default=None)

        return self.outputs[identifier]
