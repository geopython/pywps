#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
This program is simple implementation of OGC's [http://opengeospatial.org]
Web Processing Service (OpenGIS(r) Web Processing Service - OGC 05-007r7)
version 1.0.0 from 2007-06-08

Target of this application is to bring functionality of GIS GRASS
[http://grass.itc.it] to the World Wide Web - it should work like
wrapper for modules of this GIS. Though GRASS was at the first place in the
focus, it is not necessary to use it's modules - you can use any program
you can script in Python or other language.

The first version was written with support of Deutsche Bundesstiftung
Umwelt, Osnabrueck, Germany on the spring 2006. SVN server is hosted by
GDF-Hannover, Hannover, Germany.

Current development is supported mainly by:
Help Service - Remote Sensing s.r.o
Cernoleska 1600
256  01 - Benesov u Prahy
Czech Republic
Europe

For setting see comments in 'etc' directory and documentation.

This program is free software, distributed under the terms of GNU General
Public License as published by the Free Software Foundation version 2 of the
License.

Enjoy and happy GISing!

$Id$
"""
__version__ = "3.0-svn"


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
from pywps import Parser
from pywps import Exceptions
from pywps import Wps
from pywps.Exceptions import *

import sys, os, ConfigParser, urllib


class WPS:
    """This is main PyWPS Class, which parses the request, performs the
    desired operation and writes required response back.
    """

    method  =""                      # HTTP POST or GET
    parser = None
    config = None  # Configuration
    workingDir = None # this working directory

    exceptions = pywps.Exceptions

    inputs = {} # parsed input values
    request = None # object with getcapabilities/describeprocess/execute
                   # class

    defaultLanguage = "eng"
    languages = [defaultLanguage]
    defaultVersion = "1.0.0"
    versions=[defaultVersion]

    # global variables
    METHOD_GET="GET"
    METHOD_POST="POST"
    OWS_NAMESPACE = "http://www.opengis.net/ows/1.1"
    WPS_NAMESPACE = "http://www.opengis.net/wps/1.0.0"
    XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"

    def __init__(self):
        """Class constructor

        Will load configuration files, parse the input parameters and
        perform the request.

        """

        # get settings
        self._loadConfiguration()

        # set default language
        self.languages = self.getConfigValue("wps","lang").split(",")
        self.defaultLanguage = self.languages[0]
        # set default version
        self.versions=self.getConfigValue("wps","version").split(",")
        self.defaultVersion = self.versions[0]

        # find out the request method
        self.method = os.getenv("REQUEST_METHOD")
        if not self.method:  # set standard method
            self.method = self.METHOD_GET

        serverPath = urllib.splithost(urllib.splittype(self.getConfigValue("wps","serveraddress"))[1])[1]
        scriptName = os.getenv("SCRIPT_NAME")
        restPath = None
        try:
            restPath= os.getenv("PATH_INFO").split(os.sep)[1:]
        except:
            pass
        self.debug("%s %s %s"% (serverPath, scriptName, restPath))

        # decide, which method to use
        # HTTP GET vs. HTTP POST
        if self.method == self.METHOD_GET:
            from pywps.Parser.Get import Get
            parser = Get(self)
            querystring = ""
            try:
                querystring = os.environ["QUERY_STRING"]
            except KeyError:
                # if QUERY_STRING isn't found in env-dictionary, try to read
                # query from command line:
                if len(sys.argv)>1:  # any arguments available?
                    querystring = sys.argv[1]
            if querystring:
                parser.parse(querystring)
            else:
                raise Exceptions.NoApplicableCode("No query string found.")
        else:
            from pywps.Parser.Post import Post
            parser = Post(self)
            parser.parse(sys.stdin)


        # inputs parsed, perform request
        if self.inputs:
            self.debug(self.inputs)
            self.performRequest()

        # request performed, write the response back
        if self.request.response:
            # print only to standard out
            if self.request.statusFiles == sys.stdout or\
               sys.stdout in self.request.statusFiles:
                self.request.printResponse(self.request.statusFiles,parser.isSoap)

        return

    def _loadConfiguration(self):
        """Load PyWPS configuration from configuration files. This are

        Both:
        $PYWPS_CFG environment variable

        Unix/Linux:
        pywps/default.cfg
        /etc/pywps.cfg
        pywps/etc/pywps.cfg
        $HOME/.pywps.cfg

        Windows:
        pywps\\default.cfg
        pywps\\etc\\default.cfg

        The later overwrites configuration from the first

        """

        cfgfiles = None

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

        self.config = ConfigParser.ConfigParser()
        self.config.read(cfgfiles)

    def performRequest(self):
        """Performs the desired WSP Request."""

        # the modules are imported first, when the request type is known
        if self.inputs.has_key("request"):
            if self.inputs["request"]  == "getcapabilities":
                from pywps.Wps.GetCapabilities import GetCapabilities
                self.request = GetCapabilities(self)
            elif self.inputs["request"]  == "describeprocess":
                from pywps.Wps.DescribeProcess import DescribeProcess
                self.request = DescribeProcess(self)
            elif self.inputs["request"]  == "execute":
                from pywps.Wps.Execute import Execute
                self.request = Execute(self)
        elif self.inputs.has_key("wsdl"):
            self.inputs["version"]="1.0.0"
            from pywps.Wps.Wsdl import Wsdl
            self.request = Wsdl(self)
        else:
            raise self.exceptions.InvalidParameterValue(
                    "request: "+self.inputs["request"])

    def getConfigValue(self,*args):
        """Return desired value from the configuration files

        Keyword arguments:
        section -- section in configuration files
        key -- key in the section

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
        """

        dbg = self.getConfigValue("server","debug")
        if dbg == True or (type(dbg) == type("") and \
                dbg.lower() == "true") or int(dbg) != 0:
            print >>sys.stderr, "PyWPS %s: %s" % (code,debug.__str__()[0:160]),
            if len(debug.__str__()) > 160:
                print >>sys.stderr, "...",
            print >>sys.stderr, "\n"

if __name__ == "__main__":
    wps = WPS()
