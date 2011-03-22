import os
import sys
import cStringIO
import StringIO

import time
import signal
pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))

#sys.path.append(pywpsPath)
sys.path[0]=pywpsPath
sys.path.append("/users/blue_rsghome/jmdj/.eclipse/793567567/plugins/org.python.pydev.debug_1.6.0.2010071813/pysrc/")
import pywps
import pywps.Process
#from  pywps.Parser import Post
import unittest
from pywps.Parser import Post

from xml.dom import minidom
from xml.dom.ext import c14n
from pywps import Soap
import types
from pywps.Exceptions import *

#Note the postpywps.response should be an WSP response without SOAP envelope
 #SOAP envelope is then added in soap.getResponse that is called from response() accordinf the soap needs

#Note2: incorrect SOAP envelope posting is normally due to incorrect/bad order function arguments
#def response(response,targets,soapVersion=None,isSoap=False,isSoapExecute=False,contentType="application/xml"):

#Stolen from Parser.Post.getFirstChildNode()
def getFirstChildNode(document):
    for node in document.childNodes:
        if node.nodeType == minidom.Element.nodeType:
            firstChild = node
        
    document=firstChild
    return document


class SOAPTestCase(unittest.TestCase):
    """Test case that checks if SOAP is properly working, detection of SOAP, getting envelope content, version detection, SOAPpy parsing and creationf of SOAPpy.Types.structType """
   #def __init__(self):
    #    pass
    soapVersion=None
    

    
    def setUp(self):
        pass
    
    #def testIsSOAP(self):
    #    """Testing SOAP detection, wps.parser.isSoap"""
        #postpywps = pywps.Pywps(pywps.METHOD_POST)
    #    getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11.xml"))
    #    document = minidom.parse(getCapabilitiesSOAP11RequestFile)

        #Stolen from Parser.Post.getFirstChildNode()
    #    for node in document.childNodes:
    #        if node.nodeType == minidom.Element.nodeType:
     #           firstChild = node
    #    
      #  document=getFirstChildNode(document)
       # self.assertTrue(Soap.isSoap(document))
        

    def testGetWPSGetCapabilitiesContent(self):
        """Testing if GetCapabilties can be fetch from SOAP envelope""" 
        getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11.xml"))
        getCapabilitiesRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request.xml"))
        
        SOAPRequestDoc=minidom.parse(getCapabilitiesSOAP11RequestFile)
        getCapabilitiesRequestDoc=minidom.parse(getCapabilitiesRequestFile) 
        
        SOAPRequestDoc=getFirstChildNode(SOAPRequestDoc)
     
        testSOAP=Soap.SOAP(SOAPRequestDoc)
        outputDoc=testSOAP.getWPSContent()
        
        SOAPTestCase.soapVersion=testSOAP.getSOAPVersion()
        
        self.assert_((outputDoc.__class__.__name__=='Element'), 'Output from Soap.getWPSContent() is not a DOM-Element')
 
        
         #Checking if both arguments are dom objects, using assert technique (if  false things will stop)
        #self.assert_((xml1.__class__.__name__=='Document'), 'First argument is not an XML Document')
        outputDoc=minidom.parseString(outputDoc.toxml())
        xml1Cano,xml2Cano=c14n.Canonicalize(getCapabilitiesRequestDoc), c14n.Canonicalize(outputDoc)
        self.assertTrue(str(xml1Cano)==str(xml2Cano))
    
    def testSOAPVersionResponse(self):
        """Testing the correct version reply"""
        getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11.xml"))
        mypywps = pywps.Pywps(pywps.METHOD_POST)
        inputs= mypywps.parseRequest(getCapabilitiesSOAP11RequestFile)
        response=mypywps.performRequest(inputs)
        
        soapTest=Soap.SOAP()
        soapResponse=soapTest.getResponse(response,self.soapVersion)
      
 
        #s = StdOut(sys.stdout)
        #sys.stdout = s
        
        #redirecting stdout
        #import cStringIO
        #dummyIO=StringIO.StringIO()
        #sys.stdout=dummyIO=StringIO.StringIO()
        #sys.stderr=dummyIO
        
        #pywps.response.response(response,sys.stdout,mypywps.parser.soapVersion,mypywps.parser.isSoap,mypywps.request.contentType)
        #print dir(dummyIO)
        #response = soap.getResponse(response,soapVersion=11)
        #sys.stdout=sys.__stdout__
        #'sys.stderr=sys.__stderr__
        #print dummyIO.len
        #print (dummyIO.getvalue())
        
        #print dummyIO.getvalue()
        #sys.stderr = sys.__stderr__ 
        #print dummyIO.read()
        #print responseSOAP
        #Check if string contains "SOAP-ENV:Envelope"
        self.assertTrue("soap-env:envelope" in soapResponse.lower())
        #Check if string contains "SOAP-ENV:Envelope"
        
        
        
        #xmldom = minidom.parseString(mypywps.response)
        #print xmldom.toxml()
        
    def testSOAPSocket(self):
        pass
  
  
  
class SOAPSchemaTestCase(unittest.TestCase):
    #For soap 1.2 -->http://www.w3.org/2003/05/soap-envelope (self.nsIndex=0)
    #For soap 1.1 -->http://schemas.xmlsoap.org/soap/envelope/ (self.nsIndex=1)
    soapEnvNS = ["http://www.w3.org/2003/05/soap-envelope","http://schemas.xmlsoap.org/soap/envelope/"]
    soapEncNS = ["http://www.w3.org/2003/05/soap-encoding","http://schemas.xmlsoap.org/soap/encoding/"]
    
    wpsns="http://www.opengis.net/wps/1.0.0"
    owsns="http://www.opengis.net/ows/1.1"
    
    def setUp(self):
        sys.stderr=open("/dev/null","w")
    
    def testIsSOAP(self):
        """Testing SOAP detection, wps.parser.isSoap"""
        #Test using getCapabilities
        
        self._setFromEnv()
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11.xml"))
        postpywps.parseRequest(getCapabilitiesSOAP11RequestFile)
        self.assertTrue(postpywps.parser.isSoap)
        
        getCapabilitiesSOAP12RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP12.xml"))
        postpywps.parseRequest(getCapabilitiesSOAP12RequestFile)#
        self.assertTrue(postpywps.parser.isSoap)
        
        #NonSOAP content
        getCapabilitiesRequestFile=open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request.xml"))
        postpywps.parseRequest(getCapabilitiesRequestFile)#
        
        self.assertFalse(postpywps.parser.isSoap)
        
    
    def testSOAPVersion(self):
        """Testing correct wps.parser.soapVersion"""
        self._setFromEnv()
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11.xml"))
        postpywps.parseRequest(getCapabilitiesSOAP11RequestFile)
        self.assertEqual(int(postpywps.parser.soapVersion), int(11))
        
        getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP12.xml"))
        postpywps.parseRequest(getCapabilitiesSOAP11RequestFile)
        self.assertEqual(int(postpywps.parser.soapVersion), int(12))
        
        #Non soap
        getCapabilitiesRequestFile=open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request.xml"))
        postpywps.parseRequest(getCapabilitiesRequestFile)#
        self.assertTrue(type(postpywps.parser.soapVersion) is types.NoneType)
        
    def testSOAPExecute(self):
        """Testing Execute SOAP postpywps.parser.isSoapExecute"""
        self._setFromEnv()
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeSOAPRequestFile=open(os.path.join(pywpsPath,"tests","requests","wps_execute_request_compress_SOAP.xml"))
        postpywps.parseRequest(executeSOAPRequestFile)#
        self.assertTrue(postpywps.parser.isSoapExecute)
        
        postpywps.performRequest()
        
        soap = Soap.SOAP()
        response = soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute) 
        
        xmldom=minidom.parseString(response)
        self.assertTrue(xmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
        self.assertTrue(xmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
        self.assertTrue(xmldom.getElementsByTagName("output2Result")>1)
        self.assertTrue(xmldom.getElementsByTagName("output1Result")>1)
                  
    def testGetCapabilities(self):
        """Testing a complete getCapabilities using SOAP1.1"""
        
        #tmp.xml:2: element Envelope: Schemas validity error : 
        #Element '{http://schemas.xmlsoap.org/soap/envelope/}Envelope', attribute 
        #'{http://schemas.xmlsoap.org/soap/envelope/}encodingStyle': The attribute 
        #'{http://schemas.xmlsoap.org/soap/envelope/}encodingStyle' is not allowed.
        
        self._setFromEnv()
      
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11.xml"))
        postpywps.parseRequest(getCapabilitiesSOAP11RequestFile)
         
        postpywps.performRequest()
        
        
        soap = Soap.SOAP()
        response = soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute) 
        
        #Check SOAP content in response
        postxmldom = minidom.parseString(response)
        self.assertTrue(postxmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
        self.assertTrue(postxmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
        
    def testDescribeProcess(self):
         """Testing a complete describeProcess using SOAP1.1"""
        
         self._setFromEnv()
         postpywps = pywps.Pywps(pywps.METHOD_POST)
         describeSOAPRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_request_all_SOAP.xml"))
         
         postpywps.parseRequest(describeSOAPRequestFile)
         postpywps.performRequest()
         xmldoc=minidom.parseString(postpywps.response)
         
         self.assertTrue(xmldoc.getElementsByTagNameNS(self.wpsns,"ProcessDescriptions")>0)
    
    def testAsyncProcess(self):
        """Testing SOAP env in asycn req with normal document"""
        self._setFromEnv()
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        
        pid=os.getpid()
        
        executeSOAPRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request_ultimatequestion_SOAP.xml"))
        postpywps.parseRequest(executeSOAPRequestFile)
        postpywps.performRequest()
        
        if (os.getpid() != pid):
            os._exit(0)
        soap = Soap.SOAP()
        response = soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute)
        
        #Check SOAP content in response
        postxmldom = minidom.parseString(response)
        self.assertTrue(postxmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
        self.assertTrue(postxmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
        
        #Get status content
        executeEl=postxmldom.getElementsByTagNameNS("http://www.opengis.net/wps/1.0.0","ExecuteResponse")
        fileName=os.path.basename(executeEl[0].getAttribute("statusLocation"))
        filePath=pywps.config.getConfigValue("server","outputPath")+"/"+fileName
        
        #check that the status file also has a SOAP envelope
        time.sleep(2)
        statusDoc = minidom.parse(filePath) 
        self.assertTrue(statusDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
        self.assertTrue(statusDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
        
        
    def testAsyncCompressExecute(self):
        """Testing async req from compressed SOAP"""
        #os.fork make the unittest fork, being called again when the process finishes
        #in the first run the unittest will get the statusURLResult, in the second run it will parse the 
        #response content with answerResult
        
        
        self._setFromEnv()
        pid=os.getpid()
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeSOAPRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request_ultimate_compress_SOAP.xml"))
        
        postpywps.parseRequest(executeSOAPRequestFile)
        postpywps.performRequest()
        soap = Soap.SOAP()
        response=soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute)
        
        #Check SOAP content in response
        responseDoc = minidom.parseString(response)
        self.assertTrue(responseDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
        self.assertTrue(responseDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
        #print os.getpid()
        #GetStatus from <statusURLResult>
        time.sleep(2)        
        #Killing the child from os.fork in pywps
        if (os.getpid() != pid):
            os._exit(0)
        
        statusEl=responseDoc.getElementsByTagName("statusURLResult")
        
        fileName=os.path.basename(statusEl[0].firstChild.toxml())
        filePath=pywps.config.getConfigValue("server","outputPath")+"/"+fileName
        
        #check that the status file also has a SOAP envelope
    
        statusDoc = minidom.parse(filePath) 
        self.assertTrue(statusDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
        self.assertTrue(statusDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
        
    def testWSDLGenerator(self):
        """Testing WSDL generation"""
        #Major testing in the ultimatequestion process
        self._setFromEnv()
            
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        inputs=getpywps.parseRequest("WSDL")
        #print inputs
        getpywps.performRequest()
     
        #print pywps.config.getConfigValue("wps","serveraddress")
            
        wsdlDoc = minidom.parseString(getpywps.response)
        #checking content  
        addressNode=wsdlDoc.getElementsByTagName("address")[0]
        #check 4 correct server adress
        self.assertTrue(addressNode.getAttribute("location")==pywps.config.getConfigValue("wps","serveraddress"))
            
        #check for Response/Request in input/output message
        port=wsdlDoc.getElementsByTagName("portType")
        inputs=port[0].getElementsByTagName("input")
        outputs=port[0].getElementsByTagName("output")
        self.assertTrue("Request" in inputs[0].getAttribute("message"))
        self.assertTrue("Response" in outputs[0].getAttribute("message"))
            
        #check for async+sync creation
        operation=port[0].getElementsByTagName("operation")
        self.assertTrue("ExecuteProcessAsync_ultimatequestionprocess" in [item.getAttribute("name") for item in operation])
        self.assertTrue("ExecuteProcess_ultimatequestionprocess" in [item.getAttribute("name") for item in operation])
        self.assertFalse("ExecuteProcessAsync_literalprocess" in [item.getAttribute("name") for item in operation])
            
        #probably more WSDL content tests are necessary
            
            
            
    def testFaultSOAP(self):
        "Testing WPS exception to SOAP fault"
        #here a silent stderr does not work, the exception is raised and a try will catch it
        self._setFromEnv()
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        exceptionFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_exception_SOAP.xml"))    
        postpywps.parseRequest(exceptionFile)
        try:
            postpywps.performRequest()
        except InvalidParameterValue,e:
            postpywps.response=e.getResponse()

        soap = Soap.SOAP()
        response=soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute)
        xmlDoc=minidom.parseString(response)
        xmlDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Fault")
        self.assertTrue(len(xmlDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Fault"))>0)
        #check for SOAP-ENV:Server as fault code as in WCS2.0
        self.assertTrue(len(xmlDoc.getElementsByTagName("faultcode"))>0)
        exceptionDoc=xmlDoc.getElementsByTagName("detail")[0]
        self.assertTrue(len(exceptionDoc.getElementsByTagNameNS(self.owsns,"ExceptionReport"))>0)
        
    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
        #Necessary for the WSDL test
        os.putenv("PYWPS_CFG", os.path.join(pywpsPath,"pywps","default"))
        os.environ["PYWPS_CFG"] = os.path.join(pywpsPath,"pywps","default.cfg")
      
    
if __name__ == "__main__":
     # unittest.main()
   suite = unittest.TestLoader().loadTestsFromTestCase(SOAPSchemaTestCase)
   unittest.TextTestRunner(verbosity=2).run(suite)