import os
import sys
import cStringIO
import StringIO

import time
import signal
pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
#sys.path.append(pywpsPath)
sys.path.insert(0,pywpsPath)
import pywps
import pywps.Process

import unittest
from pywps.Parser import Post
from xml.dom import minidom
from pywps import Soap
import types

#Note the postpywps.response should be an WSP response without SOAP envelope
#SOAP envelope is then added in soap.getResponse that is called from response() accordinf the soap needs

#Note2: incorrect SOAP envelope posting is normally due to incorrect/bad order function arguments
#def response(response,targets,soapVersion=None,isSoap=False,isSoapExecute=False,contentType="application/xml"):

  
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
       response = soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False) 
       
       xmldom=minidom.parseString(response)
       self.assertTrue(xmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
       self.assertTrue(xmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
       self.assertTrue(xmldom.getElementsByTagName("output2Result")>1)
       self.assertTrue(xmldom.getElementsByTagName("output1Result")>1)
                 
    def testGetCapabilitiesXML(self):
       """Testing a complete getCapabilities using SOAP1.1, based on WPS XMl content"""
       
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
       response = soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False) 
       
       #Check SOAP content in response
       postxmldom = minidom.parseString(response)
       self.assertTrue(postxmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
       self.assertTrue(postxmldom.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
       
    def testGetCapabilitiesRPC(self):
       """Testing a complete getCapabilities using SOAP1.1, using RPC"""
       #SUDS SOAP client  https://fedorahosted.org/suds/
       self._setFromEnv()
       postpywps=pywps.Pywps(pywps.METHOD_POST)
       getCapabilitiesRPC=open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11RPC.xml"))
       postpywps.parseRequest(getCapabilitiesRPC)
       postpywps.performRequest()
       xmldoc=minidom.parseString(postpywps.response)
       #no need to generate soap response, just testing to get the getCapabilities document
       self.assertTrue(xmldoc.getElementsByTagNameNS(self.wpsns,"Capabilities")>0)
       #using some alternative version number
       getCapabilitiesRPC.seek(0)
       doc=minidom.parse(getCapabilitiesRPC)
       doc.getElementsByTagNameNS(self.owsns,'Version')[0].firstChild.nodeValue="3.0.0"
       try:
           postpywps.parseRequest(StringIO.StringIO(doc.toxml()))
       #<Exception exceptionCode="VersionNegotiationFailed">
       except Exception as e:
           self.assertTrue("VersionNegotiationFailed" in e.code) 
           
    def testDescribeProcessRPC(self):
        """Testing a complete describeProcess using SOAP1.1, using RPC"""
        #Note in RPC DescribeProcess is as follows
        #DescribeProcess(ns0:CodeType[] Identifier, )
        #This CodeType is not the best defintion 
        #<ns1:Body><ns0:DescribeProcess><ns0:Identifier xsi:type="ns2:CodeType">ultimatequestionprocess</ns0:Identifier></ns0:DescribeProcess></ns1:Body>
        self._setFromEnv()
        postpywps=pywps.Pywps(pywps.METHOD_POST)
        describeProcessRPC=open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_request_SOAP11RPC.xml"))
        postpywps.parseRequest(describeProcessRPC)
        postpywps.performRequest()
        xmldoc=minidom.parseString(postpywps.response)
        self.assertTrue(xmldoc.getElementsByTagNameNS(self.wpsns,"ProcessDescriptions")>0)
        
        
    def testDescribeProcessXML(self):
         """Testing a complete describeProcess using SOAP1.1 based on WPS XML content"""
        
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
        response = soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False)
        
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
        response=soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False)
        
        #Check SOAP content in response
        responseDoc = minidom.parseString(response)
        
        #GetStatus from <statusURLResult>
        time.sleep(2)        
        #Killing the child from os.fork in pywps
        if (os.getpid() != pid):
            os._exit(0)
        
        
        self.assertTrue(responseDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
        self.assertTrue(responseDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
        
        statusEl=responseDoc.getElementsByTagName("statusURLResult")
        #Check that the statusURLResult is present (compressed soap)
        self.assertTrue(len(statusEl)>0)
        
        fileName=os.path.basename(statusEl[0].firstChild.toxml())
        filePath=pywps.config.getConfigValue("server","outputPath")+"/"+fileName
        
        #check that the new status file also has a SOAP envelope
        statusDoc = minidom.parse(filePath) 
        self.assertTrue(statusDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Envelope")>0)
        self.assertTrue(statusDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Body")>0)
        self.assertTrue(statusDoc.getElementsByTagNameNS(self.wpsns,"ExecuteResponse")>0)
        
        #loop until we have a result
        counter=0
        while counter<20:
            statusDoc = minidom.parse(filePath) 
            executeEl=statusDoc.getElementsByTagNameNS(self.wpsns,"ExecuteResponse")
            if len(executeEl) > 0: 
                counter=counter+1
                time.sleep(5)
            else:
                break
        if counter>=20:
            self.fail("The assync process it taking to long, something is wrong")
        
        #result should be in compressed SOAP
        resultDoc=minidom.parse(filePath)
        
        self.assertTrue(len(resultDoc.getElementsByTagName("answerResult"))>0)
        self.assertEqual(int(resultDoc.getElementsByTagName("answerResult")[0].firstChild.nodeValue),42)
        print resultDoc.getElementsByTagName("answerResult")[0].firstChild.nodeValue
        
        
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
        self.assertTrue("ExecuteProcessAsync_literalprocess" in [item.getAttribute("name") for item in operation])
        #probably more WSDL content tests are necessary
            
    def testSOAP11Fault(self):
        "Testing WPS exception to SOAP11 fault"
        #here a silent stderr does not work, the exception is raised and a try will catch it
        self._setFromEnv()
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        exceptionFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_exception_SOAP11.xml"))    
        postpywps.parseRequest(exceptionFile)
        try:
            postpywps.performRequest()
        except pywps.Exceptions.InvalidParameterValue,e:
            postpywps.response=e.getResponse()
 
        soap = Soap.SOAP()
        response=soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False)
        xmlDoc=minidom.parseString(response)
        #xmlDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Fault")
        self.assertTrue(len(xmlDoc.getElementsByTagNameNS(self.soapEnvNS[1],"Fault"))>0)
        #check for SOAP-ENV:Server as fault code as in WCS2.0
        self.assertTrue(len(xmlDoc.getElementsByTagName("faultcode"))>0)
        exceptionDoc=xmlDoc.getElementsByTagName("detail")[0]
        self.assertTrue(len(exceptionDoc.getElementsByTagNameNS(self.owsns,"ExceptionReport"))>0)
        
        
    def testSOAP12Fault(self):
        "Testing WPS exception to SOAP12 fault"
        
        self._setFromEnv()
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        exceptionFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_exception_SOAP12.xml"))    
        postpywps.parseRequest(exceptionFile)
        try:
            postpywps.performRequest()
        except pywps.Exceptions.InvalidParameterValue,e:
            postpywps.response=e.getResponse()
 
        soap = Soap.SOAP()
        response=soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False)
        xmlDoc=minidom.parseString(response)
        
        self.assertTrue(len(xmlDoc.getElementsByTagNameNS(self.soapEnvNS[0],"Fault"))>0)
        #check for SOAP-ENV:Server as fault code as in WCS2.0
        self.assertTrue(len(xmlDoc.getElementsByTagNameNS(self.soapEnvNS[0],"Value"))>0)
        exceptionDoc=xmlDoc.getElementsByTagNameNS(self.soapEnvNS[0],"Detail")[0]
        self.assertTrue(len(exceptionDoc.getElementsByTagNameNS(self.owsns,"ExceptionReport"))>0)        
        
    def testWSDLStartChar(self):
        """Testing the flag removal from I/O (WSDL)"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        getpywps.parseRequest("WSDL")
    
        getpywps.performRequest()     
        wsdlDoc = minidom.parseString(getpywps.response)
        #getting all schema elements
        schemaEl=wsdlDoc.getElementsByTagName("schema")
        #getting all nodes called elements
        elementEl=[node.firstChild for node in schemaEl if node.firstChild.localName=="element"]
        #filter everython so that elements that contain the flag process are picked
        flagEl=[node.firstChild for node in elementEl if "flag" in node.getAttributeNode("name").nodeValue]
        #secon element fetch this time elements inside process
        element2El=[node.getElementsByTagName("element") for node in flagEl]
        #flatting the list
        element2El=[item2 for item1 in element2El for item2 in item1]
        #list of strings
        names=[node.getAttributeNode("name").nodeValue for node in element2El]
        #check for presence of "-"
        self.assertTrue(len([name for name in names if "-" in name])==0)
    
    def testIOmappingSOAP(self):
        """Test correct mapping of I/O identifier from SOAP compress to WPS"""
        #This is related to the start char problem, the SOAP flag1 need to be 
        # --flag1
        postpywps = pywps.Pywps(pywps.METHOD_POST) 
        executeSOAPRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request_flags_compress_SOAP.xml")) 
        postpywps.parseRequest(executeSOAPRequestFile)
        
        #Need to check the SOAP-->WPS convertion
        inputsList=postpywps.inputs["datainputs"]
        textIdentifier=[dic["identifier"] for dic in inputsList]
        self.assertTrue("-flag1In" in textIdentifier)
        self.assertTrue("--flag2In" in textIdentifier)
        
        postpywps.performRequest()
        
        xmlDoc=minidom.parseString(postpywps.response)
        identifierEl=xmlDoc.getElementsByTagNameNS(self.owsns,"Identifier")
        textIdentifier=[item.firstChild.nodeValue for item in identifierEl]
        self.assertTrue("-flag1Out" in textIdentifier)
        self.assertTrue("--flag2Out" in textIdentifier)
        
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