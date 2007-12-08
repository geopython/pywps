#!/usr/bin/env python 
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

import pywps
from pywps import Parser 
from pywps import Exeptions
from pywps.Exceptions import *

import sys, os, cgi, ConfigParser

class WPS:

    method  =""                      # HTTP Ost or GET 
    pidFilePrefix = "pywps-pidfile-" # pid file prefix
    maxInputLength = 0  # maximal length of one input item
    maxFileSize = 0 # maximal input XML or other file size
    maxInputSize = 0 # maximal size of HTTP Get request
    parser = None
    config = None  # Configuration
    workingDir = None # this working directory

    METHOD_GET="GET"
    METHOD_POST="POST"
    exceptions = pywps.Exceptions

    DEFAULT_WPS_VERSION = "1.0.0"
    VERSION = "3.0-svn"
    DEFAULT_LANGUAGE = "en"

    def __init__(self):

        # getsettings
        self.loadConfiguration()

        # findout the request method
        self.method = os.getenv("REQUEST_METHOD")
        if not self.method:
            self.method = self.METHOD_GET

        if self.method == self.METHOD_GET:
            from pywps.Parser.Get import Get
            parser = Get(self)
            parser.parse(cgi.FieldStorage())
        else:
            from pywps.Parser.Post import Post
            parser = Post(self)
            parser.parse(sys.stdin)

        return
    
    def loadConfiguration(self):

        cfgfiles = None

        if sys.platform == 'win32':
            self.workingDir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
            cfgfiles = (os.path.join(workingDir, "pywps","etc","pywps.cfg"),
                    os.path.join(workingDir,"pywps","etc","grass.cfg"))
        else:
            cfgfiles = (os.path.join("pywps","etc", "pywps.cfg"), "/etc/pywps.cfg")

        self.config = ConfigParser.ConfigParser()
        self.config.read(cfgfiles)

if __name__ == "__main__":
    wps = WPS()
