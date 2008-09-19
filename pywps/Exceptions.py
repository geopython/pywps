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
    WPSException should be base class for all exceptions
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
        self.value = None

    def __str__(self):

        str = "Content-type: text/xml\n\n"
        str += self.document.toprettyxml(indent='\t', newl='\n', encoding="utf-8")
        sys.stderr.write("PyWPS %s: %s\n" % (self.code, self.locator))
        print str

class MissingParameterValue(WPSException):
    def __init__(self, value):
        self.code = "MissingParameterValue"
        self.locator = str(value)
        self.make_xml()

class InvalidParameterValue(WPSException):
    def __init__(self,value):
        self.code = "InvalidParameterValue"
        self.locator = str(value)
        self.make_xml()

class NoApplicableCode(WPSException):
    def __init__(self,value=None):
        self.code = "NoApplicableCode"
        self.locator = None
        self.make_xml()
        if value:
            self.ExceptionText = self.document.createElement("ExceptionText")
            self.ExceptionText.appendChild(self.document.createTextNode(value))
            self.Exception.appendChild(self.ExceptionText)
            self.value = str(value)

class VersionNegotiationFailed(WPSException):
    def __init__(self,value=None):
        self.code = "VersionNegotiationFailed"
        self.locator = None
        self.make_xml()
        if value:
            self.ExceptionText = self.document.createElement("ExceptionText")
            self.ExceptionText.appendChild(self.document.createTextNode(value))
            self.Exception.appendChild(self.ExceptionText)
            self.value = str(value)

class ServerBusy(WPSException):
    def __init__(self,value=None):
        self.code = "ServerBusy"
        self.locator = str(value)
        self.make_xml()

class FileSizeExceeded(WPSException):
    def __init__(self,value=None):
        self.code = "FileSizeExceeded"
        self.locator = str(value)
        self.make_xml()

class ServerError(WPSException):
    def __init__(self,value=None):
        raise NoApplicableCode(value)
        self.code = "ServerError"
        try:
            self.locator = str(value)
        except:
            self.locator = None
        self.make_xml()
        self.ExceptionText = self.document.createElement("ExceptionText")
        self.ExceptionText.appendChild(self.document.createTextNode("General server error"))
        self.Exception.appendChild(self.ExceptionText)
