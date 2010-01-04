"""
WPS Execute request handler
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
#               jachym at les-ejk dot cz
# License:
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

from Response import Response
from htmltmpl import TemplateError
import time,os,sys,tempfile,re,types, ConfigParser, base64, traceback
from shutil import copyfile as COPY
from shutil import rmtree as RMTREE

try:
    from mapscript import *
except:
    pass

class Execute(Response):
    """
    This class performs the Execute request of WPS specification
    """

    # status variants
    accepted = "processaccepted"
    started = "processstarted"
    succeeded = "processsucceeded"
    paused = "processpaused"
    failed = "processfailed"
    curdir = os.path.abspath(os.path.curdir)

    # running process id
    pid = None

    # session ID
    id = ''

    # status location and file
    statusLocation = ''
    statusFileName = None
    statusFiles = [sys.stdout]

    # process status
    storeRequired = False # should the request run asynchronously?
    statusRequired = False # should the status file be updated?
    lineageRequired = False # should the output have lineage?
    status = None
    statusMessage = None
    percent = 0
    exceptioncode = None
    locator = 0
    percent = 0
    statusTime = None

    # directories, which should be removed
    dirsToBeRemoved = []

    # working directory and grass
    workingDir = ""
    grass = None

    rawDataOutput = None
    logFile = None

    mapObj = None
    mapFileName = None


    def __init__(self,wps):
        """
        wps   - parent WPS instance
        """

        Response.__init__(self,wps)

        self.wps = wps
        self.process = None
        try:
            self.template = self.templateManager.prepare(self.templateFile)
        except TemplateError,e:
            traceback.print_exc(file=sys.stderr)
            self.cleanEnv()
            raise self.wps.exceptions.NoApplicableCode(e.__str__())

        # initialization
        self.setLogFile()
        self.statusTime = time.time()
        self.pid = os.getpid()
        self.status = None
        self.id = self.makeSessionId()
        self.statusFileName = os.path.join(self.wps.getConfigValue("server","outputPath"),self.id+".xml")
        self.statusLocation = self.wps.getConfigValue("server","outputUrl")+"/"+self.id+".xml"

        # TODO: Uniform parsing in Post and Get because now they differ
        # rawDataOutput
        if len(self.wps.inputs["responseform"]["rawdataoutput"])>0:
            if type(self.wps.inputs["responseform"]["rawdataoutput"]) == types.ListType:
                self.rawDataOutput = self.wps.inputs["responseform"]["rawdataoutput"][0].values()[0]
            elif type(self.wps.inputs["responseform"]["rawdataoutput"]) == types.DictType:
                self.rawDataOutput = self.wps.inputs["responseform"]["rawdataoutput"].keys()[0]

        # is status required
        self.statusRequired = False
        if self.wps.inputs["responseform"]["responsedocument"].has_key("status"):
            if self.wps.inputs["responseform"]["responsedocument"]["status"]:
                self.statusRequired = True

        # is store response required ?
        self.storeRequired = False
        if self.wps.inputs["responseform"]["responsedocument"].has_key("storeexecuteresponse"):
            if self.wps.inputs["responseform"]["responsedocument"]["storeexecuteresponse"]:
                try:
                    self.statusFiles.append(open(self.statusFileName,"w"))
                except Exception, e:
                    traceback.print_exc(file=sys.stderr)
                    self.cleanEnv()
                    raise self.wps.exceptions.NoApplicableCode(e.__str__())
                self.storeRequired = True

        # is lineage required ?
        lineageRequired = False
        if self.wps.inputs["responseform"].has_key("responsedocument"):
            if self.wps.inputs["responseform"]["responsedocument"].has_key("lineage") and \
                self.wps.inputs["responseform"]["responsedocument"]["lineage"] == True:
                lineageRequired = True

        # setInput values
        self.initProcess()

        # check rawdataoutput against process
        if self.rawDataOutput and self.rawDataOutput not in self.process.outputs:
            self.cleanEnv()
            raise self.wps.exceptions.InvalidParameterValue("rawDataOutput")

        # check storeExecuteResponse against process
        if self.storeRequired and not self.process.storeSupported:
            self.cleanEnv()
            raise self.wps.exceptions.StorageNotSupported(
                "storeExecuteResponse is true, but the process does not support output storage")

        # check status against process
        if self.statusRequired and not self.process.statusSupported:
            self.cleanEnv()
            raise self.wps.exceptions.InvalidParameterValue(
                "status is true, but the process does not support status updates")

        # OGC 05-007r7 page 43
        # if status is true and storeExecuteResponse is false, raise an exception
        if self.statusRequired and not self.storeRequired:
            self.cleanEnv()
            raise self.wps.exceptions.InvalidParameterValue(
                "status is true, but storeExecuteResponse is false")

        # HEAD
        self.templateProcessor.set("encoding",
                                    self.wps.getConfigValue("wps","encoding"))
        self.templateProcessor.set("lang",
                                    self.wps.inputs["language"])
        self.templateProcessor.set("statuslocation",
                                    self.statusLocation)
        self.templateProcessor.set("serviceinstance",
                                    self.serviceInstanceUrl())
        # Description
        self.processDescription()

        # Asynchronous request
        # OGC 05-007r7 page 36, Table 50, note (a)
        # OGC 05-007r7 page 42
        if self.storeRequired and self.statusRequired:
            # set status to accepted
            self.promoteStatus(self.accepted,"Process %s accepted" %\
                    self.process.identifier)

            # remove stdout from statusFiles
            self.statusFiles.remove(sys.stdout)

            # apache 1.x requires forking for asynchronous requests
            serverSoft=os.getenv("SERVER_SOFTWARE")
            forkingRequired=serverSoft and serverSoft.lower().startswith("apache/1.")

            # FIXME: forking is always required, unless we find some better
            # solution
            forkingRequired = True

            if forkingRequired:
                try:
                    # this is the parent process
                    if os.fork():
                        # exit here
                        return
                    # this is the child process
                    else:
                        # continue execution
                        pass

                except OSError, e:
                    traceback.print_exc(file=sys.stderr)
                    raise self.wps.exceptions.NoApplicableCode("Fork failed: %d (%s)\n" % (e.errno, e.strerror) )

            # this is child process, parent is already gone away
            # redirect stdout, so that apache sends back the response immediately
            si = open(os.devnull, 'r')
            so = open(os.devnull, 'a+')
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())

        # attempt to execute
        try:

            # init environment variable
            self.initEnv()

            # download and consolidate data
            self.consolidateInputs()

            # set output data attributes defined in the request
            self.consolidateOutputs()

            # Execute
            self.executeProcess()

        except self.wps.exceptions.WPSException,e:
            # set status to failed
            self.promoteStatus(self.failed,
                     statusMessage=e.value,
                     exceptioncode=e.code,
                     locator=e.locator)
        except Exception,e:

            # set status to failed
            traceback.print_exc(file=sys.stderr)
            self.promoteStatus(self.failed,
                    statusMessage=str(e),
                    exceptioncode="NoApplicableCode")

        # attempt to fill-in lineage and outputs
        try:

            # lineage in and outputs
            if lineageRequired:
                self.templateProcessor.set("lineage",1)
                self.lineageInputs()
                self.outputDefinitions()

            # if succeeded
            if self.status == self.succeeded:

                # mapscript support?
                try:
                    self._initMapscript()
                except Exception, e:
                    self.wps.debug("MapScript could not be loaded, mapserver not supported: %s" %e,"Warning")

                # fill outputs
                self.processOutputs()

                if self.mapObj:
                    self.mapObj.save(self.mapFileName)


                # Response document
                self.response = self.templateProcessor.process(self.template)

                # if rawDataOutput is required
                if self.rawDataOutput:
                    self.response = None
                    self.printRawData()

            # Failed but output lineage anyway
            elif lineageRequired:
                self.response = self.templateProcessor.process(self.template)


        except self.wps.exceptions.WPSException,e:
            # set status to failed
            self.promoteStatus(self.failed,
                    statusMessage=e.value,
                    exceptioncode=e.code,
                    locator=e.locator)
            # Response document
            self.response = self.templateProcessor.process(self.template)

        except Exception,e:
            # set status to failed
            traceback.print_exc(file=sys.stderr)
            self.promoteStatus(self.failed,
                    statusMessage=str(e),
                    exceptioncode="NoApplicableCode")
            # Response document
            self.response = self.templateProcessor.process(self.template)

        # print status
        if self.storeRequired and self.statusRequired:
            self.printResponse(self.statusFiles)

        # remove all temporary files
        self.cleanEnv()

    def initProcess(self):
        """
        Setting and controlling input values, set by the client. Also the
        processes from PYWPS_PROCESS directory or default directory is
        imported.
        """

        # import the right package
        if self.wps.inputs["identifier"] in self.processes.__all__:
            try:
                module = __import__(self.processes.__name__, None, None,
                                        [str(self.wps.inputs["identifier"])])
                self.process = eval("module."+self.wps.inputs["identifier"]+".Process()")

            except Exception, e:
                self.cleanEnv()
                traceback.print_exc(file=sys.stderr)
                raise self.wps.exceptions.NoApplicableCode(
                "Could not import process [%s]: %s" %\
                        (self.wps.inputs["identifier"], e))
                return
        else:
            self.cleanEnv()
            raise self.wps.exceptions.InvalidParameterValue(
                    self.wps.inputs["identifier"])


        # set proper method for status change
        self.process.wps = self.wps
        self.process.status.onStatusChanged = self.onStatusChanged
        self.process.debug = self.wps.getConfigValue("server","debug")
        self.process.logFile = self.logFile

    def consolidateInputs(self):
        """ Donwload and control input data, defined by the client """
        # calculate maximum allowed input size
        maxFileSize = self.calculateMaxInputSize()

        # set input values
        for identifier in self.process.inputs:

            # Status
            self.promoteStatus(self.paused,
                    statusMessage="Getting input %s of process %s" %\
                    (identifier, self.process.identifier))

            input = self.process.inputs[identifier]

            # exceptions handler
            input.onProblem = self.onInputProblem

            # maximum input file size must not be greater, than the one,
            # defined in the global config file
            if input.type == "ComplexValue":
                if not input.maxFileSize or input.maxFileSize > maxFileSize:
                    input.maxFileSize = maxFileSize

            try:
                for inp in self.wps.inputs["datainputs"]:
                    if unicode(inp["identifier"]) == unicode(identifier):
                        resp = input.setValue(inp)
                        if resp:
                            self.cleanEnv()
                            raise self.wps.exceptions.InvalidParameterValue(resp)
            except KeyError,e:
                pass

        # make sure, all inputs do have values
        for identifier in self.process.inputs:
            input = self.process.inputs[identifier]

            if not input.value and input.minOccurs > 0:
                self.cleanEnv()
                raise self.wps.exceptions.MissingParameterValue(identifier)

    def consolidateOutputs(self):
        """Set desired attributes (e.g. asReference) for each output"""
        if self.wps.inputs["responseform"]["responsedocument"].has_key("outputs"):
            respOutputs = self.wps.inputs["responseform"]["responsedocument"]["outputs"]
            for identifier in self.process.outputs:
                poutput = self.process.outputs[identifier]
                respOut = None
                for out in respOutputs:
                    if out["identifier"] == identifier:
                        respOut = out

                if respOut:
                    # asReference
                    if respOut.has_key("asreference") and \
                        "asReference" in dir(poutput):
                        poutput.asReference = respOut["asreference"]

                    # mimetype
                    if respOut.has_key("mimetype") and \
                        "format" in dir(poutput):
                        if respOut["mimetype"] != '':
                            poutput.format["mimeType"] = respOut["mimetype"]

                    # schema
                    if respOut.has_key("schema") and \
                        "format" in dir(poutput):
                        if respOut["schema"] != '':
                            poutput.format["schema"] = respOut["schema"]

                    # encoding
                    if respOut.has_key("encoding") and \
                        "format" in dir(poutput):
                        if respOut["encoding"] != '':
                            poutput.format["encoding"] = respOut["encoding"]

                    # uom
                    if respOut.has_key("uom") and \
                        "uom" in dir(poutput):
                        if respOut["uom"] != '':
                            poutput.uom = respOut["uom"]

    def onInputProblem(self,what,why):
        """
        This method is used for rewriting onProblem method of each input

        what - locator of the problem
        why - possible reason of the problem
        """

        exception = None

        if what == "FileSizeExceeded":
            exception = self.wps.exceptions.FileSizeExceeded
        elif what == "NoApplicableCode":
            exception = self.wps.exceptions.NoApplicableCode

        self.cleanEnv()
        raise exception(why)

    def executeProcess(self):
        """
        Calls 'execute' method of the process, catches possible exceptions
        and set process failed or succeeded
        """
        try:
            # set status to started
            self.promoteStatus(self.started,"Process %s started" %\
                    self.process.identifier)
            # execute
            processError = self.process.execute()
            if processError:
                traceback.print_exc(file=sys.stderr)
                raise self.wps.exceptions.NoApplicableCode(
                        "Failed to execute WPS process [%s]: %s" %\
                                (self.process.identifier,processError))
            else:
                # set status to succeeded
                self.promoteStatus(self.succeeded,
                        statusMessage="PyWPS Process %s successfully calculated" %\
                        self.process.identifier)

        # re-raise WPSException, will be caught outside
        except self.wps.exceptions.WPSException,e:
            raise e

        except Exception,e:
            traceback.print_exc(file=sys.stderr)
            raise self.wps.exceptions.NoApplicableCode(
                    "Failed to execute WPS process [%s]: %s" %\
                            (self.process.identifier,e))

    def processDescription(self):
        """
        Fills Identifier, Title and Abstract, eventually WSDL, Metadata and Profile
        parts of the output XML document
        """

        self.templateProcessor.set("identifier", self.process.identifier)
        self.templateProcessor.set("title", self.process.i18n(self.process.title))
        if self.process.abstract:
            self.templateProcessor.set("abstract", self.process.i18n(self.process.abstract))
        if self.process.metadata:
            metadata=[]
            for meta in self.process.metadata:
                metadata.append({"metadatatitle":meta})
            self.templateProcessor.set("Metadata", metadata)
        if self.process.profile:
            profiles=[]
            if type(self.process.profile) == types.ListType:
                for profile in self.process.profile:
                    profiles.append({"profile":profile})
            else:
                profiles.append({"profile":self.process.profile})
            self.templateProcessor.set("Profiles", profiles)
        if self.process.wsdl:
            self.templateProcessor.set("wsdl", self.process.wsdl)
        if self.process.version:
            self.templateProcessor.set("processversion", self.process.version)

    def promoteStatus(self,status,
                    statusMessage=0, percent=0,
                    exceptioncode=0, locator=0,
                    output=None):
        """
        Sets status of currently performed Execute request

        {String} status -  name of the status
        {String} statusMessage - message, which should appear in output xml file
        {Float} percent - percent done message
        {String} exceptioncode - eventually exception
        {String} locator - where the problem occurred
        """
        self.statusTime = time.time()
        self.templateProcessor.set("statustime", time.ctime(self.statusTime))
        self.status = status
        if statusMessage != 0: self.statusMessage = statusMessage
        if percent != 0: self.percent = percent
        if exceptioncode != 0: self.exceptioncode = exceptioncode
        if locator != 0: self.locator = locator

        # init value
        self.templateProcessor.set("processstarted",0)
        self.templateProcessor.set("processsucceeded",0)
        self.templateProcessor.set("processpaused",0)
        self.templateProcessor.set("processfailed",0)
        self.templateProcessor.set("processaccepted",0)

        if self.status == self.accepted:
            self.templateProcessor.set("processaccepted",
                    self.statusMessage)

        elif self.status == self.started:
            self.templateProcessor.set("processstarted", self.statusMessage)
            self.templateProcessor.set("percentcompleted", self.percent)

        elif self.status == self.succeeded:
            self.process.status.set(msg=self.statusMessage, percentDone=100, propagate=False)
            self.templateProcessor.set("percentcompleted", self.percent)
            self.templateProcessor.set("processsucceeded",
                                                self.statusMessage)

        elif self.status == self.paused:
            self.templateProcessor.set("processpaused", self.statusMessage)
            self.templateProcessor.set("percentcompleted", self.percent)

        elif self.status == self.failed:
            self.templateProcessor.set("processfailed", 1)
            if self.statusMessage:
                self.templateProcessor.set("exceptiontext", self.statusMessage)
            self.templateProcessor.set("exceptioncode", self.exceptioncode)
            if self.locator:
                self.templateProcessor.set("locator", self.locator)

        # update response
        self.response = self.templateProcessor.process(self.template)

        # print status
        if self.storeRequired and (self.statusRequired or
                                   self.status == self.accepted or
                                   #self.status == self.succeeded or
                                   self.status == self.failed):
            self.printResponse(self.statusFiles)
        
        if self.status == self.started:
            print >>sys.stderr, "PyWPS Status [%s][%.1f]: %s" % (self.status,float(self.percent),self.statusMessage)
        else:
            print >>sys.stderr, "PyWPS Status [%s]: %s" % (self.status,self.statusMessage)


    def lineageInputs(self):
        """
        Called, if lineage request was set. Fills the <DataInputs> part of
        output XML document.
        """
        templateInputs = []

        for identifier in self.process.inputs.keys():
            input = self.process.inputs[identifier]

            for wpsInput in self.wps.inputs["datainputs"]:
                if wpsInput["identifier"] != identifier or\
                        wpsInput.has_key("lineaged"):
                    continue

                templateInput = {}
                wpsInput["lineaged"] = True

                templateInput["identifier"] = input.identifier
                templateInput["title"] = self.process.i18n(input.title)
                templateInput["abstract"] = self.process.i18n(input.abstract)

                if input.type == "LiteralValue":
                    templateInput = self._lineageLiteralInput(input,wpsInput,templateInput)
                elif input.type == "ComplexValue" and \
                       wpsInput.has_key("asReference") and wpsInput["asReference"] == True:
                    templateInput = self._lineageComplexReferenceInput(wpsInput,
                                                                input,templateInput)
                elif input.type == "ComplexValue":
                    templateInput = self._lineageComplexInput(input,templateInput)
                elif input.type == "BoundingBoxValue":
                    templateInput = self._lineageBBoxInput(input,templateInput)

                templateInputs.append(templateInput)

        self.templateProcessor.set("Inputs",templateInputs)

    def _lineageLiteralInput(self, input, wpsInput, literalInput):
        """
        Fill input of literal data
        """
        literalInput["literaldata"] = wpsInput["value"]
        literalInput["uom"] = str(input.uom)
        return literalInput

    def _lineageComplexInput(self, input, complexInput):
        """
        Fill input of complex data
        """
        complexInput["complexdata"] = open(input.value,"r").read()
        complexInput["encoding"] = input.format["encoding"]
        complexInput["mimetype"] = input.format["mimeType"]
        complexInput["schema"] = input.format["schema"]
        return complexInput

    def _lineageComplexReferenceInput(self, wpsInput, processInput, complexInput):
        """
        Fill reference input

        wpsInput - associative field of self.wps.inputs["datainputs"]
        processInput - self.process.inputs
        """
        complexInput["reference"] = wpsInput["value"]
        method = "GET"
        if wpsInput.has_key("method"):
            method = wpsInput["method"]
        complexInput["method"] = method
        complexInput["mimeType"] = processInput.format["mimeType"]
        complexInput["encoding"] = processInput.format["encoding"]
        if wpsInput.has_key("header") and wpsInput["header"]:
            complexInput["header"] = 1
            complexInput["key"] = wpsInput["header"].keys()[0]
            complexInput["value"] = wpsInput["header"][wpsInput["header"].keys()[0]]
        if wpsInput.has_key("body") and wpsInput["body"]:
            complexInput["body"] = wpsInput["body"]
        if wpsInput.has_key("bodyreference") and wpsInput["bodyreference"]:
            complexInput["bodyReference"] = wpsInput["bodyreference"]
        return complexInput

    def _lineageBBoxInput(self,input,bboxInput):
        """ Fill input of bbox data """
        bboxInput["bboxdata"] = 1
        bboxInput["crss"] = [input.crs]
        bboxInput["dimensions"] = input.dimensions
        bboxInput["minx"] = input.minx
        bboxInput["miny"] = input.miny
        bboxInput["maxx"] = input.maxx
        bboxInput["maxy"] = input.maxy
        return bboxInput

    def outputDefinitions(self):
        """
        Called, if lineage request was set. Fills the <OutputDefinitions> part of
        output XML document.
        """
        templateOutputs = []

        for identifier in self.process.outputs.keys():
            templateOutput = {}
            output = self.process.outputs[identifier]

            templateOutput["identifier"] = output.identifier
            templateOutput["title"] = self.process.i18n(output.title)
            templateOutput["abstract"] = self.process.i18n(output.abstract)

            if self.process.storeSupported and output.asReference:
                templateOutput["asreference"] = "true"
            else:
                templateOutput["asreference"] = "false"

            templateOutputs.append(templateOutput);

            if output.type == "LiteralValue":
                templateOutput = self._lineageLiteralOutput(output,templateOutput)
                templateOutput["literaldata"] = 1
            elif output.type == "ComplexValue":
                templateOutput = self._lineageComplexOutput(output,templateOutput)
                templateOutput["complexdata"] = 1
            else:
                templateOutput = self._lineageBBoxOutput(output,templateOutput)
                templateOutput["bboxdata"] = 1

        self.templateProcessor.set("Outputdefinitions",templateOutputs)

    def _lineageLiteralOutput(self, output, literalOutput):
        if len(output.uoms):
                literalOutput["uom"] = str(output.uoms[0])
        return literalOutput

    def _lineageComplexOutput(self, output, complexOutput):

        complexOutput["mimetype"] = output.format["mimeType"]
        complexOutput["encoding"] = output.format["encoding"]
        complexOutput["schema"] = output.format["schema"]

        return complexOutput

    def _lineageBBoxOutput(self, output, bboxOutput):

        bboxOutput["bboxdata"] = 1
        bboxOutput["crs"] = output.crs
        bboxOutput["dimensions"] = output.dimensions

        return bboxOutput

    def processOutputs(self):
        """Fill <ProcessOutputs> part in the output XML document
        This method is called if, self.status == ProcessSucceeded
        """

        templateOutputs = []

        for identifier in self.process.outputs.keys():
            try:
                templateOutput = {}
                output = self.process.outputs[identifier]

                templateOutput["identifier"] = output.identifier
                templateOutput["title"] = self.process.i18n(output.title)
                templateOutput["abstract"] = self.process.i18n(output.abstract)

                # Reference
                if output.asReference:
                    templateOutput = self._asReferenceOutput(templateOutput, output)
                # Data
                else:
                    templateOutput["reference"] = 0
                    if output.type == "LiteralValue":
                        templateOutput = self._literalOutput(output,templateOutput)
                    elif output.type == "ComplexValue":
                        templateOutput = self._complexOutput(output,templateOutput)
                    elif output.type == "BoundingBoxValue":
                        templateOutput = self._bboxOutput(output,templateOutput)

                templateOutputs.append(templateOutput);

            except Exception,e:
                self.cleanEnv()
                traceback.print_exc(file=sys.stderr)
                raise self.wps.exceptions.NoApplicableCode(
                        "Process executed. Failed to build final response for output [%s]: %s" % (identifier,e))
        self.templateProcessor.set("Outputs",templateOutputs)

    def _literalOutput(self, output, literalOutput):

        literalOutput["uom"] = str(output.uom)
        literalOutput["dataType"]= self.getDataTypeReference(output)["type"]
        literalOutput["literaldata"] = output.value

        return literalOutput

    def _complexOutput(self, output, complexOutput):

        complexOutput["mimeType"] = output.format["mimeType"]
        complexOutput["encoding"] = output.format["encoding"]
        complexOutput["schema"] = output.format["schema"]

        # CDATA section in output
        if output.format["mimeType"].find("text") < 0:
            #complexOutput["cdata"] = 1
            os.rename(output.value, output.value+".binary")
            base64.encode(open(output.value+".binary"),open(output.value,"w"))
            complexOutput["complexdata"] = open(output.value,"r").read()
        else:
            # set output value
            complexOutput["complexdata"] = open(output.value,"r").read()

        # remove <?xml version= ... part from beginning of some xml
        # documents
        if output.format["mimeType"].find("xml") or\
           output.format["mimeType"].find("gml") > -1:
            beginXml = complexOutput["complexdata"].split("\n")[0]
            if  beginXml.find("<?xml ") > -1:
                complexOutput["complexdata"] = complexOutput["complexdata"].replace(beginXml+"\n","")

        return complexOutput

    def _bboxOutput(self, output, bboxOutput):
        bboxOutput["bboxdata"] = 1
        bboxOutput["crs"] = output.crss[0]
        bboxOutput["dimensions"] = output.dimensions
        bboxOutput["minx"] = output.minx
        bboxOutput["miny"] = output.miny
        bboxOutput["maxx"] = output.maxx
        bboxOutput["maxy"] = output.maxy
        return bboxOutput

    def _asReferenceOutput(self,templateOutput, output):

        # copy the file to output directory
        # literal value
        if output.type == "LiteralValue":
            f = open(os.path.join(
                        self.wps.getConfigValue("server","outputPath"),
                                output.identifier+"-"+self.pid),"w")
            f.write(output.value)
            f.close()
            templateOutput["reference"] = self.wps.getConfigValue("server","outputUrl")+\
                    "/"+output.identifier+"-"+str(self.pid)
        # complex value
        else:
            outName = output.value
            outSuffix = outName.split(".")[len(outName.split("."))-1]
            outName = output.identifier+"-"+str(self.pid)+"."+outSuffix
            outFile = self.wps.getConfigValue("server","outputPath")+"/"+outName
            if not self._samefile(output.value,outFile):
                COPY(output.value, outFile)
            templateOutput["reference"] = \
                    self.wps.getConfigValue("server","outputUrl")+"/"+outName
            output.value = outFile

            # mapscript supported and the mapserver should be used for this
            # output
            # redefine the output 
            if self.mapObj and output.useMapscript:

                # get projection and bounding box
                if not output.projection or not output.bbox:
                    try:
                        if not output.projection:
                            from osgeo import gdal
                            dataset = gdal.Open(output.value)
                            output.projection = dataset.GetProjection()
                        if not output.projection:
                            output.projection = self.mapObj.getProjection()
                        if not output.bbox:
                            geotransform = dataset.GetGeoTransform()
                            output.bbox = (geotransform[0],
                                        geotransform[3]+geotransform[5]*dataset.RasterYSize,
                                        geotransform[0]+geotransform[1]*dataset.RasterXSize,
                                        geotransform[3])
                            output.width = dataset.RasterXSize
                            output.height = dataset.RasterYSize

                        myLayerObj = layerObj(self.mapObj)
                        myLayerObj.setMetaData("wms_title", output.title)
                        myLayerObj.setMetaData("wcs_label", output.title)
                        myLayerObj.setMetaData("wfs_title", output.title)
                        myLayerObj.group = self.process.identifier
                        myLayerObj.setMetaData("wms_group_title",self.process.title)
                        if self.process.abstract:
                            myLayerObj.setMetaData("group_abstract",self.process.abstract)
                        if output.abstract:
                            myLayerObj.setMetaData("wms_abstract", output.abstract)
                            myLayerObj.setMetaData("wcs_abstract", output.abstract)
                            myLayerObj.setMetaData("wfs_abstract", output.abstract)
                        myLayerObj.data = output.value
                        myLayerObj.name = output.identifier

                        if output.projection:
                            myLayerObj.setProjection("epsg:4326")
                        if output.bbox:
                            myLayerObj.setExtent(output.bbox[0],output.bbox[1],output.bbox[2],output.bbox[3])

                        # set the output to be WMS
                        if output.format["mimeType"].find("tiff") == -1:
                            templateOutput["reference"] = self._getMapServerWMS(output)
                            myLayerObj.type = MS_LAYER_RASTER
                        # make it WFS
                        elif output.format["mimeType"].find("text")  > -1:
                            templateOutput["reference"] = self._getMapServerWFS(output)
                        # make it WCS
                        else:
                            myLayerObj.type = MS_LAYER_RASTER
                            templateOutput["reference"] = self._getMapServerWCS(output)
                    except ImportError:
                        self.wps.debug("GDAL could not be loaded, mapserver not supported","Warning")

 
        templateOutput["mimetype"] = output.format["mimeType"]
        templateOutput["schema"] = output.format["encoding"]
        templateOutput["encoding"] = output.format["schema"]

        return templateOutput

    def _getMapServerWMS(self,output):
        """Get the URL for mapserver WMS request of the output"""
        import urllib2
        return urllib2.quote(self.wps.getConfigValue("mapserver","mapserveraddress")+
                "?map="+self.mapFileName+
                "&SERVICE=WMS"+ "&REQUEST=GetMap"+ "&VERSION=1.3.0"+
                "&LAYERS="+output.identifier+"&STYLES=default&SRS="+output.projection.replace("+init=","")+
                "&BBOX=%s,%s,%s,%s&"%(output.bbox[0],output.bbox[1],output.bbox[2],output.bbox[3])+
                "&WIDTH=%s"%output.width+"&HEIGHT=%s"%output.height+"&FORMAT=%s"%output.format["mimeType"])

    def _getMapServerWCS(self,output):
        """Get the URL for mapserver WCS request of the output"""
        import urllib2
        return urllib2.quote(self.wps.getConfigValue("mapserver","mapserveraddress")+
                "?map="+self.mapFileName+
                "&SERVICE=WCS"+ "&REQUEST=GetCoverage"+ "&VERSION=1.0.0"+
                "&COVERAGE="+output.identifier+"&CRS="+output.projection.replace("+init=","")+
                "&BBOX=%s,%s,%s,%s&"%(output.bbox[0],output.bbox[1],output.bbox[2],output.bbox[3])+
                "&WIDTH=%s"%output.width+"&HEIGHT=%s"%output.height+"&FORMAT=%s"%output.format["mimeType"])

    def _getMapServerWFS(self,output):
        """Get the URL for mapserver WFS request of the output"""
        import urllib2
        return urllib2.quote(self.wps.getConfigValue("mapserver","mapserveraddress")+
                "?map="+self.mapFileName+
                "&SERVICE=WFS"+ "&REQUEST=GetFeature"+ "&VERSION=1.0.0"+
                "&TYPENAME="+output.identifier)

    def _samefile(self, src, dst):
        # Macintosh, Unix.
        if hasattr(os.path,'samefile'):
            try:
                return os.path.samefile(src, dst)
            except OSError:
                return False

        # All other platforms: check for same pathname.
        return (os.path.normcase(os.path.abspath(src)) ==
                os.path.normcase(os.path.abspath(dst)))

    def makeSessionId(self):
        """
        Returns unique Execute session ID
        """
        return "pywps-"+str(int(time.time()*100))

    def getSessionIdFromStatusLocation(self,statusLocation):
        """
        Parses the statusLocation, and gets the unique session ID from it

        NOTE: Not in use, maybe should be removed.
        """
        begin = statusLocation.find("/pywps-")
        end = statusLocation.find(".xml")
        if begin > -1 and end > -1:
            return statusLocation[begin:end]
        else:
            return None

    def serviceInstanceUrl(self):
        """
        Creates URL of GetCapabilities for this WPS
        """
        serveraddress = self.wps.getConfigValue("wps","serveraddress")

        if not serveraddress.endswith("?") and \
           not serveraddress.endswith("&"):
            if serveraddress.find("?") > -1:
                serveraddress += "&"
            else:
                serveraddress += "?"

        serveraddress += "service=WPS&request=GetCapabilities&version="+self.wps.defaultVersion

        serveraddress = serveraddress.replace("&", "&amp;") # Must be done first!
        serveraddress = serveraddress.replace("<", "&lt;")
        serveraddress = serveraddress.replace(">", "&gt;")

        return serveraddress

    def onStatusChanged(self):
        """
        This method is used for redefinition of self.process.status class
        """

        self.promoteStatus(self.process.status.code,
                statusMessage=self.process.status.value,
                percent=self.process.status.percentCompleted)

    def initEnv(self):
        """Create process working directory, initialize GRASS environment,
        if required.

        """

        # find out number of running sessions
        maxOperations = int(self.wps.getConfigValue("server","maxoperations"))
        tempPath = self.wps.getConfigValue("server","tempPath")

        dirs = os.listdir(tempPath)
        pyWPSDirs = 0
        for dir in dirs:
            if dir.find("pywps") == 0:
                pyWPSDirs += 1

        if pyWPSDirs >= maxOperations and\
            maxOperations != 0:
            raise self.wps.exceptions.ServerBusy()

        # create temp dir
        self.workingDir = tempfile.mkdtemp(prefix="pywps", dir=tempPath)

        self.workingDir = os.path.join(
                self.wps.getConfigValue("server","tempPath"),self.workingDir)

        os.chdir(self.workingDir)
        self.dirsToBeRemoved.append(self.workingDir)

        # init GRASS
        try:
            if self.process.grassLocation:
                from pywps import Grass
                grass = Grass.Grass(self)
                if self.process.grassLocation == True:
                    self.process.grassMapset = grass.mkMapset()
                elif os.path.exists(os.path.join(self.wps.getConfigValue("grass","gisdbase"),self.process.grassLocation)):
                    self.process.grassMapset = grass.mkMapset(self.process.grassLocation)
                else:
                    raise Exception("Location [%s] does not exist" % self.process.grassLocation)
        except Exception,e:
            self.cleanEnv()
            traceback.print_exc(file=sys.stderr)
            raise self.wps.exceptions.NoApplicableCode("Could not init GRASS: %s" % e)

        return

    def cleanEnv(self):
        """
        Removes temporary created files and dictionaries
        """
        os.chdir(self.curdir)
        def onError(*args):
            self.wps.debug("Could not remove temporary dir","Error")

        for i in range(len(self.dirsToBeRemoved)):
            dir = self.dirsToBeRemoved[0]
            if os.path.isdir(dir) and dir != "/":
                RMTREE(dir, onerror=onError)
                pass
            self.dirsToBeRemoved.remove(dir)


    def calculateMaxInputSize(self):
        maxSize = self.wps.getConfigValue("server","maxfilesize")
        maxSize = maxSize.lower()

        units = re.compile("[gmkb].*")
        size = float(re.sub(units,'',maxSize))

        if maxSize.find("g") > -1:
            size *= 1024*1024*1024
        elif maxSize.find("m") > -1:
            size *= 1024*1024
        elif maxSize.find("k") > -1:
            size *= 1024
        else:
            size *= 1

        return size

    def printRawData(self):
        """
        Prints raw data to sys.stdout with correct content-type, according
        to mimeType attribute or output value
        """

        output = self.process.outputs[self.rawDataOutput]
        if output.type == "LiteralValue":
            print "Content-type: text/plain\n"
            print output.value
        elif output.type == "ComplexValue":
            f = open(output.value,"rb")
            print "Content-type: %s\n" % output.format["mimeType"]
            print f.read()
            f.close()

    def setLogFile(self):
        """Set self.logFile to sys.stderr or something else
        """

        # logfile
        self.logFile = sys.stderr
        try:
            self.logFile = self.wps.getConfigValue("server","logFile")
            if self.logFile:
                se = open(self.logFile, 'a+', 0)
                os.dup2(se.fileno(), sys.stderr.fileno())
            else:
                self.logFile = sys.stderr
        except ConfigParser.NoOptionError,e:
            pass
        except IOError,e:
            traceback.print_exc(file=sys.stderr)
            raise self.wps.exceptions.NoApplicableCode("Logfile IOError: %s" % e.__str__())
        except Exception, e:
            traceback.print_exc(file=sys.stderr)
            raise self.wps.exceptions.NoApplicableCode("Logfile error: %s" % e.__str__())


    def _initMapscript(self):
        """Create self.mapObj"""

        self.mapObj = mapObj()
        self.mapObj.setExtent(-180,-90,180,90)
        self.mapObj.setProjection("+init=epsg:4326")
        self.mapObj.name = "%s-%s"%(self.process.identifier,self.pid)
        self.mapObj.setMetaData("ows_title", self.wps.getConfigValue("wps","title"))
        self.mapObj.setMetaData("wms_abstract", self.wps.getConfigValue("wps","abstract"))
        self.mapObj.setMetaData("wcs_abstract", self.wps.getConfigValue("wps","abstract"))
        self.mapObj.setMetaData("wfs_abstract", self.wps.getConfigValue("wps","abstract"))
        self.mapObj.setMetaData("ows_keywordlist", self.wps.getConfigValue("wps","keywords"))
        self.mapObj.setMetaData("ows_fees", self.wps.getConfigValue("wps","fees"))
        self.mapObj.setMetaData("ows_accessconstraints", self.wps.getConfigValue("wps","constraints"))
        self.mapObj.setMetaData("ows_contactorganization", self.wps.getConfigValue("provider","providerName"))
        self.mapObj.setMetaData("ows_contactperson", self.wps.getConfigValue("provider","individualName"))
        self.mapObj.setMetaData("ows_contactposition", self.wps.getConfigValue("provider","positionName"))
        phone =  self.wps.getConfigValue("provider","phoneVoice")
        if phone:
            self.mapObj.setMetaData("ows_contactvoicetelephone", self.wps.getConfigValue("provider","phoneVoice"))
        phone = self.wps.getConfigValue("provider","phoneFacsimile")
        if phone:
            self.mapObj.setMetaData("ows_contactfacsimiletelephone", self.wps.getConfigValue("provider","phoneFacsimile"))
        self.mapObj.setMetaData("ows_address", self.wps.getConfigValue("provider","deliveryPoint"))
        self.mapObj.setMetaData("ows_city", self.wps.getConfigValue("provider","city"))
        self.mapObj.setMetaData("ows_country", self.wps.getConfigValue("provider","country"))
        self.mapObj.setMetaData("ows_postcode", self.wps.getConfigValue("provider","postalCode"))
        self.mapObj.setMetaData("ows_contactelectronicmailaddress", self.wps.getConfigValue("provider","electronicMailAddress"))
        self.mapObj.setMetaData("ows_role", self.wps.getConfigValue("provider","role"))

        self.mapFileName = os.path.join(self.wps.getConfigValue("server","outputPath"),"wps"+str(self.pid)+".map")

        self.mapObj.setMetaData("wms_onlineresource",self.wps.getConfigValue("mapserver","mapserveraddress")+"?map="+self.mapFileName)

