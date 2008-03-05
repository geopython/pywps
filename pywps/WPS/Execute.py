"""
WPS Execute request handler
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

from Request import Request
import time

class Execute(Request):
    """
    """
    accepted = "processaccepted"
    started = "processstarted"
    succeeded = "processsucceeded"
    paused = "processpaused"
    failed = "processfailed"

    status = 0
    processstatus = 0
    percent = 0
    exceptioncode = 0
    locator = 0

    percent = 0
    processstatus = 0

    def __init__(self,wps):
        """
        Arguments:
           self
           wps   - parent WPS instance
        """

        Request.__init__(self,wps)

        self.wps = wps
        self.process = None

        self.template = self.templateManager.prepare(self.templateFile)

        #
        # initialization
        #
        self.statusTime = time.time()
        self.status = None

        #
        # setInput values
        #
        self.initProcess()

        #
        # HEAD
        #
        self.templateProcessor.set("encoding",
                                    self.wps.getConfigValue("wps","encoding"))
        self.templateProcessor.set("lang",
                                    self.wps.getConfigValue("wps","lang"))
        self.templateProcessor.set("version",
                                    self.wps.getConfigValue("wps","version"))


        #
        # Process
        #
        self.processDescription()

        #
        # Status
        #
        self.setStatus(self.accepted)

        #
        # lineage
        #
        if self.wps.inputs['responseform']['responsedocument']['lineage']:
            self.lineageInputs()

        self.response = self.templateProcessor.process(self.template)

        return

    def initProcess(self):
        if self.wps.inputs["identifier"] in self.processes.__all__:
            try:
                module = __import__(self.processes.__name__,fromlist=[self.wps.inputs["identifier"]])
                self.process = eval("module."+self.wps.inputs["identifier"]+".Process()")

            except Exception, e:
                print e
                pass #FIXME - process not loaded
                return
        else:
            print "invalid parameter valule" # FIXME
            return

        # set input values
        for identifier in self.process.inputs:
            input = self.process.inputs[identifier]

            try:
                input.setValue(self.wps.inputs["datainputs"][identifier]["value"])
            except KeyError,e:
                pass

        # make sure, all inputs do have values
        for identifier in self.process.inputs:
            input = self.process.inputs[identifier]

            if not input.value:
                raise self.wps.exceptions.MissingParameterValue(identifier)



    def processDescription(self):

        self.templateProcessor.set("title", self.process.title)
        self.templateProcessor.set("abstract", self.process.abstract)
        self.templateProcessor.set("identifier", self.process.identifier)

        #self.templateProcessor.set("profile", self.process.profile)
        #self.templateProcessor.set("wsdl", self.process.wsdl)

    def setStatus(self,status,
                    processstatus=0, percent=0,
                    exceptioncode=0, locator=0):
        
        self.templateProcessor.set("statustime", time.ctime(self.statusTime))
        self.status = status
        if processstatus != 0: self.processstatus = processstatus 
        if percent != 0: self.percent = percent 
        if exceptioncode != 0: self.exceptioncode = exceptioncode 
        if locator != 0: self.locator = locator 

        # init value
        self.templateProcessor.set("processstarted", 0)
        self.templateProcessor.set("processsucceeded", 0)
        self.templateProcessor.set("processpaused", 0)
        self.templateProcessor.set("processfailed", 0)

        if self.status == self.accepted:
            self.templateProcessor.set("processaccepted", "true")

        elif self.status == self.started:
            self.templateProcessor.set("processstarted", "true")
            self.templateProcessor.set("percentcompleted", self.percent*100)

        elif self.status == self.succeeded:
            self.templateProcessor.set("processstarted",
                                                self.processstatus)

        elif self.status == self.paused:
            self.templateProcessor.set("processpaused", self.processstatus)
            self.templateProcessor.set("percentcompleted", self.percent)

        elif self.status == self.failed:
            self.templateProcessor.set("exceptiontext", self.processstatus)
            self.templateProcessor.set("exceptioncode", self.exceptioncode)

    def lineageInputs(self):
        templateInputs = []
        self.templateProcessor.set("lineage",1)
    
        for identifier in self.process.inputs.keys():
            templateInput = {}
            input = self.process.inputs[identifier]

            templateInput["identifier"] = input.identifier
            templateInput["title"] = input.title
            templateInput["abstract"] = input.abstract

            templateInputs.append(templateInput);

            if input.type == "LiteralValue":
                templateInput = self.lineageLiteralInput(input,templateInput)
            elif input.type == "ComplexValue":
                templateInput = self.lineageComplexInput(input,templateInput)
            elif input.type == "BoundingBoxValue":
                templateInput = self.lineageBboxInput(input,templateInput)

        self.templateProcessor.set("Inputs",templateInputs)

    def lineageLiteralInput(self, input, literalInput):
        literalInput["literaldata"] = input.value
        literalInput["uom"] = str(input.uom)
        return literalInput

    def lineageComplexInput(self, input, complexInput):
        complexInput["complexdata"] = input.value
        complexInput["encoding"] = input.format["encoding"]
        complexInput["mimetype"] = input.format["mimetype"]
        complexInput["schema"] = input.format["schema"]
        return complexInput

    def lineageBboxInput(self,input,bboxInput):
        bboxInput["bboxdata"] = 1
        bboxInput["crs"] = input.crs
        bboxInput["dimensions"] = input.dimensions
        bboxInput["minx"] = input.value[0]
        bboxInput["miny"] = input.value[1]
        bboxInput["maxx"] = input.value[2]
        bboxInput["maxy"] = input.value[3]

        return bboxInput


