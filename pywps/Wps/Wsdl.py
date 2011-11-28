"""
WPS WSDL request handler
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
from pywps.Wps import Request
from pywps.Wps.DescribeProcess import DescribeProcess
from pywps.Template import TemplateError
from pywps import XSLT 
import os,types
import pywps
from pywps import config
from lxml import etree
import StringIO
import re

########### START OF XSLT FUNCTIONS ##################


# http://www.w3.org/TR/REC-xml/#charsets (only ":" | [A-Z] | "_" | [a-z])
regExp=re.compile(r"[^a-zA-Z_:]*") 
def flagRemover(dummy,strXML):
    """Function called from describeProcess2WSDL.xsl and necessary
    to remove any char that is not allowed as Element name only (":" | [A-Z] | "_" | [a-z]) allowed as start char"""
    endN=regExp.match(strXML).end()
    return strXML[endN:]

#Registering necessary etree functions
ns=etree.FunctionNamespace("http://pywps.wald.intevation.org/functions")
ns.prefix='fn'
ns["flagRemover"]=flagRemover

########### END OF XSLT FUNCTIONS ##################

class Wsdl(Request):
    """
    """

    def __init__(self,wps):
        """
        Arguments:
           self
           wps   - parent WPS instance
        """
        Request.__init__(self,wps)
        #
        # global variables
        #
        serverName = "".join(map(lambda x: x.capitalize(),config.getConfigValue("wps","title").split()))
        #self.templateProcessor.set("name",name)
        #self.templateProcessor.set("address",config.getConfigValue("wps","serveraddress"))
        
        
        
        serverURL=config.getConfigValue("wps","serveraddress")
        
        #Generating a describeProcess for all processes
        wps2=pywps.Pywps()
        wps2.inputs={'identifier': ['all'], 'version': '1.0.0', 'request': 'describeprocess', 'language': 'eng', 'service': 'wps'}
        requestDescribeProcess=DescribeProcess(wps2)
        describeProcessXML=requestDescribeProcess.response
        
        
        #Transforming the describeProcessXML into WSDL document
        describeProcess2WSDLXSL=open(pywps.XSLT.__path__[0]+"/describeProcess2WSDL.xsl","r")
        transformerXSLT=etree.XSLT(etree.parse(describeProcess2WSDLXSL))
        
        #Recall: serverName/serverURL parameters are XPath structures, therefore we need '' in the string: 'http://foo/dummy' to be used by XSLT
        WSDLTree=transformerXSLT(etree.parse(StringIO.StringIO(describeProcessXML)),serverName="'"+serverName+"'",serverURL="'"+serverURL+"'")
        
        #Concerting to String from tree
        WSDL=etree.tostring(WSDLTree)
        
        #Attention: It's not possible to set the tns namespace to the server's URL 
        #with XSLT, since it is in the root element. The XML contains a REPLACEME string that 
        #will be replaced only once (so the process is very efficient)
        
        WSDL=re.sub(r'REPLACEME',serverURL,WSDL,1)
        
        self.response=WSDL

        return

  