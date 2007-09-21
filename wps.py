#!/usr/bin/python 
#-*- coding: utf-8 -*-
"""
This program is simple implementation of OGS's [http://opengeospatial.org]
Web Processing Service (OpenGIS(r) Web Processing Service - OGC 05-007r4)
version 0.4.0 from 2005-09-16

Target of this application is to bring functionality of GIS GRASS
[http://grass.itc.it] to the World Wide Web - it should work like
wrapper for modules of this GIS. Though GRASS was at the first place in the
focuse, it is not necessery to use it's modules - you can use any program
you can script in Python or other language.

This first version was written with support of Deutsche Bundesstiftung
Umwelt, Osnabrueck, Germany on the spring 2006. SVN server is hosted by
GDF-Hannover, Hannover, Germany.

For setting see comments in 'etc' directory and documentation.

This program is free sotware, distributed under the terms of GNU General
Public License as bulished by the Free Software Foundation version 2 of the
License.

Enjoy and happy GISing!
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

pywpscomment = [] # Comment, which should be added to the XML
import pywps
try:
    from pywps.etc import grass as customgrass
except ImportError:
    pywpscomment.append("""Could not load GRASS settings file (pywps/etc/grass.py).
    Please check if the file is created and its permissions.""")

try:
    from pywps.etc import settings as customsettings
except ImportError:
    pywpscomment.append("""Could not load PyWPS settings file (pywps/etc/settings.py).
    Please check if the file is created and its permissions.""")

from pywps import Wps
from pywps import processes
from pywps.Wps import wpsexceptions
from pywps.Wps.wpsexceptions import *
from pywps.Wps import settings 
from pywps.Wps import capabilities
from pywps.Wps import describe
from pywps.Wps import execute
from pywps.Wps import inputs
from pywps.Wps import debug

try:
    from pywps.processes import *
except Exception,e :
    raise ServerError(e)


import string, sys, os, tempfile, glob, shutil, cgi

class WPS:
    def __init__(self):
        """
        WPS Initialization
        """
        # consolidate settings - custom vs. default
        try:
            self.settings = settings.ConsolidateSettings(customsettings)
        except NameError, error:
            self.settings = settings.ConsolidateSettings(None)
        try:
            self.grass = settings.ConsolidateSettings(customgrass,
                    grass=True)
        except NameError, error:
            self.grass = settings.ConsolidateSettings(None,grass=True)

        self.inputs = inputs.Inputs()
        self.method = os.getenv("REQUEST_METHOD")

        self.maxInputLength = 0  # maximal length of one input item
        self.maxFileSize = 0 # maximal input XML or other file size
        self.wpsrequest = None

        self.pidFilePref = "pywps-pidfile-"

        # (re) setting of variables
        try:
            os.setenv("PyWPS_DEBUG",self.serverSettings["debuglevel"])
            if int(self.serverSettings["debuglevel"]) >= 3:
                import cgitb
                cgitb.enable()
        except:
            pass

        if not self.method:
            self.method = "GET"

        #
        # init, get inputs, check them
        #
        self._setMaxInputSize()

        if self.method == "GET":
            self._storeFromGET()
        else:
            self._storeFromPOST()

        self._checkRequest()

        #
        # debug
        #
        debug.PyWPSdebug(self.inputs.values)


    def _setMaxInputSize(self):
        """(re)set maximal length of one input item"""

        if self.method == "GET" or not self.method:
            try:
                self.maxInputLength = int(self.serverSettings["maxInputParamLength"])
            except:
                self.maxInputLength = 0
        else:
            try:
                self.maxFileSize = int(self.serverSettings["maxSize"])
            except:
                self.maxFileSize = 0 
        return

    def _storeFromGET(self):
        """converts input key values to lower case to avoid later
        problems. only for GET method"""

        inputValues = {}
        
        if self.method == "GET" or not self.method:
            form = cgi.FieldStorage()  # the input values (GET method)
            for key in cgi.FieldStorage().keys():
                value = form.getvalue(key)
                # to avoid problems with more then one inputs
                if type(form.getvalue(key)) == type([]):
                    value = value[-1].strip()
                else:
                    value = value.strip()

                if len(value) > self.maxInputLength and self.maxInputLength > 0:
                    raise FileSizeExceeded(key)

                # store input into intputValues structure
                # convert keys to lower case
                inputValues[key.lower()] = value
        # FIXME: should return self.inputValues
        self.inputs.formvalsGet2dict(inputValues) 
        
        return

    def _storeFromPOST(self):
        """converts input key values to lower case to avoid later
        problems. only for GET method"""

        # FIXME: should return self.inputValues
        self.inputs.formvalsPost2dict(sys.stdin,self.maxFileSize)

    def _checkRequest(self):
        """First checking of the request format"""

        # service == "wps"
        if not 'service' in self.inputs.values.keys(): 
            raise MissingParameterValue("service")
        elif self.inputs.values['service'].lower() != 'wps':
            raise InvalidParameterValue('service')

        # request must be set
        if not 'request' in self.inputs.values.keys():
            raise MissingParameterValue("request")
        if not self.inputs.values["request"].lower() in \
                ["getcapabilities" , "describeprocess" , "execute"]:
                raise InvalidParameterValue("request")

        # version == "0.4.0"
        #!!! if not 'version' in self.inputs.values.keys() and \
        #!!!     self.inputs.values['request'].lower() != "getcapabilities":
        #!!!     raise MissingParameterValue("version")

        #!!! elif self.inputs.values['request'].lower() != "getcapabilities" \
        #!!!     and self.inputs.values['version'].lower() != '0.4.0':
        #!!!     raise InvalidParameterValue('version')

        # Controll of all 'identifier' values - if wrongprocess is
        # set, exception, nothing otherwice
        wrongprocess = self.inputs.controllProcesses(processes.__all__,self.inputs.values)
        if wrongprocess:
            if wrongprocess != "identifier":
                raise InvalidParameterValue(wrongprocess)
            else:
                raise MissingParameterValue(wrongprocess)
            return

    def PerformRequest(self):
        """Performs the request according to Request type. Resulting XML
        will be printed"""

        if self.GetRequestType() == "getcapabilities":
            self.GetCapabilities()
        elif self.GetRequestType() == "describeprocess":
            self.DescribeProcess()
        elif self.GetRequestType() == "execute":
            self.Execute()

    def GetRequestType(self):
        """Returns request type converted to lower case"""
        
        return self.inputs.values["request"].lower()

    def GetCapabilities(self,printres=True):
        """Perform GetCapabilities request
        Inputs: printres    - print resulting xml
        """

        self.wpsrequest =  capabilities.Capabilities(self.settings,processes)
        if printres:
            wps.PrintXmlDocument()

    def DescribeProcess(self,printres=True):
        """Perform DescribeProcess request
        Inputs: printres    - print resulting xml
        """

        self.wpsrequest = describe.Describe(self.settings,processes,self.inputs.values)
        if printres:
            wps.PrintXmlDocument()

    def Execute(self,printres=True):
        """Perform Execute request
        Inputs: printres    - print resulting xml
        """


        # 
        # PID file(s) management
        #

        # Create PID file, temp directory etc.
        # check for number of running operations
        try:
            nPIDFiles = len(glob.glob(
                os.path.join(self.settings.ServerSettings['tempPath'],self.pidFilePref+"*")))
        except (IOError, OSError), what:
            raise ServerError("IOError,OSError: %s" % what)

        try:
            maxPIDFiles = self.settings.ServerSettings['maxOperations']
        except KeyError:
            maxPIDFiles = 1

        # too many processes ?
        if nPIDFiles >=  maxPIDFiles:
            raise ServerBusy()
        else:
            PIDFile = tempfile.mkstemp(prefix=self.pidFilePref)
            pass

        #
        # Executing process
        #
        try:
            process = eval("processes.%s.Process()" % (self.inputs.values['identifier'][0]))
            # all grass directories existing?
            settings.GRASSSettings(process)
            # execute
            self.wpsrequest = execute.Execute(self.settings,self.grass.grassenv,
                                              process,self.inputs.values,
                                              self.method)
        except Exception,e :
            os.remove(PIDFile[1])
            raise ServerError(e)

        # 
        # Asynchron management
        #

        # running asynchronously, print to file
        if not self.wpsrequest.pid:
            file = open(os.path.join(
                    self.settings.ServerSettings['outputPath'],
                    self.wpsrequest.executeresponseXmlName),"w")
            sys.stdout = file
        else:
            sys.stdout = sys.__stdout__

        #----------------------
        if printres:
            self.PrintXmlDocument()
        #----------------------

        # clean the PID file        
        if not (self.wpsrequest.status.lower() == "processaccepted" or \
                self.wpsrequest.status.lower() == "processstarted"):
                os.remove(PIDFile[1])


        # only, if this is child process:
        if not self.wpsrequest.pid:
            file.close()


    def PrintXmlDocument(self):
        if self.wpsrequest.document: #FIXME: document should be returned directly
            global pywpscomment
            for com in pywpscomment:
                pywpscommentNode = self.wpsrequest.document.createComment(com)
                self.wpsrequest.document.importNode(pywpscommentNode, 0)
            if sys.stdout == sys.__stdout__:
                print "Content-type: text/xml\n"
            print self.wpsrequest.document.toxml(encoding=self.settings.WPS["encoding"])
        return
        
if __name__ == "__main__":
    """
    This main function controlls input variables and calls either
    GetCapabilities, DescribeProcess or Execute functions.

    If Execute request is called, the temporary directory will be created
    and everything should happen in this directory.
    """
    # import pycallgraph
    # pycallgraph.start_trace()
    wps = WPS()
    wps.PerformRequest()
    # pycallgraph.make_dot_graph('graf-execute.png')
