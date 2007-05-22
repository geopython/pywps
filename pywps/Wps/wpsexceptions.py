"""
Exception classes of WPS
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

from xml.dom.minidom import Document
import sys
        
called = 0

class WPSException(Exception):
    """
    WPSException should be base class for all exeptions
    """
    def make_xml(self):
        # formulate XML
        self.document = Document()
        self.ExceptionReport = self.document.createElementNS("http://www.opengis.net/ows","ExceptionReport")
        self.ExceptionReport.setAttribute("xmlns","http://www.opengis.net/ows")
        self.ExceptionReport.setAttribute("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        self.ExceptionReport.setAttribute("version","1.0.0")
        self.document.appendChild(self.ExceptionReport)

        # make exception
                
        self.Exception = self.document.createElement("Exception")
        self.Exception.setAttribute("exceptionCode",self.code)

        if self.locator:
            self.Exception.setAttribute("locator",self.locator)
            self.ExceptionReport.appendChild(self.Exception)

        self.ExceptionReport.appendChild(self.Exception)


    def __str__(self):

        str = "Content-type: text/xml\n\n"
        str += self.document.toprettyxml(indent='\t', newl='\n', encoding="utf-8")
        sys.stderr.write("PyWPS %s: %s" % (self.code, self.locator))

        # FIXME: To avoid multiple printing, this hack works
        #        however, I do not know, why it is printed two times :-(
        global called
        if not called:
            print str
        called += 1

class MissingParameterValue(WPSException):
    def __init__(self, value):
        self.code = "MissingParameterValue"
        self.locator = value
        self.make_xml()

class InvalidParameterValue(WPSException):
    def __init__(self,value):
        self.code = "InvalidParameterValue"
        self.locator = value
        self.make_xml()

class NoApplicableCode(WPSException):
    def __init__(self,value=None):
        self.code = "NoApplicableCode"
        self.locator = value
        self.make_xml()
        self.ExceptionReport.appendChild(self.document.createComment(repr(locator)))

class ServerBusy(WPSException):
    def __init__(self,value=None):
        self.code = "ServerBusy"
        self.locator = value
        self.make_xml()

class FileSizeExceeded(WPSException):
    def __init__(self,value=None):
        self.code = "FileSizeExceeded"
        self.locator = value
        self.make_xml()

class ServerError(WPSException):
    def __init__(self,value=None):
        self.code = "ServerError"
        self.locator = str(value)
        self.make_xml()
        self.ExceptionReport.appendChild(self.document.createComment("General server error"))
