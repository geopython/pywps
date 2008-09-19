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

from Response import Response
from htmltmpl import TemplateError
import time,os,sys,tempfile,re
from shutil import copyfile as COPY
from shutil import rmtree as RMTREE

class Execute(Response):
    """
    This class performs the Execute request of WPS specification

    In the class, fork of the  processes has to be done, if the client
    requested asynchronous request performance (status=true)
    """

    # status variants
    accepted = "processaccepted"
    started = "processstarted"
    succeeded = "processsucceeded"
    paused = "processpaused"
    failed = "processfailed"

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


    def __init__(self,wps):
        """
        wps   - parent WPS instance
        """

        Response.__init__(self,wps)

        self.wps = wps
        self.process = None
        try:
            self.template = self.templateManager.prepare(self.templateFile)
        except TemplateError:
            self.cleanEnv()
            raise self.wps.exceptions.InvalidParameterValue("version")

        # initialization
        self.statusTime = time.time()
        self.pid = os.getpid()
        self.status = None
        self.id = self.makeSessionId()
        self.statusFileName = os.path.join(self.wps.getConfigValue("server","outputPath"),self.id+".xml")
        self.statusLocation = self.wps.getConfigValue("server","outputUrl")+"/"+self.id+".xml"

        # rawDataOutput
        if self.wps.inputs["responseform"]["rawdataoutput"]:
            self.rawDataOutput = self.wps.inputs["responseform"]["rawdataoutput"][0].values()[0]

        # is status required
        self.statusRequired = False
        if self.wps.inputs["responseform"]["responsedocument"].has_key("status"):
            if self.wps.inputs["responseform"]["responsedocument"]["status"]:
                self.statusRequired = True

        # is store response required ?
        self.storeRequired = False
        if self.wps.inputs["responseform"]["responsedocument"].has_key("storeexecuteresponse"):
            if self.wps.inputs["responseform"]["responsedocument"]["storeexecuteresponse"]:
                self.statusFiles.append(open(self.statusFileName,"w"))
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
            raise self.wps.exceptions.InvalidParameterValue(
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

        # OGC 05-007r7 page 36, Table 49
        # Either responseDocument or rawDataOutput should be specified
        if self.rawDataOutput and self.storeRequired:
            self.cleanEnv()
            raise self.wps.exceptions.InvalidParameterValue(
                "Either responseDocument or rawDataOutput should be specified, but not both")


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
        if self.storeRequired:
            # Output response to client
            print "Content-type: text/xml\n"
            # set status to accepted
            self.promoteStatus(self.accepted,"Process %s accepted" %\
                    self.process.identifier)

            # redirect stdout, so that apache sends back the response immediately
            so = open(os.devnull, 'a+')
            os.dup2(so.fileno(), sys.stdout.fileno())

            # remove stdout and add statusFileName to statusFiles
            self.statusFiles.remove(sys.stdout)
            if len(self.statusFiles) == 0:
                self.statusFiles = [open(self.statusFileName,"w")]

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

        except Exception,ex:
            # set status to failed
            self.promoteStatus(self.failed,
                    statusMessage=str(e),
                    exceptioncode="NoApplicableCode")

        # lineage in and outputs
        if lineageRequired:
            self.templateProcessor.set("lineage",1)
            self.lineageInputs()
            self.outputDefinitions()

        # if succeeded
        if self.status == self.succeeded:

            # fill outputs
            self.processOutputs()

            # Response document
            self.response = self.templateProcessor.process(self.template)

            # if rawDataOutput is required
            if self.rawDataOutput:
                self.response = None
                self.printRawData()

        # Failed but output lineage anyway
        elif lineageRequired:
            self.response = self.templateProcessor.process(self.template)

        # print status
        if self.storeRequired:
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
                    if respOut.has_key("asreference"):
                        poutput.asReference = respOut["asreference"]

                    # mimetype
                    if respOut.has_key("mimetype"):
                        poutput.format["mimeType"] = respOut["mimetype"]

                    # schema
                    if respOut.has_key("schema"):
                        poutput.format["schema"] = respOut["schema"]

                    # encoding
                    if respOut.has_key("encoding"):
                        poutput.format["encoding"] = respOut["encoding"]

                    # uom
                    if respOut.has_key("uom"):
                        poutput.format["uom"] = respOut["uom"]

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
                raise self.wps.exceptions.NoApplicableCode(
                        "Failed to execute WPS process [%s]: %s" %\
                                (self.process.identifier,processError))
            else:
                # set status to succeeded
                self.promoteStatus(self.succeeded,
                        statusMessage="PyWPS Process %s successfully calculated" %\
                        self.process.identifier)

        except Exception,e:
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
            for profile in self.process.profile:
                profiles.append({"profile":profile})
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
                                   self.status == self.succeeded or
                                   self.status == self.failed):
            self.printResponse(self.statusFiles)


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
                                                wpsInput["asReference"] == True:
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
        complexInput["complexdata"] = input.value
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
            complexOutput["cdata"] = 1
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
        if output.type == "LiteralValue":
            f = open(os.path.join(
                        self.wps.getConfigValue("server","outputPath"),
                                output.identifier+"-"+self.pid),"w")
            f.write(output.value)
            f.close()
            templateOutput["reference"] = self.wps.getConfigValue("server","outputUrl")+\
                    "/"+output.identifier+"-"+str(self.pid)
        else:
            outName = output.value
            outSuffix = outName.split(".")[len(outName.split("."))-1]
            outName = output.identifier+"-"+str(self.pid)+"."+outSuffix
            outFile = self.wps.getConfigValue("server","outputPath")+"/"+outName
            if not self._samefile(output.value,outFile):
                COPY(output.value, outFile)
            templateOutput["reference"] = \
                    self.wps.getConfigValue("server","outputUrl")+"/"+outName
        templateOutput["mimetype"] = output.format["mimeType"]
        templateOutput["schema"] = output.format["encoding"]
        templateOutput["encoding"] = output.format["schema"]

        return templateOutput

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
                    grass.mkMapset()
                elif os.path.exists(os.path.join(self.wps.getConfigValue("grass","gisdbase"),self.process.grassLocation)):
                    grass.mkMapset(self.process.grassLocation)
                else:
                    self.cleanEnv()
                    raise self.wps.exceptions.NoApplicableCode("Location [%s] does not exist" % self.process.grassLocation)
        except Exception,e:
            self.cleanEnv()
            raise self.wps.exceptions.NoApplicableCode("Could not init GRASS: %s" % e)

        return

    def cleanEnv(self):
        """
        Removes temporary created files and dictionaries
        """
        for i in range(len(self.dirsToBeRemoved)):
            dir = self.dirsToBeRemoved[0]
            if os.path.isdir(dir) and dir != "/":
                RMTREE(dir)
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
            f = open(output.value,"r")
            print "Content-type: %s\n" % output.format["mimeType"]
            print f.read()
            f.close()

