import os
import sys
import cStringIO
import StringIO

import warnings
warnings.filterwarnings("ignore")

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.append(pywpsPath)

import pywps
import pywps.Process
#from  pywps.Parser import Post
import unittest
from pywps.Parser import Post

from xml.dom import minidom
from xml.dom.ext import c14n
from pywps import Soap

class StdOut(StringIO.StringIO):
     def __init__(self,stdout):
         self.__stdout = stdout
         StringIO.StringIO.__init__(self)

     def write(self,s):
         self.__stdout.write(s)
         StringIO.StringIO.write(self,s)

     def read(self):
         self.seek(0)
         self.__stdout.write(StringIO.StringIO.read(self))





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
    
    def testIsSOAP(self):
        """Testing SOAP detection, wps.parser.isSoap"""
        #postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11.xml"))
        document = minidom.parse(getCapabilitiesSOAP11RequestFile)

        #Stolen from Parser.Post.getFirstChildNode()
        for node in document.childNodes:
            if node.nodeType == minidom.Element.nodeType:
                firstChild = node
        
        document=getFirstChildNode(document)
        self.assertTrue(Soap.isSoap(document))
        

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
        inputs = mypywps.parseRequest(getCapabilitiesSOAP11RequestFile)
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
  
  
  
 #  wps = pywps.Pywps(method)
  #  if wps.parseRequest(inputQuery):
   #     pywps.debug(wps.inputs)
    #    response = wps.performRequest()

        # request performed, write the response back
     #   if response:
            # print only to standard out
      #      pywps.response.response(wps.response,
        #            sys.stdout,wps.parser.soapVersion,wps.parser.isSoap,
       #             wps.request.contentType)
if __name__ == "__main__":
    unittest.main()
  
  
  
  
        