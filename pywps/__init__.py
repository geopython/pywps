"""
PyWPS
=====
This package contains classes necessary for input parsing OGC WPS requests,
working with list of processes, executing them and redirecting OGC WPS
responses back to client.

The outputs are generated using python's htmltmpl template system.

.. moduleauthor:: Jachym Cepicky <jachym bnhelp cz>
"""

__all__ = [ "Parser","processes", "Process", "Exceptions", "Wps", "Templates"]


# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# License:
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

import pywps
import Parser
import Exceptions
import Wps
from Exceptions import *

import sys, os, ConfigParser, urllib, re, traceback
from sys import stdout as STDOUT
from sys import stderr as STDERR

# global variables
METHOD_GET="GET"
METHOD_POST="POST"
OWS_NAMESPACE = "http://www.opengis.net/ows/1.1"
WPS_NAMESPACE = "http://www.opengis.net/wps/1.0.0"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
EMPTYPARAMREGEX = re.compile('( \w+="")|( \w+="None")')


class Pywps:
    """This is main PyWPS Class, which parses the request, performs the
    desired operation and writes required response back.
    """

    method  =""                      # HTTP POST or GET
    parser = None
    config = None  # Configuration
    workingDir = None # this working directory

    exceptions = pywps.Exceptions
    statusFiles = STDOUT
    stdOutClosed = False

    inputs = {} # parsed input values
    request = None # object with getcapabilities/describeprocess/execute
                   # class
    parser = None # pywps.Parser Get or Post

    defaultLanguage = "eng"
    languages = [defaultLanguage]
    defaultVersion = "1.0.0"
    versions=[defaultVersion]
    logFile = STDERR

    def __init__(self, method=METHOD_GET, configFiles=None):
        """Class constructor

        :param method: Used HTTP method, which is either ref:METHOD_POST:
        or :ref:`METHOD_GET`:
        :type method: string
        :param configFiles: List of configuration files. Ignore, if you want to use standard files location
        :type configFiles: list
        """

        # get settings
        self._loadConfiguration(configFiles)
        self._setLogFile()

        # set default language
        self.languages = self.getConfigValue("wps","lang").split(",")
        self.defaultLanguage = self.languages[0]

        # set default version
        self.versions=self.getConfigValue("wps","version").split(",")
        self.defaultVersion = self.versions[0]

        # find out the request method
        self.method = method


    def parseRequest(self,queryStringObject):
        """
        Parse input OGC WPS request, which is either URL Query string or
        file object, e.g.  :mod:`sys.stdin`

        :param queryStringObject: string or file object with the request
        :type queryStringObject: string or file object
        :returns: Dictionary of parsed input values
        :rtype: dict
        """

        # decide, which method to use
        # HTTP GET vs. HTTP POST
        if self.method == METHOD_GET:
            from Parser.Get import Get
            self.parser = Get(self)
        else:
            from pywps.Parser.Post import Post
            self.parser = Post(self)

        self.inputs = self.parser.parse(queryStringObject)
        return self.inputs

    def _loadConfiguration(self, cfgfiles=None):
        """Load PyWPS configuration from configuration files.
        The later configuration file in the array overwrites configuration
        from the first.

        :param cfgfiles: list of file names, where to get configuration from.
        :type cfgfiles: list of strings
        """

        if cfgfiles == None:
            cfgfiles = self.getDefaultConfigFilesLocation()

        if type(cfgfiles) != type(()):
            cfgfiles = (cfgfiles)

        self.config = ConfigParser.ConfigParser()
        self.config.read(cfgfiles)

    def getDefaultConfigFilesLocation(self):
        """Get the locations of the standard configuration files. This are

        Unix/Linux:
            1. `pywps/default.cfg`
            2. `/etc/pywps.cfg`
            3. `pywps/etc/pywps.cfg`
            4. `$HOME/.pywps.cfg`

        Windows:
            1. `pywps\\default.cfg`
            2. `pywps\\etc\\default.cfg`
        
        Both:
            1. `$PYWPS_CFG environment variable`

        :returns: configuration files
        :rtype: list of strings
        """

        # configuration file as environment variable
        if os.getenv("PYWPS_CFG"):

            # Windows or Unix
            if sys.platform == 'win32':
                self.workingDir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
                cfgfiles = (os.path.join(self.workingDir,"pywps","default.cfg"),
                        os.getenv("PYWPS_CFG"))
            else:
                cfgfiles = (os.path.join(pywps.__path__[0],"default.cfg"),
                        os.getenv("PYWPS_CFG"))

        # try to eastimate the default location
        else:
            # Windows or Unix
            if sys.platform == 'win32':
                self.workingDir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
                cfgfiles = (os.path.join(self.workingDir,"pywps","default.cfg"),
                        os.path.join(self.workingDir, "pywps","etc","pywps.cfg"))
            else:
                homePath = os.getenv("HOME")
                if homePath:
                    cfgfiles = (os.path.join(pywps.__path__[0],"default.cfg"),
                            os.path.join(pywps.__path__[0],"etc", "pywps.cfg"), "/etc/pywps.cfg",
                        os.path.join(os.getenv("HOME"),".pywps.cfg" ))
                else: 
                    cfgfiles = (os.path.join(pywps.__path__[0],"default.cfg"),
                            os.path.join(pywps.__path__[0],"etc",
                                "pywps.cfg"), "/etc/pywps.cfg")
        return cfgfiles


    def performRequest(self,inputs = None):
        """Performs the desired WSP Request.

        :param inputs: idealy self.inputs (Default) object, result from
            parseRequest. Default is self.inputs
        :rtype: pywps.Wps.Response
        """

        if inputs == None:
            inputs = self.inputs

        # the modules are imported first, when the request type is known
        if inputs.has_key("request"):
            if inputs["request"]  == "getcapabilities":
                from pywps.Wps.GetCapabilities import GetCapabilities
                self.request = GetCapabilities(self)
            elif inputs["request"]  == "describeprocess":
                from pywps.Wps.DescribeProcess import DescribeProcess
                self.request = DescribeProcess(self)
            elif inputs["request"]  == "execute":
                from pywps.Wps.Execute import Execute
                self.request = Execute(self)
        elif inputs.has_key("wsdl"):
            inputs["version"]="1.0.0"
            from pywps.Wps.Wsdl import Wsdl
            self.request = Wsdl(self)
        else:
            raise self.exceptions.InvalidParameterValue(
                    "request: "+inputs["request"])

        self.response = self.request.response
        return self.response

    def getConfigValue(self,*args):
        """Get desired value from  configuration files

        :param section: section in configuration files
        :type section: string
        :param key: key in the section
        :type key: string
        :returns: value found in the configuration file
        :rtype: string
        """

        value = self.config.get(*args)

        # Convert Boolean string to real Boolean values
        if value.lower() == "false":
            value = False
        elif value.lower() == "true" :
            value = True
        return value

    def debug(self,debug,code="Debug"):
        """Print debug argument to standard error

        :param debug: debugging text, which should be printed to the 
            :ref:`logFile`_
        :type debug: string
        :param code: text, which will be printed to the :ref:`logFile`_
            direct after 'PyWPS' and before the debug text
        :type code: string.
        """

        dbg = self.getConfigValue("server","debug")
        if dbg == True or (type(dbg) == type("") and \
                dbg.lower() == "true") or int(dbg) != 0:
            print >>self.logFile, "PyWPS %s: %s" % (code,debug.__str__()[0:160]),
            if len(debug.__str__()) > 160:
                print >>self.logFile, "...",
            print >>self.logFile, "\n"

    def printResponse(self,fileDes,isSoap=False,response=None):
        """
        Print response to files given as input parameter.

        :param fileDes: file object or list of file objects
        :type fileDes: string or list
        :param isSoap: print the response in SOAP envelope
        :type isSoap: bool
        :param response: the response object. Default is self.response
        """

        if type(fileDes) != type([]):
            fileDes = [fileDes]

        if not response:
            response = self.response

        if isSoap:
            soap = Soap.SOAP()
            response = soap.getResponse(response)

        for f in fileDes:

	    if f == STDOUT and self.stdOutClosed == True:
		    continue

            if f == STDOUT:
                print "Content-Type: text/xml"
                #print "Content-Length: %d" % len(self.response)
                print ""

            # open file
            if f != STDOUT and f.closed:
                f = open(f.name,"w")

            # '""' and '"None"'s will be removed
            f.write(re.sub(EMPTYPARAMREGEX,"",response))
            f.flush()

            if (f != STDOUT):
                f.close()

	    # remove stdout from fileDes
	    else: 
		self.stdOutClosed = True

    def _setLogFile(self):
        """Set self.logFile. Default is sys.stderr
        """

        # logfile
        self.logFile = STDERR
        try:
            self.logFile = self.getConfigValue("server","logFile")
            if self.logFile:
                #se = open(self.logFile, 'a+', 0)
                #os.dup2(se.fileno(), STDERR.fileno())
                self.logFile = open(self.logFile,"a+")
            else:
                self.logFile = STDERR
        except ConfigParser.NoOptionError,e:
            pass
        except IOError,e:
            traceback.print_exc(file=STDERR)
            raise self.exceptions.NoApplicableCode("Logfile IOError: %s" % e.__str__())
        except Exception, e:
            traceback.print_exc(file=STDERR)
            raise self.exceptions.NoApplicableCode("Logfile error: %s" % e.__str__())

        self.exceptions.logFile = self.logFile
