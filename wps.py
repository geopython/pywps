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

import pywps
from pywps.etc import grass
from pywps.etc import settings
from pywps import Wps
from pywps.Wps import wpsexceptions
from pywps.Wps.wpsexceptions import *
from pywps.Wps import capabilities
from pywps.Wps import describe
from pywps.Wps import execute
from pywps.Wps import inputs
from pywps import processes
from pywps.processes import *


import string, sys, os, tempfile, glob, shutil, time, cgi
#import cgitb; cgitb.enable()

def main():
    """
    This main function controlls input variables and calls either
    GetCapabilities, DescribeProcess or Execute functions.

    If Execute request is called, the temporary directory will be created
    and everything should happen in this directory.
    """
    
    try:
        formValues = {}  # input values
        serverSettings = settings.ServerSettings
        inpts = inputs.Inputs() # data inputs
        pid = os.getpid()
        method = os.getenv("REQUEST_METHOD")
        

        try: #  Maximal length of one input
            if method == "GET" or not method:
                maxSize = int(serverSettings['maxInputParamLength'])
                maxSize = int(serverSettings['maxSize'])
        except:
            if method == "GET" or not method:
                maxSize = 1024
            else:
                maxSize = 0 # will be controlled later

        # key values to lower case
        if method == "GET" or not method:
            form = cgi.FieldStorage()  # the input values (GET method)
            for key in form.keys():
                value = form.getvalue(key)
                # to avoid problems with more then one inputs
                if type(form.getvalue(key)) == type([]):
                    value = value[-1].strip()

                value = value.strip()

                if len(value) > maxSize and maxSize > 0:
                    raise FileSizeExceeded(key)
                    return
                formValues[key.lower()] = value

        #
        # HTTP POST
        if method == "POST":
            try:
                size = serverSettings['maxSize']
            except:
                size = 0
            inpts.formvalsPost2dict(sys.stdin,size)


        #
        # HTTP GET
        else:
            inpts.formvalsGet2dict(formValues)

            # request 
            if not 'request' in inpts.values.keys():
                raise MissingParameterValue("request")

            #
            # Check inputs again
            if not 'service' in inpts.values.keys(): 
                raise MissingParameterValue("service")

            elif not 'version' in inpts.values.keys() and \
                inpts.values['request'].lower() != "getcapabilities":
                raise MissingParameterValue(version)
            
            # service == wps
            if inpts.values['service'].lower() != 'wps':
                raise InvalidParameterValue('service')
            # version == 0.4.0
            elif inpts.values['request'].lower() != "getcapabilities" \
                and inpts.values['version'].lower() != '0.4.0':
                raise InvalidParameterValue('version')




        # Controll of all 'identifier' values - if wrongprocess is
        # set, exception, nothing otherwice
        wrongprocess = inpts.controllProcesses(
                processes.__all__,inpts.values)
        if wrongprocess:
            if wrongprocess != "identifier":
                raise InvalidParameterValue(wrongprocess)
            else:
                raise MissingParameterValue(wrongprocess)
            return

        #---------------------------------------------------------------------

        #
        # Request  handeling
        #
        
        #
        # GetCapabilities
        if inpts.values['request'].lower() == "getcapabilities":
            getCapabilities = capabilities.Capabilities(settings,processes)
            print "Content-type: text/xml\n"
            print getCapabilities.document.toprettyxml()
        #
        # DescribeProcess
        elif inpts.values["request"].lower() == "describeprocess":
            describeProc = describe.Describe(settings,processes,inpts.values)
            if describeProc.document != None:
                print "Content-type: text/xml\n"
                print describeProc.document.toprettyxml()
        #
        # Execute
        elif inpts.values["request"].lower() == "execute":

            # Create PID file, temp directory etc.
            # check for number of running operations
            try:
                nPIDFiles = len(glob.glob(
                    os.path.join(settings.ServerSettings['tempPath'],"pywps-pidfile-*")))
                # cleaning if something goes wrong
                # for file in glob.glob(
                #         os.path.join(settings.ServerSettings['tempPath'],"pywps*")):
                #     sys.stderr.write(file+"\n")
                #     os.remove(file)
            except (IOError, OSError), what:
                raise ServerError("IOError,OSError: %s" % what)
            try:
                maxPIDFiles = settings.ServerSettings['maxOperations']
            except KeyError:
                maxPIDFiles = 1

            # too many processes ?
            if nPIDFiles >=  maxPIDFiles:
                raise ServerBusy()
            else:
                PIDFile = tempfile.mkstemp(prefix="pywps-pidfile-")
                pass


            # MAKE
            process = eval("processes.%s.Process()" %
                    (inpts.values['identifier'][0]))
            executeProc = None
            try:
                executeProc = execute.Execute(settings,grass.grassenv,process,inpts.values,method)
            except Exception,e:
                # cleaning
                os.remove(PIDFile[1])
                raise ServerError(e)


            # asynchronous?
            # only, if this is child process:
            if not executeProc.pid:
                file = open(
                    os.path.join(settings.ServerSettings['outputPath'],executeProc.executeresponseXmlName),"w")
                sys.stdout = file

            # clean the PID file        
            if not (executeProc.status.lower() == "processaccepted" or \
                    executeProc.status.lower() == "processstarted"):
                    os.remove(PIDFile[1])

            if executeProc.document:
                if sys.stdout == sys.__stdout__:
                    print "Content-type: text/xml\n"
                print executeProc.document.toprettyxml(indent='\t', newl='\n')
            else:
                # clean the PID file        
                try:
                    os.remove(PIDFile[1])
                except:
                    pass

            # only, if this is child process:
            if not executeProc.pid:
                file.close()
        else:
            raise InvalidParameterValue("request")
    # catch all exceptions
    except Exception, e:
        print e
        return


        
if __name__ == "__main__":
    main()

