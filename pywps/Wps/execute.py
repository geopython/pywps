"""
This module generates XML file with Execute response of WPS and executes the process
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
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

from ogc import execute
from xml.dom.minidom import Document
from xml.dom.minidom import parse
import grass
import wpsexceptions
import append

from threading import Thread
import tempfile, shutil, os, urllib,time,sys,re

class Status(Thread):
    """
    Make thread for watching at process.status array
    """
    def __init__ (self,document=None, filename=None,interval=1,process=None):
      Thread.__init__(self)

      self.document = document # xml document
      self.filename = filename # name of input file
      self.interval = interval # interval for checking
      self.process = process   # process

    def run(self):
        """
        Run this in thread
        """
        oldmessage = None
        oldpercent = 0

        while 1:
            try:
                # get new message from the process
                newmessage,newpercent=self.process.status

                # no reason for continuing
                if self.process.stopChecking:
                    break
            except AttributeError,e:
                newmessage=""
                newpercent=0
            except ValueError,e :
                pass

            # generate the xml
            if oldmessage != newmessage or\
                newpercent != oldpercent:

                status = self.document.getElementsByTagName('Status')[0].firstChild
                self.document.getElementsByTagName('Status')[0].removeChild(status)
                status = self.document.getElementsByTagName('Status')[0]
                node = self.document.createElement("ProcessStarted")
                messnode = self.document.createTextNode(newmessage)
                node.setAttribute("message",newmessage)
                node.setAttribute("percentCompleted",str(newpercent))
                node.appendChild(messnode)
                status.appendChild(node)

                file = open(self.filename,"w")
                file.write(self.document.toprettyxml())
                file.close()

                oldmessage = newmessage
                oldpercent = newpercent

            # wait about a second
            time.sleep(self.interval)

class Execute:
    """
    This class includes functions for perforing the Execute operation and
    returning the resulting XML or file or value

    NOTE: If you are here, you should allready have created some writeable
    teporary directory and chdir in it.
    """

    def __init__(self, serverSettings, grassSettings, process, formvalues,):
        """
        Initialization of the Execute request

        Inputs:
            serverSettings  -   file from  etc/settings.py or similar
                                structure
            grassSettings   -   file from /etc/grass.py or similar
                                structure
            process         -   file with process, with settings and
                                "execute" function
            formvalues      -   input comma separated string in form
                                "arg1,value1,arg2,value2,arg3,value3,..."
        """

        self.settings = serverSettings  # etc/settings.py
        self.grassSettings = grassSettings  # etc/grass.py
        self.WPS = execute.WPS()        # ogc/execute.py
        self.ex = self.WPS.e['response'] # just shorcut
        self.process = process          # processes/...
        self.Append = append.Append()   # functions for siple appending
                                        # attributes and nodes
        self.wpsExceptions = wpsexceptions.WPSExceptions() # function for
                                        # printing execptions
        self.dirsToRemove = []          # here appear temporary
                                        # directories, which should be 
                                        # removed e.g.
                                        # [/tmp/tmpgrassSOMETHING,
                                        # /var/grassdata/spear/tmpmapset]
        self.formvalues = formvalues   # comma separated string
        self.timestamp = "%d-%d-%d-%d-%d-%d" % (time.localtime()[0:6])

                                    # the output XML file name - needed, if
                                    # statusSupported == true
        self.executeresponseXmlName = "executeresponse-%s.xml" % (self.timestamp)
        self.statusLocation = None  # URL to executeresponseXmlName file
        self.statusSupported = None   # Default -> everything will be printed
                                    # to STDOUT and what more, no fork is
                                    # needed
 
        self.document = Document()
        self.status = "ProcessAccepted" # default: everything is all right 
        self.statusMessage = None
        self.errorCode = 0
        self.pid = os.getpid()

        # 
        # storing the data in self.process.Inputs[input]['value']
        #
        if not 'datainputs' in self.formvalues.keys():
            print "Content-type: text/xml\n"
            print self.wpsExceptions.make_exception("MissingParameterValue","DataInputs")
            self.document = None
            return
        else:
            if not self.checkInputs(formvalues=self.formvalues):
                return

        #
        # Status Support
        # 
        try:
            # if store && status are supported and set to "true"
            # fork the process
            if self.process.statusSupported == "true" and \
               self.process.storeSupported.lower() == "true" and \
               self.formvalues['status'].lower() == "true" and \
               self.formvalues['store'].lower() == "true":

                # fork process
                # It's way harder than it should be to have a CGI script 
                # do something asynchronously in Apache. The root of the 
                # problem is that it's not enough to fork a child, you 
                # have to close stdin, stdout, and stderr. Only you can't 
                # really close them, you have to reassign them.
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
                        status = Status(document=self.document, 
                                    filename=os.path.join(
                                        self.settings.ServerSettings['outputPath'],
                                        self.executeresponseXmlName),
                                    interval=1,
                                    process=self.process)
                        # take care on self.process.status
                        status.start()

                except OSError, e: 
                    print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
                    sys.exit(1)
        except KeyError,e :
            print >>sys.stderr, "Execute.execute failed with KeyError : (%s)" % (e) 
        except AttributeError,e :
            pass
            print >>sys.stderr, "Execute.execute failed with AttributeError: %s" % (e) 

        #
        # Return just XML response -> statusSupported == "true"
        # or execute the process and return the XML after that
        #
        self.execute()
        return 

    def execute(self):
        """
        1) Creates the temporary directory
        2) If needed, downloads the data
        3) Calls the process
        4) Returns the XML or the resulting file/value
        5) Cleans the temporary directory

        Reason for having this all in separate function is the possible
        fork of the process.
        """
        
        #
        # create the tempdir
        #
        self.tempdir = self.mktempdir()
        if not self.tempdir:
            return
        else:
            self.dirsToRemove.append(self.tempdir)
        
        #
        # make GRASS MAPSET.
        # NOTE: Current dir should be somewhere in /tmp/tmpgrassSOMETHING
        # which is LOCATION_NAME to us
        #
        # Set 
        #     *self.process.grassEnv
        # variables
        grassEnv = grass.GRASS(self.grassSettings)
        try:
            self.mapset = grassEnv.mkmapset(self.process.grassLocation)
            self.dirsToRemove.append(os.path.join(self.process.grassLocation,self.mapset))
            self.process.grassenv=grassEnv.grassenv
        except AttributeError:
            self.mapset = grassEnv.mkmapset()
 
        #
        # downloading the data
        #
        for procInput in self.process.Inputs:
            # only Complex Input Data will try to download
            if "ComplexValueReference" in procInput.keys() or \
               "ComplexValue" in procInput.keys(): 


                valtype = 'ComplexValueReference'
                if "ComplexValue" in procInput.keys():
                    valtype = "ComplexValue"

                # download
                newFileName = \
                    self.get_data(data=self.formvalues['datainputs'][procInput['Identifier']],
                                  output=procInput['Identifier'],
                                  type=valtype)
                if not newFileName:
                    self.cleanTempDir()
                    return
                else:
                    procInput['value'] = newFileName # replace the
                    self.process.DataInputs[procInput['Identifier']] = procInput['value']
        #######
        # MAKE
        if sys.stdout == sys.__stdout__:
            sys.stdout = sys.__stderr__
        # None == Everything OK. String == Problem
        try:
            error = self.process.execute()
            if sys.stdout == sys.__stderr__:
                sys.stdout = sys.__stdout__

            if error:
                self.errorCode = 1
                raise StandardError, error

            else:
                self.status = "ProcessSucceeded"
            self.process.stopChecking = True
            # just to be shure, go back to grass mapset
            os.system("""g.mapset mapset=%s >/dev/null 2>&1""" %\
                    (grassEnv.grassenv['MAPSET']))

        except Exception,e:
            sys.stderr.write("PyWPS ERROR: %s in self.process.execute()\n" % (e))
            if sys.stdout == sys.__stderr__:
                sys.stdout = sys.__stdout__
            self.status = "ProcessFailed"
            self.statusMessage = e
            self.make_response_xml()
            # just to be shure, go back to grass mapset
            os.system("""g.mapset mapset=%s >/dev/null 2>&1""" %\
                    (grassEnv.grassenv['MAPSET']))
            self.cleanTempDir()
            return

        # is there stored map?
        outputMap = False
        for procOutput in self.process.Outputs:
            try:
                if type(procOutput['value']) == type(None) or \
                    procOutput['value'] == []:
                     try:
                        procOutput['value'] = self.process.DataOutputs[procOutput['Identifier']]
                     except:
                         raise KeyError, "Output value not set"
            except KeyError,e:
                    procOutput['value'] = e
                
            if 'ComplexValueReference' in procOutput.keys():
                    outputMap = True

        # for each process output
        for procOutput in self.process.Outputs:
            # store support requested?
            if 'store' in self.formvalues.keys() and\
                self.formvalues['store'].lower() == "true":  
                # store support setted in the conf. file
                if 'ComplexValueReference' in procOutput.keys():

                        try:
                            # move output files to prepared directory
                            try:
                                (name,appendix) = procOutput['value'].split(".")
                            except ValueError:
                                name = procOutput['value']
                                appendix="out"
                            procOutput['filename'] =  name+"-"+self.timestamp+"."+appendix
                            procOutput['filePath'] = os.path.join(
                                    self.settings.ServerSettings['outputPath'], 
                                    procOutput['filename']) 
                            shutil.move(procOutput['value'], 
                                    procOutput['filePath'])
                            # replace the output value: file.tif ->
                            # http://server/file.tif
                            procOutput['value'] = os.path.join(
                                    self.settings.ServerSettings['outputUrl'],
                                    procOutput['filename'])

                        except IOError, what:
                            print "Content-type: text/xml\n"
                            print self.wpsExceptions.make_exception(
                                    "ServerError","IOError: %s" % what)
                            self.document = None
                            self.cleanTempDir()
                            return

            else:
                # content type
                try:
                    outtype = None
                    if procOutput.has_key("ComplexValue"):
                        outtype="ComplexValue"
                    elif procOutput.has_key("ComplexValueReference"):
                        outtype="ComplexValueReference"
                    elif procOutput.has_key("LiteralValue"):
                        outtype="LiteralValue"
                    elif procOutput.has_key("BoundingBoxValue"):
                        outtype="BoundingBoxValue"

                    if outtype:
                        conttype = procOutput[outtype]['Formats'][0]
                    else:
                        raise KeyError
                except KeyError:
                    conttype = "text/plain"

                self.data_response(procOutput,conttype=conttype)
                self.document = None
                self.cleanTempDir()
                # only first output
                return

        self.make_response_xml()
        # clean temp Dir
        self.cleanTempDir()
        return
        
    def data_response(self,output,where="stdout",conttype="text/plain"):
        """ This function sends outputValue to STDOUT -> to the browser

        outputType - one of "ComplexOutput", "LiteralOutput",
        outputValue - name of the file/variable
        conttype    - Content-type, default text/plain
        """

        # return to stdout
        if where=="stdout":
            print "Content-type: %s\n" % (conttype)

            if "ComplexValue" in output.keys() or \
               "ComplexValueReference" in output.keys():
                outputh = open(output['value'],"r")
                for line in outputh:
                    print line,
                outputh.close()

            elif "LiteralValue" in output.keys():
                print output['value'],

            elif "BoundingBoxValue" in output.keys():
                if output['value'][0] >  output['value'][2]:
                    output['value'][0],  output['value'][1], output['value'][2],  output['value'][3] =\
                            output['value'][2],  output['value'][3], output['value'][0],  output['value'][1] 
                print output['value'][0],output['value'][1],output['value'][2],output['value'][3],

            self.document = None
            return

        # return as text variable
        else:
            if conttype=="text/plain":
                outputh = open(output['value'],"r")
                str=""
                for line in outputh.readlines():
                    str += line
                outputh.close()
                # if file[0].find("xml") > -1:
                #     file = file[1:]
                return str
            elif conttype=="text/xml":
                out= parse(output['value'])
                return out.firstChild

    def make_response_xml(self):
        """
        This function generates responding XML file.
        """

        #
        # cleaning the document
        # 
        self.document = Document()

        #
        # Create the root node in XML document
        #
        self.Execute = self.document.createElementNS(self.WPS.namespaces['ows'],"ExecuteResponse")
        self.Execute.setAttribute("xmlns",self.WPS.namespaces['wps'])
        self.Execute.setAttribute("xmlns:ows",self.WPS.namespaces['ows'])
        self.Execute.setAttribute("xmlns:xlink",self.WPS.namespaces['xlink'])
        self.Execute.setAttribute("xmlns:xsi",self.WPS.namespaces['xsi'])
        self.Execute.setAttribute("xsi:schemaLocation",self.WPS.namespaces['wps']+' '+self.WPS.schemalocation['wps'])
        if self.statusLocation:
            self.Execute.setAttribute("statusLocation",self.statusLocation)
        self.document.appendChild(self.Execute)

        


        # attributes
        try:
            for attribute in self.ex['attributes'].keys():
                if attribute == "statusLocation":
                    continue
                self.Append.Attribute(
                        document=self.document,
                        attributeName = attribute,
                        Node = self.Execute,
                        Attributes = self.ex['attributes'],
                        Values = self.settings.WPS
                        )
        except AttributeError, what:
            pass
        
        # For each element separate function
        for element in self.ex['order']:
            if element == 'Identifier':
                identifier = self.document.createElement(
                        self.ex['elements']['Identifier']['ns']+"Identifier")
                identifier.appendChild(
                        self.document.createTextNode(self.process.Identifier))
                self.Execute.appendChild(identifier)
            elif element == 'Status':
                self.statusNode(self.Execute)
            elif element == "DataInputs":
                # this structure is ommited
                pass
            elif element == "OutputDefinitions":
                # this structure is ommited
                pass
            elif element == "ProcessOutputs":
                if self.status == "ProcessSucceeded":
                    self.process_outputsNode(self.Execute)
        return

    def statusNode(self,parent):
        """
        Status XML Node

        Inputs:
            parent   -  parent XML node
        """
        Status = self.ex['elements']['Status']
        statusNode = self.document.createElement("%s%s" % \
                (Status['ns'],"Status"))

        if self.statusMessage:
            message = self.statusMessage
        else:
            message = ''

        node = self.document.createElement("%s%s" % \
                (Status['elements'][self.status]['ns'],self.status))
        if self.status == "ProcessStarted":
            node.setAttribute("%s%s" % \
                    (Status['elements'][self.status]['attributes']['message']['ns'],"message"),
                    message )
        elif self.status.lower() == "processfailed":
            # Exceptions, ProcessFailed
            # NOTE: Should be separate function
                
            report = self.document.createElement("ows:ExceptionReport")
            report.setAttribute("verion","1.0")
            node.appendChild(report)

            # code: known errors do have code  1, unkown 0
            exception = self.document.createElement("ows:Exception")
            exception.setAttribute("exceptionCode", str(self.errorCode))
            report.appendChild(exception)

            text = self.document.createElement("ows:ExceptionText")
            text.appendChild(self.document.createTextNode(str(message)))
            exception.appendChild(text)

        statusNode.appendChild(node)
        parent.appendChild(statusNode)
        return

    def process_outputsNode(self,parent):
        """
        ProcessOutputs XML Node
        """
        outputOws = self.ex['elements']['ProcessOutputs']['elements']['Output']

        processOutputs = self.document.createElement("ProcessOutputs")
        parent.appendChild(processOutputs)

        # for each element in output structure
        for outputProc in self.process.Outputs:
            outputNode = self.document.createElement("Output") 
            processOutputs.appendChild(outputNode)

            # for each node in input ogc's conf. structure
            for element in outputOws['order']:
                if element == "ValueFormChoice":

                    #
                    # ComplexValueReference
                    if "ComplexValueReference" in outputProc.keys():
                        ComplexValueRef = self.document.createElement("ComplexValueReference")
                        outputNode.appendChild(ComplexValueRef)
                        for attribute in outputOws['elements']['ValueFormChoice']['elements']['ComplexValueReference']['attributes']:
                            if attribute == "format":
                                ComplexValueRef.setAttribute("format",outputProc['ComplexValueReference']['Formats'][0])
                            elif attribute == "reference":
                                ComplexValueRef.setAttribute(
                                        "ows:reference",outputProc['value'])
                            else:
                                    self.Append.Attribute(
                                        document=self.document,
                                        attributeName = attribute,
                                        Node = ComplexValueRef,
                                        Attributes =\
                                        outputOws['elements']['ValueFormChoice']['elements']['ComplexValueReference']['attributes'],
                                        Values = outputProc
                                        )
                    #
                    # ComplexValue
                    elif "ComplexValue" in outputProc.keys():
                        ComplexValue = self.document.createElement("ComplexValue")
                        outputNode.appendChild(ComplexValue)
                        format = outputProc['ComplexValue']['Formats'][0] 
                        for attribute in outputOws['elements']['ValueFormChoice']['elements']['ComplexValue']['attributes']:

                            if attribute == "format":
                                ComplexValue.setAttribute("format",format)
                        for elm in outputOws['elements']['ValueFormChoice']['elements']['ComplexValue']['elements']:
                            if elm == "Value":
                                node = self.document.createElement("Value")

                                # if format of this element is text/xml or
                                # similar, append xml, append text/plain
                                # otherwise
                                if format == "text/xml":
                                    out =  self.data_response(
                                            outputProc,where="file",
                                            conttype="text/xml")
                                else:
                                    out = self.document.createTextNode(
                                    self.data_response(outputProc,where="file")
                                    #"XML or Binary result should be here"
                                            )
                                node.appendChild(out)
                                ComplexValue.appendChild(node)

                    #
                    # LiteralValue 
                    # LiteralData is depredecated
                    elif "LiteralData" in outputProc.keys() or\
                         "LiteralValue" in outputProc.keys():
                        LiteralValue = self.document.createElement("LiteralValue")
                        outputNode.appendChild(LiteralValue)
                        #LiteralValue.setAttribute("value",
                        #str(outputProc['value']))
                        LiteralValue.appendChild(
                                self.document.createTextNode(str(outputProc['value'])))

                    #
                    # BoundBox
                    elif "BoundingBoxValue" in outputProc.keys():
                        bboxNode = self.document.createElement("%s%s" %\
                                (outputOws['elements']['ValueFormChoice']['elements']['BoundingBoxValue']['ns'],"BoundingBoxValue"))
                        outputNode.appendChild(bboxNode)

                        lower = self.document.createElement("%s%s" % \
                                (outputOws['elements']['ValueFormChoice']['elements']['BoundingBoxValue']['elements']['LowerCorner']['ns'],"LowerCorner"))

                        upper = self.document.createElement("%s%s" % \
                                (outputOws['elements']['ValueFormChoice']['elements']['BoundingBoxValue']['elements']['UpperCorner']['ns'],"UpperCorner"))

                        try:
                            if outputProc['value'][0] >  outputProc['value'][2]:
                                outputProc['value'][0],  outputProc['value'][1], outputProc['value'][2],  outputProc['value'][3] =\
                                        outputProc['value'][2],  outputProc['value'][3], outputProc['value'][0],  outputProc['value'][1] 
                            lower.appendChild(self.document.createTextNode(
                                "%s %s" %
                                (str(outputProc['value'][0]).strip(),str(outputProc['value'][1]).strip())))
                            upper.appendChild(self.document.createTextNode(
                                "%s %s" %
                                (str(outputProc['value'][2]).strip(),str(outputProc['value'][3]).strip())))

                        except IndexError,e:
                            lower = upper = "%s: not enough output values for bounding box"
                        bboxNode.appendChild(lower)
                        bboxNode.appendChild(upper)


                        pass
                else: # try to append 'standard' node
                    self.Append.Node(
                        document=self.document, 
                        childNode=element, 
                        parentNode=outputNode,
                        Elements=outputOws['elements'],
                        Values=outputProc
                        )
        return

    def get_data(self,
                 data=None,
                 postFile=None,
                 maxSize=5242880,
                 output="input.file",
                 type="ComplexValue"):
        """
        Tryes to download the data from net and check's, if they are in 
        appropriate format.

        data - URI, from which the file should be downloaded, or e.g. GML
                string
        postFile - file name which arriwed trough the POST method
        """
        try:
            maxSize = self.settings.ServerSettings['maxSize']
        except KeyError:
            pass

        # check, if the file with this name already exist.
        # if so, try to find "filename.fileN" name, where N 
        # standes for integer bumber
        inputNumber = 1
        while inputNumber:
            if os.path.isfile(output):
                output = "%s-%d" %(output,inputNumber)
                inputNumber +=1
            else:
                break


        if type=="ComplexValueReference":
            if data:
                inputUrl = urllib.urlopen(data)
                
                try:
                    fout=open(output,'wb')
                except IOError, what:
                    print "Content-type: text/xml\n"
                    print self.wpsExceptions.make_exception(
                        "ServerError","IOError: %s" % what)
                    self.document = None
                    return

                # ok, get the file!
                size = 0
                while 1:
                    # reading after 100kB
                    size += 100000
                    chunk = inputUrl.read(100000)

                    # something is wrong
                    if re.search("not found",chunk,re.IGNORECASE):
                        print "Content-type: text/xml\n"
                        print self.wpsExceptions.make_exception(
                                "InvalidParameterValue",
                                "server says: %s not found" % (data))
                        self.document = None
                        return

                    # everything is here, break
                    if not chunk: 
                        break
                    fout.write (chunk)

                    # TOO BIG! STOP THIS
                    if size > maxSize: 
                        print "Content-type: text/xml\n"
                        print self.wpsExceptions.make_exception("FileSizeExceeded")
                        self.document = None
                        return
                fout.close()
        elif type=="ComplexValue":
            try:
                fout=open(output,'w')
                fout.write(data)
                fout.close()
            except IOError, what:
                print "Content-type: text/xml\n"
                print self.wpsExceptions.make_exception(
                    "ServerError","IOError: %s" % what)
                self.document = None
                return

        if not os.path.isfile(output):
            print "Content-type: text/xml\n"
            print self.wpsExceptions.make_exception("InvalidParameterValue","DataInputs")
            self.document = None
            return
        else:
            return output

    def cleanTempDir(self,directory=None):
        """
        Cleans temporary directory - removes the complet tree.
        if directory not set, it will go thru self.dirsToRemove variable
        """
        if directory:
            if os.path.isdir(directory):
                shutil.rmtree(directory)
            else:
                raise TypeError
            return 
        else:
            for dir in self.dirsToRemove:
                shutil.rmtree(dir)
    
    def mktempdir(self,directory=None):
        """
        Creates temporary directory and  chdir to it

        returns name of the temp directory, if OK
        nothing if failed

        inputs:
            directory   -   if set, the tmpgrassSOMETHING dir will be created in this directory
                            if not set, will try to look to settitings.ServerSettings['tempPath']
                            if not set, will try to create in default directory (/tmp)
        """
        # create our temp directory where the admin wants to
        # in /tmp else
        try:
            if directory:
                    tempdir = tempfile.mkdtemp(prefix="tmpgrass",dir=directory)
            else:
                try:
                    tempdir = tempfile.mkdtemp(prefix="tmpgrass",dir=self.settings.ServerSettings['tempPath'])
                except KeyError:
                    tempdir = tempfile.mkdtemp()
        except (IOError,OSError), what:
            print "Content-type: text/xml\n"
            print self.wpsExceptions.make_exception(
                    "ServerError","IOError, OSError: tempdir not created - %s" % what)
            self.document = None
            return
        #########
        # everything will be done in our temp directory
        os.chdir(tempdir)
        return (tempdir)

    def checkInputs(self,formvalues=None):
        """
        Check the process input values sended in the 'formvalues' string. 
        The string represents comma separated values: key1,value1,key2,value2

        If everything looks good, new DataInputs structure is returned.
        """
        
        # new variable for each process for easy access of input values
        #     *self.process.DataInputs
        #     *self.process.DataOutputs
        self.process.DataInputs = {}
        self.process.DataOutputs = {}

        if not formvalues:
            return
        #
        # All the parameters are here?
        #
        for input in self.process.Inputs:
            try:
                if not formvalues['datainputs'][input['Identifier']]:
                        raise KeyError
            except (KeyError),e :
                if not input.has_key('value') or input['value'] == None:
                    print "Content-type: text/xml\n"
                    print self.wpsExceptions.make_exception( \
                            "MissingParameterValue",input['Identifier'])
                    self.document = None
                    return
        #
        # Type and value checking
        #   
        for input in self.process.Inputs:
            
            # it can happen, that dataType is not set but default value is
            # -> get the dataType from default value

            if (input.has_key('value') and not input.has_key('dataType')):
                input['dataType'] = type(input['value'])
                    
            # set "value"
            if formvalues['datainputs'].has_key(input['Identifier']):

                input['value'] = formvalues['datainputs'][input['Identifier']]

                if self._checkType(input,formvalues['datainputs'][input['Identifier']]):
                    print "Content-type: text/xml\n"
                    print self.wpsExceptions.make_exception(
                            "InvalidParameterValue","%s: %s" % \
                                    (str(input['Identifier']), 
                                    str(formvalues['datainputs'][input['Identifier']])))
                    self.document = None
                    return

                if input.has_key('LiteralValue') and \
                    len(input['value']) == 1:
                        input['value'] = input['value'][0]
                elif input.has_key("BoundingBoxValue"):
                    if input['value'][0] > input['value'][2]:
                        input['value'][0], input['value'][2] = input['value'][2],input['value'][0]
                        input['value'][1], input['value'][3] = input['value'][3],input['value'][1]

            # setting input values to one structure - pointer to input['value']
            self.process.DataInputs[input['Identifier']] = input['value']

        return True

    #
    # Type and value checking
    #   
    def _checkType(self,input=None,values=None):
        """This function checkes type and value of input values"""
         
        if not type(values) == type([]):
            values = [values]

        for value in values:
            try:
                if input['dataType'] == type(0.0):
                    value = float(value)
                elif input['dataType'] == type(1):
                    value =  int(value)
                elif input['dataType'] == type(''):
                    value = str(value)
            except (KeyError),e:
                pass
            except TypeError,e:
                return True

            # list of allowed literal values in
            if input.has_key("LiteralValue"):
                isin = False
                if not input['LiteralValue'].has_key('values') or\
                        "*" in input['LiteralValue']['values']:
                    isin = True
                else:
                    if value in input['LiteralValue']['values']:
                        isin = True
                if not isin:
                    return True

            return
