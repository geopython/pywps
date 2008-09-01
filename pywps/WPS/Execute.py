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
import time,os,sys,tempfile,re
from shutil import copyfile as COPY
from shutil import rmtree as RMTREE

class Execute(Response):
    """
    This class performes the Execute request of WPS specification

    In the class, fork of the  processes has to be done, if the client
    requested asynchronous request performance (status=true)
    """

    statusPrinted = 0

    # status variants
    accepted = "processaccepted"
    started = "processstarted"
    succeeded = "processsucceeded"
    paused = "processpaused"
    failed = "processfailed"

    # runnig process id
    pid = None

    # session ID
    id = ''

    # status location and file
    statusLocation = ''
    statusFileName = None
    statusFiles = [sys.stdout]
    
    # process status
    statusRequired = False # should the request run assynchronously?
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

    parentProcess = False # Fork
    printStatus = False

    rawDataOutput = None


    def __init__(self,wps):
        """
        wps   - parent WPS instance
        """

        Response.__init__(self,wps)

        self.wps = wps
        self.process = None
        self.template = self.templateManager.prepare(self.templateFile)

        # initialization
        self.statusTime = time.time()
        self.pid = os.getpid()
        self.status = None
        self.id = self.makeSessionId()
        self.statusFileName = os.path.join(self.wps.getConfigValue("server","outputPath"),self.id+".xml")
        self.statusLocation = self.wps.getConfigValue("server","outputUrl")+"/"+self.id+".xml"

        # rawDataOutput
        if self.wps.inputs["responseform"]["rawdataoutput"]:
            self.rawDataOutput = self.wps.inputs["responseform"]["rawdataoutput"].keys()[0]

        # is status required
        self.statusRequired = False
        if  self.wps.inputs["responseform"]["responsedocument"].has_key("status"):
            if self.wps.inputs["responseform"]["responsedocument"]["status"]:
                self.statusRequired = True
                
        # is store response required ?
        if  self.wps.inputs["responseform"]["responsedocument"].has_key("storeexecuteresponse"):
            if self.wps.inputs["responseform"]["responsedocument"]["storeexecuteresponse"]:
                self.statusFiles.append(open(self.statusFileName,"w"))

        # setInput values
        self.initProcess()

        # HEAD
        self.templateProcessor.set("encoding",
                                    self.wps.getConfigValue("wps","encoding"))
        self.templateProcessor.set("lang",
                                    self.wps.getConfigValue("wps","lang"))
        self.templateProcessor.set("version",
                                    self.wps.getConfigValue("wps","version"))
        self.templateProcessor.set("statuslocation",
                                    self.statusLocation)
        self.templateProcessor.set("serviceinstance",
                                    self.serviceInstanceUrl())
        # Description
        self.processDescription()

        # Status == True ?
        if self.statusRequired:
            # Status
            self.promoteStatus(self.accepted,"Process %s accepted" %\
                    self.process.identifier)
            
            self.printStatus = True

            # fork
            self.splitThreads()

        if not self.parentProcess:

            # init environment variable
            self.initEnv()

            # donwload and consolidate data
            self.consolidateInputs()

            # set output data attributes defined in the request
            self.consolidateOutputs()

            self.promoteStatus(self.started,"Process %s started" %\
                    self.process.identifier)

            # Execute
            self.executeProcess()

            # Status
            self.promoteStatus(self.succeeded, 
                    statusMessage="PyWPS Process %s successfully calculated" %\
                    self.process.identifier)

            # lineage in and outputs
            if self.wps.inputs['responseform'].has_key("responsedocument"):
                if self.wps.inputs['responseform']['responsedocument'].has_key('lineage') and \
                    self.wps.inputs['responseform']['responsedocument']['lineage'] == True:
                    self.templateProcessor.set("lineage",1)
                    self.lineageInputs()
                    self.outputDefinitions()

            # fill outputs
            self.processOutputs()

            # Response document
            self.response = self.templateProcessor.process(self.template)

            if self.rawDataOutput:
                self.response = None
                self.printRawData()

            # everything worked, remove all temporary files
            self.cleanEnv()

            if (self.statusRequired):
                self.printResponse(self.statusFiles)
        return

    def initProcess(self):
        """
        Setting and controling input values, set by the client. Also the
        processes from PYWPS_PROCESS directory or default directory is
        imported.
        """

        # import the right package
        if self.wps.inputs["identifier"] in self.processes.__all__:
            try:
                module = __import__(self.processes.__name__,
                                        fromlist=[str(self.wps.inputs["identifier"])])
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


        # set propper method for status change
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

            # maximum input file size mut not be grater, then the one,
            # defined in the global config file
            if input.type == "ComplexValue":
                if not input.maxFileSize or input.maxFileSize > maxFileSize:
                    input.maxFileSize = maxFileSize

            try:
                input.setValue(self.wps.inputs["datainputs"][unicode(identifier)])
            except KeyError,e:
                pass

        # make sure, all inputs do have values
        for identifier in self.process.inputs:
            input = self.process.inputs[identifier]

            if not input.value:
                self.cleanEnv()
                raise self.wps.exceptions.MissingParameterValue(identifier)

    def consolidateOutputs(self):
        """Set desired attributes (e.g. asReference) for each output"""
        if self.wps.inputs["responseform"]["responsedocument"].has_key("outputs"):
            respOutputs = self.wps.inputs["responseform"]["responsedocument"]["outputs"]
            for identifier in self.process.outputs:
                poutput = self.process.outputs[identifier]
                respOut = None
                try:
                    respOut = respOutputs[identifier]
                except:
                    continue

                # asReference
                if respOut.has_key("asReference"):
                    poutput.asReference = respOut["asReference"]

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
        Calls 'execute' method of the process, catches possible exeptions
        and raise error, if needed
        """
        try:
            processError = self.process.execute()
            if processError:
                self.cleanEnv()
                raise self.wps.exceptions.NoApplicableCode(
                        "Failed to execute WPS process [%s]: %s" %\
                                (self.process.identifier,processError))
        except Exception,e:
                self.cleanEnv()
                raise self.wps.exceptions.NoApplicableCode(
                        "Failed to execute WPS process [%s]: %s" %\
                                (self.process.identifier,e))

    def processDescription(self):
        """
        Fills Identifier, Title and Abstract, eventually WSDL and Profile
        parts of the output XML document
        """

        self.templateProcessor.set("title", self.process.title)
        self.templateProcessor.set("abstract", self.process.abstract)
        self.templateProcessor.set("identifier", self.process.identifier)

        #self.templateProcessor.set("profile", self.process.profile)
        #self.templateProcessor.set("wsdl", self.process.wsdl)

    def promoteStatus(self,status,
                    statusMessage=0, percent=0,
                    exceptioncode=0, locator=0,
                    output=None):
        """
        Sets status of currently performed Execute request

        {String} status -  name of the status
        {String} statusMessage - message, which should appear in output xml file
        {Float} percent - percent done message
        {String} exceptioncode - eventualy exception
        {String} locator - where the problem occured
        """

        self.process.status.percentCompleted, self.process.status.value,\
        self.printStatus
        
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
            self.templateProcessor.set("exceptiontext", self.statusMessage)
            self.templateProcessor.set("exceptioncode", self.exceptioncode)

        # update response
        self.response = self.templateProcessor.process(self.template)

        # printStatus
        if self.printStatus and not self.rawDataOutput:
            self.statusPrinted += 1
            self.printResponse(self.statusFiles)


    def lineageInputs(self):
        """
        Called, if lineage request was set. Fills the <DataInputs> part of
        output XML document.
        """
        templateInputs = []
    
        for identifier in self.process.inputs.keys():
            templateInput = {}
            input = self.process.inputs[identifier]
            wpsInput = self.wps.inputs["datainputs"][identifier]

            templateInput["identifier"] = input.identifier
            templateInput["title"] = input.title
            templateInput["abstract"] = input.abstract

            templateInputs.append(templateInput);

            if input.type == "LiteralValue":
                templateInput = self._lineageLiteralInput(input,templateInput)
            elif wpsInput["type"] == "ComplexValue" and \
                                            wpsInput["asReference"] == True:
                templateInput = self._lineageComplexReferenceInput(wpsInput,
                                                            input,templateInput)
            elif input.type == "ComplexValue":
                templateInput = self._lineageComplexInput(input,templateInput)
            elif input.type == "BoundingBoxValue":
                templateInput = self._lineageBBoxInput(input,templateInput)

        self.templateProcessor.set("Inputs",templateInputs)

    def _lineageLiteralInput(self, input, literalInput):
        """
        Fill input of literal data
        """
        literalInput["literaldata"] = input.value
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

        wpsInput - asociative field of self.wps.inputs["datainputs"]
        processInput - self.process.inputs
        """
        complexInput["reference"] = wpsInput["value"]
        complexInput["method"] = wpsInput["method"]
        complexInput["mimeType"] = processInput.format["mimeType"]
        complexInput["encoding"] = processInput.format["encoding"]
        if wpsInput["header"]:
            complexInput["header"] = 1
            complexInput["key"] = wpsInput["header"].keys()[0]
            complexInput["value"] = wpsInput["header"][wpsInput["header"].keys()[0]]
        if wpsInput["body"]:
            complexInput["body"] = wpsInput["body"]
        if wpsInput["bodyreference"]:
            complexInput["bodyReference"] = wpsInput["bodyreference"]

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
            templateOutput["title"] = output.title
            templateOutput["abstract"] = output.abstract
        
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

        return complexOutput

    def processOutputs(self):
        """Fill <ProcessOutputs> part in the ouput XML document
        This method is called if, self.status == ProcessSucceeded
        """

        templateOutputs = []
    
        for identifier in self.process.outputs.keys():
            templateOutput = {}
            output = self.process.outputs[identifier]

            templateOutput["identifier"] = output.identifier
            templateOutput["title"] = output.title
            templateOutput["abstract"] = output.abstract

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

            COPY(output.value, self.wps.getConfigValue("server","outputPath")+"/"+outName)
            templateOutput["reference"] = \
                    self.wps.getConfigValue("server","outputUrl")+"/"+outName
        templateOutput["mimetype"] = output.format["mimeType"]
        templateOutput["schema"] = output.format["encoding"]
        templateOutput["encoding"] = output.format["schema"]

        return templateOutput

    # --------------------------------------------------------------------

    def splitThreads(self):
        """
        Will 'try' to for currently running process. Parent process will
        formulate resulting XML response with ProcessAccepted status, child
        process will turn all sys.stdout and sys.stdin off, so the Web
        Server can break the connection to the client.
        """
        try:
            # this is the parent process
            if os.fork():
                self.parentProcess = True
                return
            # this is the child process
            else:
                self.pid = os.getpid()

                # should the status be printed on each change?
                self.irintStatus = True

                self.parentProcess = False
                self.statusFiles.remove(sys.stdout)
                if len(self.statusFiles) == 0:
                    self.statusFiles = [open(self.statusFileName,"w")]

                self.promoteStatus(self.started,"Process %s started" %\
                    self.process.identifier)

                return
                # time.sleep(2)
                # Reassign stdin, stdout, stderr for child
                # so Apache will ignore it
                si = open(os.devnull, 'r')
                so = open(os.devnull, 'a+')
                se = open(os.devnull, 'a+', 0)
                os.dup2(si.fileno(), sys.stdin.fileno())
                os.dup2(so.fileno(), sys.stdout.fileno())
                os.dup2(se.fileno(), sys.stderr.fileno())
        except OSError, e: 
            raise self.wps.exceptions.NoApplicableCode("Fork failed: %d (%s)\n" % (e.errno, e.strerror) )
        return

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

        serveraddress += "service=WPS&request=GetCapabilities&version="+self.wps.DEFAULT_WPS_VERSION

        serveraddress = serveraddress.replace("&", "&amp;") # Must be done first!
        serveraddress = serveraddress.replace("<", "&lt;")
        serveraddress = serveraddress.replace(">", "&gt;")

        return serveraddress

    def onStatusChanged(self):
        """
        This method is used for redefinition of self.process.status class
        """

        self.promoteStatus(self.process.status.code,statusMessage =
                self.process.status.value,
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

