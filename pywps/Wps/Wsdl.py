##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################
"""
WPS WSDL request handler
"""

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

  