"""
SOAP
----
SOAP wrapper 
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# License:
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


#HTTP_SOAPACTION': '"http://localhost/wps.cgi/DescribeProcess"

from xml.dom import minidom

from xml.sax.saxutils import unescape # Very practical unescape char converted
from xml.xpath.Context  import Context #Context setting for namespace support
from xml.xpath import Evaluate
from xml.xpath import Compile

def getFirstChildNode(document):
    for node in document.childNodes:
        if node.nodeType == minidom.Element.nodeType:
            firstChild = node
        
    document=firstChild
    return document


#For soap 1.2 -->http://www.w3.org/2003/05/soap-envelope (self.nsIndex=0)
#For soap 1.1 -->http://schemas.xmlsoap.org/soap/envelope/ (self.nsIndex=1)
soap_env_NS = ["http://www.w3.org/2003/05/soap-envelope","http://schemas.xmlsoap.org/soap/envelope/"]
soap_enc_NS = ["http://www.w3.org/2003/05/soap-encoding","http://schemas.xmlsoap.org/soap/encoding/"]

#Envelope for soap 1.2
SOAP_ENVELOPE12="""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.w3.org/2003/05/soap-envelope
	http://www.w3.org/2003/05/soap-envelope">
	<soap:Body>$SOAPBODY$</soap:Body>
</soap:Envelope>"""

#Envelope for soap 1.1
SOAP_ENVELOPE11="""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/1999/XMLSchema">
<SOAP-ENV:Body>$SOAPBODY$</SOAP-ENV:Body></SOAP-ENV:Envelope>"""

WPSNamespace= {"wps":"http://www.opengis.net/wps/1.0.0"}
import logging

soap = False


def isSoap(document): 
    global soap
    if document.localName == "Envelope" and\
            document.namespaceURI in soap_env_NS:
        soap = True
        return True
    else:
        soap = False
        return False

class SOAP:
    """Soap wrapper, used for parsing requests, which are in Soap envelope
    and creating Soap responses from normal XMLs.

    .. note:: This class is very primitive, it does not support advanced
        Soap features, like authorization and so on.

    """

    document = None
    nsIndex = 0

    def __init__(self,document=None):
		
        if document:
            if type(input) == type(""):
                self.document = minidom.parseString(unescape(document,entities={"&quot;":"'"}))
            else:
                self.document = minidom.parseString(unescape(document.toxml(),entities={"&quot;":"'"})) # Not very efficient, the XML is converted to string and then back again to XML
            self.nsIndex = soap_env_NS.index(document.namespaceURI)
            logging.debug("NameSpaceURI %s" % document.namespaceURI)
            if (self.nsIndex==1):
            	self.soapVersion=11
            else:
            	self.soapVersion=12
            #logging.debug("SoapVersion %s" % self.soapVersion)	
    #getNode has been replaced with getWPSContent()  
    #def getNode(self,namespace,nodeName):
    #    """Get XML nod from DOM of specified name and namespace"""

    #    elements = self.document.getElementsByTagNameNS(namespace, nodeName)
    #    if len(elements) > 0:
    #        return elements[0]
    #    else:
    #        return None
    
    def getWPSContent(self):
    	    """Get the specific XWPS ML content of inside the SOAP request. The Element position may change if there is a SOAP header or if is was sent as a message inside the Body content"""   
	    #Creating context that will be used by xpath
        #logging.debug("Taverna is sending the following request")
	    #logging.debug(str(self.document.toxml()))
	    context=Context(self.document)
	    #setting WPS name spaces
	    context.setNamespaces(WPSNamespace)
	    #Generating xpath expression for the 3 WPS possibilities
	    xpathExpression=Compile("//*[local-name() = 'GetCapabilities'] | //*[local-name() = 'DescribeProcess'] | //*[local-name() = 'Execute']")
	    #xpathExpression = Compile("//wps:Execute | //wps:GetCapabilities | //wps:DescribeProcess")
	    #Getting WPS content as first result of list
	    WPSDocument=xpathExpression.evaluate(context)[0]
	    
	    if WPSDocument.getAttribute("service")=="":
    	 	WPSDocument.setAttribute("service","WPS")
        #Crap Eclpse indent
        
        
            tagNameRequest=WPSDocument.localName
            #logging.debug("LocalName tag: %s" % tagNameRequest)
            
         #   tagNameRequest=firstElement.tagName.split(":")[1]
            if tagNameRequest=="DescribeProcess" or tagNameRequest=="Execute":
                WPSDocument.setAttribute("version","1.0.0")
       		
	    ###Dumping server variables for checking
            #import os
            #logging.debug(str(os.environ))
            
            #logging.debug(WPSDocument.toxml())    
            
	    return WPSDocument
	    #return getFirstChildNode(WPSDocument)


    def getSOAPVersion(self):
		return self.soapVersion

    def getResponse(self,document,soapVersion):
        """Wrap document into soap envelope"""
        # very primitive, but works
        #SOAP 1.1 Content-type: text/xml
        # SOAP 1.2   Content-Type: application/xml maybe application/soap ?!
        
        document = document.__str__().replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>","")
        #return SOAP_ENVELOPE.replace("$SOAPBODY$",document)
       
        if (int(soapVersion)==11):
         	return SOAP_ENVELOPE11.replace("$SOAPBODY$",document)
        else:
        	return SOAP_ENVELOPE12.replace("$SOAPBODY$",document)
        
	
