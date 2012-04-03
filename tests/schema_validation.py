import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
#sys.path.append(pywpsPath)
sys.path.insert(0,pywpsPath)
import pywps
import pywps.Process
import unittest
import time

from lxml import etree
import urllib
import StringIO
from pywps import Soap


if os.name != "java":
    from osgeo import ogr
else:
    os.putenv("PYWPS_CFG", os.path.join(pywpsPath,"pywps","default"))
    os.environ["PYWPS_CFG"] = os.path.join(pywpsPath,"pywps","default.cfg")
    os.putenv("PYWPS_TEMPLATES", os.path.join(pywpsPath,"tests","Templates"))
    os.environ["PYWPS_TEMPLATES"] = os.path.join(pywpsPath,"tests","Templates")
    os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
    os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")


class SchemaTestCase(unittest.TestCase):
   #The class takes some time to load since it's in here where the schema objects are created and the schema's URL contacted
   
    getCapabilitiesRequest = "service=wps&request=getcapabilities"
    getDescribeProcessRequest = "service=wps&request=describeprocess&version=1.0.0&identifier=bboxprocess,complexprocess,literalprocess,complexRaster,complexVector,ogrbuffer"
    
    postExecuteBBOXRequest=open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-bbox.xml"))
    #1 raster + 1 vector output No def of response doc
    postExecuteComplexInputRequest=open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-direct.xml"))
    postExecuteComplexInputOneOutputRequest=open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-one-output-as-reference.xml"))
    
    postExecuteLiteraDataRequest=open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-literalinput-responsedocument.xml"))
    
    base_url="http://schemas.opengis.net/wps/1.0.0/"
    
    getCapabilitiesSchemaResponse="http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd"
    describeProcessSchemaResponse="http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd"
    executeSchemaResponse="http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd"
    wsdlSchema="http://schemas.xmlsoap.org/wsdl/"
    soap11Schema="http://schemas.xmlsoap.org/soap/envelope/"
    soap12Schema="http://www.w3.org/2003/05/soap-envelope/"
     
    parser=etree.XMLParser(no_network=False)

    def setUp(self):
        #Silence PyWPS Warning: Usage of....
        sys.stderr=open("/dev/null","w")
    
    def testStatusLocation(self):
        """Test, status=false, storeexecuteresposne=false, statusLocation
        file should NOT be empty"""
        self._setFromEnv()
        
        schemaDocExecute=etree.XML(urllib.urlopen(self.executeSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaExecute=etree.XMLSchema(schemaDocExecute)
        
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest("service=wps&request=execute&version=1.0.0&identifier=ultimatequestionprocess&status=false&storeExecuteResponse=true")
        mypywps.performRequest()
        
        #First parse
        executeAssyncGET=etree.XML(mypywps.response,self.parser)
        self.assertEquals(schemaExecute.assertValid(executeAssyncGET),None)
        #get path to status document
        fileName=os.path.basename(executeAssyncGET.xpath("//*[local-name()='ExecuteResponse']/@statusLocation")[0])
        filePath=pywps.config.getConfigValue("server","outputPath")+"/"+fileName
        self.assertEquals(True,os.path.exists(filePath))
        fileOpen = open(filePath)
        
        self.assertEquals(fileOpen.read(), mypywps.response)

    def testAssync(self):
        """Test assync status document"""
        
        self._setFromEnv()
        pid=os.getpid()
        schemaDocExecute=etree.XML(urllib.urlopen(self.executeSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaExecute=etree.XMLSchema(schemaDocExecute)
        
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest("service=wps&request=execute&version=1.0.0&identifier=ultimatequestionprocess&status=true&storeExecuteResponse=true")
        mypywps.performRequest()
        #Killing the child from os.fork in pywps
        if (os.getpid() != pid):
            os._exit(0)
        
        #First parse
        executeAssyncGET=etree.XML(mypywps.response,self.parser)
        self.assertEquals(schemaExecute.assertValid(executeAssyncGET),None)
        
        #get path to status document
        fileName=os.path.basename(executeAssyncGET.xpath("//*[local-name()='ExecuteResponse']/@statusLocation")[0])
        filePath=pywps.config.getConfigValue("server","outputPath")+"/"+fileName
        
        time.sleep(2)
        executeAssyncStatus=etree.parse(open(filePath,"r"),parser=self.parser)
        self.assertEquals(schemaExecute.assertValid(executeAssyncStatus),None)
        
        #Looping waiting for ProcessSucceeded
        #will loop max 20 times and wait 5 sec
        #if the assync is taking to long it mught be a problem
        counter=0
       
        while counter<20:
            executeAssyncStatus=etree.parse(open(filePath,"r"),parser=self.parser)
            processStatus=executeAssyncStatus.xpath("//*[local-name()='ProcessAccepted' or local-name()='ProcessStarted' or local-name()='ProcessPaused']")
            self.assertEquals(schemaExecute.assertValid(executeAssyncStatus),None)
            if len(processStatus) > 0:
                counter=counter+1
                time.sleep(5)
            else:
                break
        if counter>=20:
            self.assertEquals("The assync process is taking to long",None)
 
    def testGetCapabilities(self):
        """Test if GetCapabilities request returns a valid XML document"""
        #Note:schemaGetCapabilities.assertValid(getCapabilitiesDoc)
        # will dump the location of the error, schemaGetCapabilities.validate(getCapabilitiesDoc)
        #will give true or false
        
        #Note2:Setting the Process class constructor (Process/__init__.py) without a default processVersion value
        # def __init__(self, identifier,...,profile=[],version=None,...): 
        # Will make the parser to invalidate the request, this is a ways to test if the parser is working ok
        #DocumentInvalid: Element '{http://www.opengis.net/wps/1.0.0}Process': The attribute '{http://www.opengis.net/wps/1.0.0}processVersion' is required but missing., line 74
        
        #Note3: complexVector has mimeTypes None (application/x-empty)
        
        
        self._setFromEnv()
        schemaDocGetCap=etree.XML(urllib.urlopen(self.getCapabilitiesSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaGetCapabilities=etree.XMLSchema(schemaDocGetCap)
          
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        getinputs=getpywps.parseRequest(self.getCapabilitiesRequest)
    
        getpywps.performRequest(getinputs)
        getCapabilitiesGET=etree.XML(getpywps.response,self.parser)
       
        #Validate GET response
        self.assertEquals(schemaGetCapabilities.assertValid(getCapabilitiesGET),None)
        
        #POST request should be the same, since the response is generated from the same inputs
        # But you never know....
        #postpywps = pywps.Pywps(pywps.METHOD_POST)
       
        #postinputs = postpywps.parseRequest(self.getCapabilitiesRequestFile)
        #postpywps.performRequest(postinputs)
        #getCapabilitiesPOST=etree.XML(postpywps.response,self.parser)
        #self.assertEquals(schemaGetCapabilities.assertValid(getCapabilitiesPOST),None)
        
        
    def testDescribeProcess(self):
        """Test if DescribeProcess requests returns a valid XML document"""
        #Note: assyncprocess fails since it has no outputs and outputs
        
        #Note2:Processes that miss format list (formats) ex: complexVector will have <MimeType>None></MimeType>
        #element MimeType: Schemas validity error : Element 'MimeType': [facet 'pattern']
        # The value 'None' is not accepted by the pattern '(application|audio|image|text|video|message|multipart|model)/.+(;\s*.+=.+)*'
        
        #Note3: processes ok: bboxprocess,complexprocess,literalprocess,complexRaster
        
        self._setFromEnv()
        
        schemaDocDescribe=etree.XML(urllib.urlopen(self.describeProcessSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaDescribeProcess=etree.XMLSchema(schemaDocDescribe)
    
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        getinputs = getpywps.parseRequest(self.getDescribeProcessRequest)
        getpywps.performRequest(getinputs)
     
        describeProcessGET=etree.XML(getpywps.response,self.parser)
        self.assertEquals(schemaDescribeProcess.assertValid(describeProcessGET),None)
        
 
    def testExecuteBBOXProcess(self):
        """Test execute with bbox"""
        
        self._setFromEnv()
        
        schemaDocExecute=etree.XML(urllib.urlopen(self.executeSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaExecute=etree.XMLSchema(schemaDocExecute)
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        postinputs = postpywps.parseRequest(self.postExecuteBBOXRequest)
        self.postExecuteBBOXRequest.seek(0)
        postpywps.performRequest(postinputs)
        executeBBOXPOST=etree.XML(postpywps.response,self.parser)
        self.assertEquals(schemaExecute.assertValid(executeBBOXPOST),None)
 
    def testExecuteComplexInputDirect(self):
        """Test standard Execute direct output of raster and vector"""
        #wps_execute_request-complexinput-direct.xml
        
        self._setFromEnv()
        
        schemaDocExecute=etree.XML(urllib.urlopen(self.executeSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaExecute=etree.XMLSchema(schemaDocExecute)
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        postinputs = postpywps.parseRequest(self.postExecuteComplexInputRequest)
        self.postExecuteComplexInputRequest.seek(0)
        postpywps.performRequest(postinputs)
        executeComplexInputPOST=etree.XML(postpywps.response,self.parser)
        self.assertEquals(schemaExecute.assertValid(executeComplexInputPOST),None)
    
 
    def testExecuteComplexInputOutputDirect(self):
        """Testing raster and vector I/O"""
        
        self._setFromEnv()
         
        #Testing simple request with 2 complexdata, one raster another vector
        schemaDocExecute=etree.XML(urllib.urlopen(self.executeSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaExecute=etree.XMLSchema(schemaDocExecute)
            
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        postinputs = postpywps.parseRequest(self.postExecuteComplexInputRequest)
        self.postExecuteComplexInputRequest.seek(0)
        #postinputs = postpywps.parseRequest(self.postExecuteComplexInputOneOutputRequest)
        postpywps.performRequest(postinputs)
        
        executeComplexInputOneOutputPOST=etree.XML(postpywps.response,self.parser)
        self.assertEquals(schemaExecute.assertValid(executeComplexInputOneOutputPOST),None)
    
 
 
   
    def testExecuteComplexInputOneOutputReference(self):
        """Test lineage and output as reference"""
        
        self._setFromEnv()
        
        schemaDocExecute=etree.XML(urllib.urlopen(self.executeSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaExecute=etree.XMLSchema(schemaDocExecute)
            
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        postinputs = postpywps.parseRequest(self.postExecuteComplexInputOneOutputRequest)
        self.postExecuteComplexInputOneOutputRequest.seek(0)
        postpywps.performRequest(postinputs)
        executeComplexInputOneOutputPOST=etree.XML(postpywps.response,self.parser)
        self.assertEquals(schemaExecute.assertValid(executeComplexInputOneOutputPOST),None)
 
 
 
    def testExecuteLiteraData(self):
        """Test literaldata lineage and response document"""
        #Literal data doesnt support reference output, yet
       
        self._setFromEnv()
        
        schemaDocExecute=etree.XML(urllib.urlopen(self.executeSchemaResponse).read(),parser=self.parser,base_url=self.base_url)
        schemaExecute=etree.XMLSchema(schemaDocExecute)
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        postinputs = postpywps.parseRequest(self.postExecuteLiteraDataRequest)
        self.postExecuteLiteraDataRequest.seek(0)
        postpywps.performRequest(postinputs)
        
        executeComplexInputOneOutputPOST=etree.XML(postpywps.response,self.parser)
        self.assertEquals(schemaExecute.assertValid(executeComplexInputOneOutputPOST),None)
 
    def testWSDL(self):
        """Test WSDL output content"""
        self._setFromEnv()
        schemaDocWSDL=etree.XML(urllib.urlopen(self.wsdlSchema).read(),parser=self.parser,base_url=self.base_url)
        schemaWSDL=etree.XMLSchema(schemaDocWSDL)
        
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        inputs=getpywps.parseRequest("WSDL")
        #print inputs
        getpywps.performRequest()
     
        wsdlDoc=etree.XML(getpywps.response,self.parser)
        self.assertEquals(schemaWSDL.assertValid(wsdlDoc),None)

    
    def testSOAP11(self):
        """Test SOAP1.1 returned envelope"""
        #Same as testGetCapabilities is soap_tests
        self._setFromEnv()
        
        schemaDocSOAP=etree.XML(urllib.urlopen(self.soap11Schema).read(),parser=self.parser,base_url=self.base_url)
        schemaSOAP=etree.XMLSchema(schemaDocSOAP)
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesSOAP11RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP11.xml"))
        postpywps.parseRequest(getCapabilitiesSOAP11RequestFile)
         
        postpywps.performRequest()
        soap = Soap.SOAP()
        response = soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False) 
        soapDoc=etree.XML(response,self.parser)
        self.assertEquals(schemaSOAP.assertValid(soapDoc),None)
      
    def testSOAP12(self):
        """Test SOAP1.2 returned envelope"""
        self._setFromEnv()
        
        schemaDocSOAP=etree.XML(urllib.urlopen(self.soap12Schema).read(),parser=self.parser,base_url=self.base_url)
        schemaSOAP=etree.XMLSchema(schemaDocSOAP)
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesSOAP12RequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request_SOAP12.xml"))
        postpywps.parseRequest(getCapabilitiesSOAP12RequestFile)
         
        postpywps.performRequest()
        
        soap = Soap.SOAP()
        response = soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False) 
        soapDoc=etree.XML(response,self.parser)
        self.assertEquals(schemaSOAP.assertValid(soapDoc),None)
    
    def testSOAP11Fault(self):
        """Test Fault SOAP1.1"""
        
        schemaDocSOAP=etree.XML(urllib.urlopen(self.soap11Schema).read(),parser=self.parser,base_url=self.base_url)
        schemaSOAP=etree.XMLSchema(schemaDocSOAP)
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        exceptionFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_exception_SOAP11.xml"))
        postpywps.parseRequest(exceptionFile)
        try:
            postpywps.performRequest()
        except pywps.Exceptions.InvalidParameterValue,e:
            postpywps.response=e.getResponse()
        
        soap=Soap.SOAP()
        response=soap.getResponse(postpywps.response,soapVersion=postpywps.parser.soapVersion,isSoapExecute=postpywps.parser.isSoapExecute,isPromoteStatus=False)
       
        soapDoc=etree.XML(response,self.parser)
        self.assertEquals(schemaSOAP.assertValid(soapDoc),None)   

    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
    
   
if __name__ == "__main__":
   # unittest.main()
   suite = unittest.TestLoader().loadTestsFromTestCase(SchemaTestCase)
   unittest.TextTestRunner(verbosity=2).run(suite)
        