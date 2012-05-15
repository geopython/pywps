"""Exception classes of WPS """
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
import pywps
from re import escape
from pywps.Soap import SOAP
import pywps.Soap
import sys

called = 0

class WPSException(Exception):
    """WPSException should be base class for all exceptions
    """
    code = "NoApplicableCode"
    value = None
    locator = None

    def _make_xml(self):
        # formulate XML
        self.document = Document()
        self.ExceptionReport = self.document.createElementNS("http://www.opengis.net/ows","ExceptionReport")
        self.ExceptionReport.setAttribute("xmlns","http://www.opengis.net/ows/1.1")
        self.ExceptionReport.setAttribute("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        self.ExceptionReport.setAttribute("xsi:schemaLocation","http://www.opengis.net/ows/1.1 http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd")
        self.ExceptionReport.setAttribute("version","1.0.0")
        self.document.appendChild(self.ExceptionReport)

        # make exception

        self.Exception = self.document.createElement("Exception")
        self.Exception.setAttribute("exceptionCode",self.code)

        if self.locator:
            self.Exception.setAttribute("locator",self.locator)

        self.ExceptionReport.appendChild(self.Exception)
        #self.value = None

    def getResponse(self):
        return self.document.toprettyxml(indent='\t', newl='\n', encoding="utf-8")
        if pywps.Soap.soap == True:
            soapCls = SOAP()
            response = soapCls.getResponse(response)

    def __str__(self):
        error = "PyWPS %s: Locator: %s; Value: %s\n" % (self.code, self.locator, self.value)
        try:
            logFile.write(error)
        except:
            sys.stderr.write(error)

        return self.document.toprettyxml(indent='\t', newl='\n', encoding="utf-8")

class MissingParameterValue(WPSException):
    """MissingParameterValue WPS Exception"""
    def __init__(self, value):
        self.code = "MissingParameterValue"
        self.locator = str(value)
        self._make_xml()

class InvalidParameterValue(WPSException):
    """InvalidParameterValue WPS Exception"""
    def __init__(self,value):
        self.code = "InvalidParameterValue"
        self.locator = str(value)
        self._make_xml()

class NoApplicableCode(WPSException):
    """NoApplicableCode WPS Exception"""
    def __init__(self,value=None):
        WPSException.__init__(self,value)
        self.code = "NoApplicableCode"
        self.value = None
        self._make_xml()
        self.message = value
        if value:
            self.ExceptionText = self.document.createElement("ExceptionText")
            self.ExceptionText.appendChild(self.document.createTextNode(repr(value)))
            self.Exception.appendChild(self.ExceptionText)
            self.value = escape(value)

class VersionNegotiationFailed(WPSException):
    """VersionNegotiationFailed WPS Exception"""
    def __init__(self,value=None):
        self.code = "VersionNegotiationFailed"
        self.locator = None
        self._make_xml()
        if value:
            self.ExceptionText = self.document.createElement("ExceptionText")
            self.ExceptionText.appendChild(self.document.createTextNode(value))
            self.Exception.appendChild(self.ExceptionText)
            self.value = str(value)

class NotEnoughStorage(WPSException):
    """NotEnoughStorage WPS Exception"""
    def __init__(self,value=None):
        self.code = "NotEnoughStorage"
        self.locator = value
        self._make_xml()

class StorageNotSupported(WPSException):
    """StorageNotSupported WPS Exception"""
    def __init__(self,value=None):
        self.code = "StorageNotSupported"
        self.locator = value
        self._make_xml()

class ServerBusy(WPSException):
    """ServerBusy WPS Exception"""
    def __init__(self,value=None):
        self.code = "ServerBusy"
        self.value = value
        self._make_xml()

class FileSizeExceeded(WPSException):
    """FileSizeExceeded WPS Exception"""
    def __init__(self,value=None):
        self.code = "FileSizeExceeded"
        self.locator = str(value)
        self._make_xml()

class ServerError(WPSException):
    """ServerError WPS Exception
    
    .. note:: This is custom PyWPS exception and should not be used."""
    def __init__(self,value=None):
        raise NoApplicableCode(value)
        self.code = "ServerError"
        try:
            self.locator = str(value)
        except:
            self.locator = None
        self._make_xml()
        self.ExceptionText = self.document.createElement("ExceptionText")
        self.ExceptionText.appendChild(self.document.createTextNode("General server error"))
        self.Exception.appendChild(self.ExceptionText)

