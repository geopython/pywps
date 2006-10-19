#!/usr/bin/python
# -*- coding: ISO-8859-2 -*-

# $Id$
# Author:	Jachym Cepicky
#		http://les-ejk.cz

from xml.dom.minidom import Document

class WPSExceptions:
    def __init__(self):
        self.document = Document()
        self.ExceptionReport = self.document.createElementNS("http://www.opengis.net/ows","ExceptionReport")
        self.ExceptionReport.setAttribute("xmlns","http://www.opengis.net/ows")
        self.ExceptionReport.setAttribute("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        self.ExceptionReport.setAttribute("version","1.0.0")
        self.document.appendChild(self.ExceptionReport)

        return

    def make_exception(self,code,locator=None):
        locator =  "%s" % locator
        if code =="NoApplicableCode":
            self.Exception = self.document.createElement("Exception")
            self.Exception.setAttribute("exceptionCode",code)
            self.ExceptionReport.appendChild(self.document.createComment(repr(locator)))
        else:
            self.Exception = self.document.createElement("Exception")
            self.Exception.setAttribute("exceptionCode",code)
        if locator:
            self.Exception.setAttribute("locator",locator)
            self.ExceptionReport.appendChild(self.Exception)

        self.ExceptionReport.appendChild(self.Exception)
        return self.document.toprettyxml(indent='\t', newl='\n', encoding="utf-8")

        

