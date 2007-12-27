"""
Request handler - prototype class
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
#               jachym at les-ejk dot cz
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

import xml.dom.minidom
from htmltmpl import TemplateManager, TemplateProcessor
import os
from pywps import Templates

class Request:
    response = None # Output document
    wps = None # Parent WPS object
    templateManager = None # HTML TemplateManager
    templateProcessor = TemplateProcessor() # HTML TemplateProcessor
    template = None # HTML Template
    templateFile = None # File with template

    def __init__(self,wps):
        self.wps = wps

        self.templateManager = TemplateManager(precompile = 1, 
            debug = self.wps.config.getboolean("server","debug")) 

        if self.wps.inputs["request"] == "getcapabilities":
            self.templateFile = os.path.join(
                                os.path.join(Templates.__path__)[0],
                                     "GetCapabilities.tmpl")
        elif self.wps.inputs["request"] == "describeprocess":
            self.templateFile = os.path.join(
                                os.path.join(Templates.__path__)[0],
                                    "Templates","DescribeProcess.tmpl")
        elif self.wps.inputs["request"] == "execute":
            self.templateFile = os.path.join(
                                os.path.join(Templates.__path__)[0],
                                    "Templates","Execute.tmpl")
