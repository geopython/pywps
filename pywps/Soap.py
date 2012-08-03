"""
SOAP
----
SOAP wrapper 
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# Author:  Jorge de Jesus
#		   http://rsg.pml.ac.uk
#          jmdj@pml.ac.uk
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

from lxml import etree
import StringIO
import pywps

from pywps import XSLT

import types
import re

########### START OF XSLT FUNCTIONS ##################
def getCorrectInputID(dummy,identifier):
	"""XSLT function that converts the I/O identifier into a correct process I/O identifier. This is necessary
	to deal with cases like <ows:Identifier>--flag<ows:Identifier> that get converted into <flag> elements, in the WSDL description. 
	Function will do a reverse mapping. Simple flags like -r are problematic to map since they are only one char"""
	
	#Note it's not very efficient to generate a dictionary everything pywps checks an input.I/O are very small (5,6 elements in a process)
	#The use oh a key:value instead of a loop like  correctInput=[input for input in inputKeys if input.find(identifier)>-1][0] , managed to deal
	# with processes that have flags with one char that would return any inputs that would contain the char
	inputMap={}
	processInputKeys=process.inputs.keys()
	[inputMap.__setitem__(flagRemover("dummy",input),input) for input in processInputKeys]
	correctInput=inputMap[identifier] #get the correct input
	return correctInput

# http://www.w3.org/TR/REC-xml/#charsets (only ":" | [A-Z] | "_" | [a-z])
regExp=re.compile(r"[^a-zA-Z_:]*") 
def flagRemover(dummy,strXML):
    """Remove any char that is not allowed as Element name only (":" | [A-Z] | "_" | [a-z]) allowed as start char. Same function as describeProcess2WSDL"""
    endN=regExp.match(strXML).end()
    return strXML[endN:]

def isComplexData(dummy,inputName):
    
    inputInstance=process.inputs[inputName]
    #Checking if the input is of complexInput type
    return isinstance(inputInstance,pywps.Process.InAndOutputs.ComplexInput("foo","foo").__class__)



ns=etree.FunctionNamespace("http://pywps.wald.intevation.org/functions")
ns.prefix='fn'
ns["getCorrectInputID"]=getCorrectInputID
ns["flagRemover"]=flagRemover
ns["isComplexData"]=isComplexData
########### END OF XSLT FUNCTIONS ##################

#For soap 1.2 -->http://www.w3.org/2003/05/soap-envelope (self.nsIndex=0)
#For soap 1.1 -->http://schemas.xmlsoap.org/soap/envelope/ (self.nsIndex=1)
soap_env_NS = ["http://www.w3.org/2003/05/soap-envelope","http://schemas.xmlsoap.org/soap/envelope/"]
soap_enc_NS = ["http://www.w3.org/2003/05/soap-encoding","http://schemas.xmlsoap.org/soap/encoding/"]

#Envelope for soap 1.2
SOAP_ENVELOPE_FAULT12="""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.w3.org/2003/05/soap-envelope
	http://www.w3.org/2003/05/soap-envelope">
	<soap:Body><soap:Fault><soap:Code><soap:Value>soap:Sender</soap:Value></soap:Code><soap:Reason><soap:Text>$REPORT$</soap:Text></soap:Reason><soap:Detail>$REPORTEXCEPTION$</soap:Detail></soap:Fault></soap:Body>
</soap:Envelope>"""

SOAP_ENVELOPE12="""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.w3.org/2003/05/soap-envelope
	http://www.w3.org/2003/05/soap-envelope">
	<soap:Body>$SOAPBODY$</soap:Body>
</soap:Envelope>"""


#Envelope for soap 1.1
SOAP_ENVELOPE11="""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/1999/XMLSchema">
<SOAP-ENV:Body>$SOAPBODY$</SOAP-ENV:Body></SOAP-ENV:Envelope>"""

#Its assumed that the fault it always caused by the client PyWPS is 100% correct :)
#Faultstring contains a description string of the error, Taverna only show this
#The WSDL defines the ows:ExceptionReport as fault structure inside <detail>
SOAP_ENVELOPE_FAULT11="""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/1999/XMLSchema">
<SOAP-ENV:Body><SOAP-ENV:Fault><faultcode>SOAP-ENV:Client</faultcode><faultstring>$REPORT$</faultstring><detail>$REPORTEXCEPTION$</detail></SOAP-ENV:Fault></SOAP-ENV:Body></SOAP-ENV:Envelope>"""

###### GLOBALS #######
soap = False
process=None #filled in SOAP2WPS and then used by getCorrectInputID isComplexInput
######################

def isSoap(document): 
    global soap
    
    if document.localName == "Envelope" and\
            document.namespaceURI in soap_env_NS:
        soap = True
        return True
    else:
        soap = False
        return False

def getFirstChildNode(document):
    for node in document.childNodes:
        if node.nodeType == minidom.Element.nodeType:
            firstChild = node
        
    document=firstChild
    return document

def SOAPtoWPS(tree):
    #NOTE: 
    #The etree output of ComplexData will not contain the OWS/WPS/XSI namespace since this name space is defined in the head of the WPS:Execute
    #The XSI is not necessary in the WPS:Execute, therefore it was deleted and its now inside the ComplexInput (if necessary)
    #An input shouldn't have elements in with OWS/WPS namespace, nevertheless a hack was implemented that allows for their presence.
    #The solution is a tiny hack the XSL file, the WPS/OWS namespace are different from the ComplexInput, something like this: http://REPLACEME/wps/1.0.0
    #When etree is printed the REPLACEME is subtituted by www.opengis.net, creating the correct namespaces for the DOM parsing.
    #The replace is done using module re and set that it has to do only 2 replaces in the beggining. Therefore the replace is independe of the since of XML content
    global process
    from pywps import processes
    
    processID=tree.tag.split("_",1)[-1]
    wps2=pywps.Pywps()
    wps2.inputs={'request': 'getCapabilities', 'version': '1.0.0', 'service': 'wps'}
    from pywps.Wps import Request
    
    request=Request(wps2)
    try:
     	process=[process for process in request.processes if process.identifier in [processID]][0]
    except IndexError:
    #	#If the server url is incorrect the process request will not be found in the WPS process list
    	raise pywps.NoApplicableCode("The requested process is not part of the instance. Check pywps conf file and WSDL. WSDL has to point to the correct wrapper, please check location attribute in address element of WSDL document")	
    XSLTDocIO=open(pywps.XSLT.__path__[0]+"/SOAP2WPS.xsl","r")
   
    XSLTDoc=etree.parse(XSLTDocIO)
   
    transformer=etree.XSLT(XSLTDoc)
    WPSTree = transformer(tree)
    etree.cleanup_namespaces(WPSTree)
    
    XMLOut=etree.tostring(WPSTree)
    XMLOut=re.sub(r'REPLACEME',"www.opengis.net",XMLOut,2)
    return XMLOut


def WPStoSOAP(tree):
	
	
	#If we have an expection then will just dump the Exception report and not the WPS failure + Exception Report
	# This allows for the use of message ows:ExectionReport in the WSDL process description
    XSLTDocIO=open(pywps.XSLT.__path__[0]+"/WPS2SOAP.xsl","r")
   
    #Output: string XML 
    root=tree.getroot() #root is <type 'lxml.etree._Element'>
    #Check for Exception:
    exceptionElementList=root.xpath("//*[local-name()='Exception']")
    if bool(exceptionElementList):
    	#Just dump the OGC exception
    	return etree.tostring(exceptionElementList[0])
   
     

    XSLTDoc =etree.parse(XSLTDocIO)
    transformer=etree.XSLT(XSLTDoc)
    SOAPTree=transformer(tree)
   
    return etree.tostring(SOAPTree)

def doFixTavernaBug(WPSTree):
	#Taverna hack until version 2.3 release
	
	#Check that the attributes are empy
	if not bool(WPSTree.attrib):
		WPSTree.set("service","WPS")
		
	tagNameRequest=WPSTree.tag.split("}")[1]
        #tagNameRequest=firstElement.tagName.split(":")[1]
        if tagNameRequest=="DescribeProcess" or tagNameRequest=="Execute":
             WPSTree.set("version","1.0.0")
     

	return WPSTree


def doCleanBug5762(document):
#Please check for explanation	
#http://bugs.python.org/issue5762
#Problem cause by an empty XMLNS in the root element of the document
#It's OK to have an empty attribute. Bug fixed in new python versions (2010-10-15 17:59) 	
#Check for empty attributed in the root element and remove it:
    
    for node in doc_order_iter(document):
	    attrMap=node.attributes
	    try:
       	    	for attrKey in attrMap.keys():
          		attr=attrMap[attrKey]
                  
                if (type(attr.value)==types.NoneType or len(attr.value)==0):
            	    node.removeAttribute(attr.name)
                   
                    
     	    except:
		pass
    return document

def doc_order_iter(node):
    """
    Iterates over each node in document order,
    returning each in turn
    http://www.ibm.com/developerworks/library/x-tipgenr.html
    """
    #Document order returns the current node,
    #then each of its children in turn
    yield node
    for child in node.childNodes:
        #Create a generator for each child,
        #Over which to iterate
        for cn in doc_order_iter(child):
            yield cn
    return

class SOAP:
    """Soap wrapper, used for parsing requests, which are in Soap envelope
    and creating Soap responses from normal XMLs.

    .. note:: This class is very primitive, it does not support advanced
        Soap features, ralike authorization and so on.
    .. note: The class requires the lxml package to be installed so that XSLT can be used. The xml.dom module lacks such functionality    

    """

    document = None
    nsIndex = 0

    def __init__(self,document=None):
        if document:
        	#http://bugs.python.org/issue5762
            parser=etree.XMLParser(resolve_entities=False)
            try:
               if type(input) == type(""):
                  self.tree=etree.parse(StringIO.StringIO(unescape(document,entities={"&quot;":"'"})),parser)
               #<?xml version='1.0' encoding='UTF-8'?> will cause a crash
               #lxml.etree.XMLSyntaxError: XML declaration allowed only at the start of the document, line 1, column 103
               else:
               	  try:
                   		self.tree = etree.parse(StringIO.StringIO(unescape(document.toxml(),entities={"&quot;":"'"})),parser) # Not very efficient, the XML is converted to string and then back again to XML
                  except:
                  		document=doCleanBug5762(document)  
                  		self.tree = etree.parse(StringIO.StringIO(unescape(document.toxml(),entities={"&quot;":"'"})),parser)
            except etree.XMLSyntaxError,e: # Generic parsing error
                 raise pywps.NoApplicableCode(e.message)
            
            
            self.root=self.tree.getroot()
           
            #Searching of a Envelope element (case sensitive)
            self.envElement=self.root.xpath("//*[contains(local-name(),'Envelope')]") #It actually retunrs the node

            #Check for SOAP name space
            self.nameSpaceSet=set(self.root.nsmap.values()) & set(soap_env_NS)
            self.nsIndex = soap_env_NS.index(self.nameSpaceSet.pop())
            if (self.nsIndex==1):
            	self.soapVersion=11
            else:
            	self.soapVersion=12
            
            #Check for ExecuteProcess
          
            self.isSoapExecute=bool(self.root.xpath("//*[contains(local-name(),'ExecuteProcess')]")) # just to be certain that is a bool
           

            
    def getWPSContent(self):
    	    """Get the specific WPS XML content of inside the SOAP request. The Element position may change if there is a SOAP header or if is was sent as a message inside the Body content
    	    The script will check for a standard WPS request or a ExecuteProcess_ one"""   
	   
       
            reqWPS=self.root.xpath("//*[local-name() = 'GetCapabilities' or local-name()='DescribeProcess' or local-name()='Execute' or contains(local-name(),'ExecuteProcess_') or contains(local-name(),'ExecuteProcessAsync_')] ")
            if bool(reqWPS):
             #General WPS:
           #print reqWPS[0].tag #getting the element's name
                if "ExecuteProcess" in reqWPS[0].tag:
                   XMLStr=SOAPtoWPS(reqWPS[0])
                   XMLDoc=minidom.parseString(XMLStr)
            	  
                   return getFirstChildNode(XMLDoc)
        
        
    #GetCapabilites/DescribeProcess or Execute
    #getCapabilities=root.xpath("//*[local-name() = 'GetCapabilities' or local-name()='DescribeProcess']")
                else:
                   #Normal WPS
                   reqWPS=doFixTavernaBug(reqWPS[0])
                   XMLDoc = minidom.parseString(etree.tostring(reqWPS))
                   return getFirstChildNode(XMLDoc)

            else: #if bool(reqWPS)
                raise  pywps.NoApplicableCode("Could not deternine the WPS request type from SOAP envelope. Couldnt determine GetCapabilities/DescribeProcess/Execute/ExecuteProcess_ from XML content")


    def getSOAPVersion(self):
		return self.soapVersion
	
    def getSoapExecute(self):
		return self.isSoapExecute


    def doSOAPFault(self,exceptionReportTree,soapVersion):
    	#Assumed standard Execption document
    	
    	
        if (int(soapVersion)==11):#
        	SOAP_ENVELOPE_FAULT=SOAP_ENVELOPE_FAULT11
        else:
        	SOAP_ENVELOPE_FAULT=SOAP_ENVELOPE_FAULT12
        	
        soapFaultResponse=SOAP_ENVELOPE_FAULT.replace('$REPORTEXCEPTION$',etree.tostring(exceptionReportTree))
       
        	
        exceptionTree=exceptionReportTree.xpath("//*[local-name() = 'Exception']")
        exceptionStr=etree.tostring(exceptionTree[0])
        exceptionStr="<![CDATA["+exceptionStr+"]]>"
       
        return soapFaultResponse.replace('$REPORT$',exceptionStr)
        	
   	 
        	

    def getResponse(self,document,soapVersion,isSoapExecute,isPromoteStatus):
        """Wrap document into soap envelope"""
        # very primitive, but works
        #SOAP 1.1 Content-type: text/xml
        # SOAP 1.2   Content-Type: application/xml maybe application/soap ?!
        
        document = document.__str__().replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>","")
        
        #sometime there is some binary trash in the stream (e.g. r.fillnulls) and we
        #set the parser to try to fix it
	    #http://papeltank.blogspot.com/2010/12/lxmletreexmlsyntaxerror-pcdata-invalid.html      
        documentTree=etree.parse(StringIO.StringIO(document), etree.XMLParser(ns_clean=True, recover=True))
        root=documentTree.getroot()
        # #Check if it's a isSoapFault
        exceptionReportTree=root.xpath("//*[local-name() = 'ExceptionReport']")
        if bool(exceptionReportTree):
        	exceptionReportTree=exceptionReportTree[0] #getting the tree from list
        	isSoapFaul=True
        else:
        	isSoapFaul=False
        	
        #Check if it is a status response: in this case we juist output this with soap envelope
        #if we have processAccepted we will only pass the result, otherwise the WPS with soap 
        #import traceback
        #f1=open("/tmp/tmp.xml","w")
        #traceback.print_stack(file=f1)
       
        #and not bool(isAsync)
        if (isSoapExecute and not bool(isPromoteStatus)):
        	
        	WPSTree=documentTree
        	#it continues as a normal document 	
       	 	document=WPStoSOAP(WPSTree)
       	 	      		
       #normal response if not SOAP Fault
        if not isSoapFaul:
           
           if (int(soapVersion)==11):
         		return SOAP_ENVELOPE11.replace("$SOAPBODY$",document)
           else:
        		return SOAP_ENVELOPE12.replace("$SOAPBODY$",document)
        else: #ERROR FAULT
        	
        	return self.doSOAPFault(exceptionReportTree,soapVersion)
        
	
