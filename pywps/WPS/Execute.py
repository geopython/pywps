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
import time,os,tempfile,re
from pywps import Grass

class Execute(Request):
    """
    """
    accepted = "processaccepted"
    started = "processstarted"
    succeeded = "processsucceeded"
    paused = "processpaused"
    failed = "processfailed"

    id = ''
    statusLocation = ''
    statusFile = None
    
    status = 0
    processstatus = 0
    percent = 0
    exceptioncode = 0
    locator = 0

    percent = 0
    processstatus = 0

    dirsToBeRemoved = []     # directories, which should be removed

    workingDir = ""
    grass = None

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
        self.id = self.makeSessionId()
        self.statusLocation = os.path.join(self.wps.getConfigValue("server","outputPath"),self.id+".xml")

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
        self.templateProcessor.set("statuslocation",
                                    self.statusLocation)
        self.templateProcessor.set("serviceinstance",
                                    self.serviceInstanceUrl())
        #
        # Description
        #
        self.processDescription()


        #
        # Status
        #
        self.setStatus(self.accepted)

        #
        # lineage
        #
        if self.wps.inputs['responseform'].has_key("responsedocument"):
            if self.wps.inputs['responseform']['responsedocument'].has_key('lineage') and \
                self.wps.inputs['responseform']['responsedocument']['lineage'] == True:
                self.lineageInputs()

        # FIXME here we are
        self.response = self.templateProcessor.process(self.template)

        # 
        # Execute
        #
        #
        # Description
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

        # 
        # Execute
        #
        if self.wps.inputs["responseform"]["responsedocument"]["status"]:
            pass
            #self.splitThreads()
        self.executeProcess()

        return

    def initProcess(self):

        # import the right package
        if self.wps.inputs["identifier"] in self.processes.__all__:
            try:
                module = __import__(self.processes.__name__,
                                        fromlist=[str(self.wps.inputs["identifier"])])
                self.process = eval("module."+self.wps.inputs["identifier"]+".Process()")

            except Exception, e:
                raise self.wps.exceptions.NoApplicableCode(
                "Could not import process [%s]: %s" %\
                        (self.wps.inputs["identifier"], e))
                return
        else:
            raise self.wps.exceptions.InvalidParameterValue(
                    self.wps.inputs["identifier"])

        # create temporary directory
        self.initEnv()

        # calculate maximum allowed input size
        maxFileSize = self.calculateMaxInputSize()

        # set input values
        for identifier in self.process.inputs:
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
                raise self.wps.exceptions.MissingParameterValue(identifier)

        # set propper method for status change
        self.process.wps = self.wps
        self.process.status.onStatusChanged = self.onStatusChanged
        self.process.debug = self.wps.getConfigValue("server","debug")

    def onInputProblem(self,what,why):
        
        exception = None
        if what == "FileSizeExceeded":
            exception = self.wps.exceptions.FileSizeExceeded
        elif what == "NoApplicableCode":
            exception = self.wps.exceptions.NoApplicableCode

        raise exception(why)


    def executeProcess(self):
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

        self.templateProcessor.set("title", self.process.title)
        self.templateProcessor.set("abstract", self.process.abstract)
        self.templateProcessor.set("identifier", self.process.identifier)

        #self.templateProcessor.set("profile", self.process.profile)
        #self.templateProcessor.set("wsdl", self.process.wsdl)

    def setStatus(self,status,
                    processstatus=0, percent=0,
                    exceptioncode=0, locator=0):
        
        self.statusTime = time.time()
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

    
    def splitThreads(self):
        try:
            self.statusLocation = self.settings.ServerSettings['outputUrl']+"/"+self.executeresponseXmlName
            self.pid = os.fork() 
            if self.pid:
                self.make_response_xml()
                file = open(
                        os.path.join(self.settings.ServerSettings['outputPath'],self.executeresponseXmlName),"w")
                file.write(self.document.toprettyxml())
                file.close()
                return
            else:
                # Reassign stdin, stdout, stderr for child
                # so Apache will ignore it
                # time.sleep(2)
                self.status = "ProcessStarted"
                si = open('/dev/null', 'r')
                so = open('/dev/null', 'a+')
                se = open('/dev/null', 'a+', 0)
                os.dup2(si.fileno(), sys.stdin.fileno())
                os.dup2(so.fileno(), sys.stdout.fileno())
                os.dup2(se.fileno(), sys.stderr.fileno())

                # make document
                self.make_response_xml()

                # begin checking
                self.process.stopChecking = False

                # define thread
                status = Status(self,document=self.document, 
                            filename=os.path.join(
                                self.settings.ServerSettings['outputPath'],
                                self.executeresponseXmlName),
                            interval=1,
                            process=self.process)
                # take care on self.process.status
                status.start()

        except OSError, e: 
            sys.stderr.write( "fork #1 failed: %d (%s)\n" % (e.errno, e.strerror) )
            sys.exit(1)

    def makeSessionId(self):
        return "pywps-"+str(int(time.time()*100))

    def getSessionIdFromStatusLocation(self,statusLocation):
        begin = statusLocation.find("/pywps-")
        end = statusLocation.find(".xml")
        if begin > -1 and end > -1:
            return statusLocation[begin:end]
        else:
            return None

    def serviceInstanceUrl(self):
        serveraddress = self.wps.getConfigValue("wps","serveraddress")

        if not serveraddress.endswith("?") and \
           not serveraddress.endswith("&"):
            if serveraddress.find("?") > -1:
                serveraddress += "&"
            else:
                serveraddress += "?"

        return serveraddress + "service=WPS&request=GetCapabilities&version="+self.wps.DEFAULT_WPS_VERSION

    def onStatusChanged(self):
        pass
        print self.process.status

    def initEnv(self):

        self.workingDir = tempfile.mkdtemp(prefix="pywps",
                                dir=self.wps.getConfigValue("server","tempPath"))

        self.workingDir = os.path.join(
                self.wps.getConfigValue("server","tempPath"),self.workingDir)

        os.chdir(self.workingDir)
        self.dirsToBeRemoved.append(self.workingDir)

        if self.process.grassLocation:
            grass = Grass.Grass(self)
            if self.process.grassLocation == True:
                grass.mkMapset()
            elif os.path.exists(self.process.grassLocation):
                grass.mkMapset(self.process.grassLocation)
            else:
                raise self.wps.exceptions.NoApplicableCode("Location [%s] does not exist" % self.process.location)
        
    def cleanEnv(self):
       
        from shutil import rmtree
        for dir in self.dirsToBeRemoved:
            if os.path.isdir(dir) and dir != "/":
                #rmtree(dir)
                pass

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
