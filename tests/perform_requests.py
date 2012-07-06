import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
#sys.path.append(pywpsPath)
sys.path.insert(0,pywpsPath)

import pywps
import pywps.Process
import unittest
from xml.dom import minidom
from lxml import etree
import base64,re,urllib,tempfile
if os.name != "java":
    from osgeo import ogr
else:
    os.putenv("PYWPS_CFG", os.path.join(pywpsPath,"pywps","default"))
    os.environ["PYWPS_CFG"] = os.path.join(pywpsPath,"pywps","default.cfg")
    os.putenv("PYWPS_TEMPLATES", os.path.join(pywpsPath,"tests","Templates"))
    os.environ["PYWPS_TEMPLATES"] = os.path.join(pywpsPath,"tests","Templates")
    os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
    os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")

import tempfile

#FTP server function called by test19FTPSupport     
def ftpServer(ftpHost,ftpPort,ftpLogin,ftpPasswd,ftpPath,ftpPerm):
    from pyftpdlib import ftpserver
    authorizer = ftpserver.DummyAuthorizer()
    authorizer.add_user(ftpLogin, ftpPasswd, ftpPath, ftpPerm)
    handler = ftpserver.FTPHandler
    handler.authorizer = authorizer
    address = (ftpHost, ftpPort)
    ftpd = ftpserver.FTPServer(address, handler)
    ftpd.serve_forever()


class RequestGetTestCase(unittest.TestCase):
    inputs = None
    getcapabilitiesrequest = "service=wps&request=getcapabilities"
    getdescribeprocessrequest = "service=wps&request=describeprocess&version=1.0.0&identifier=dummyprocess"
    getdescribeprocessallrequest = "service=wps&request=describeprocess&version=1.0.0&identifier=all"
    getexecuterequest = "service=wps&request=execute&version=1.0.0&identifier=dummyprocess&datainputs=[input1=20;input2=10]"
    #wfsurl = "http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.0.0&request=getfeature&service=wfs&typename=park"
    wfsurl = "http://rsg.pml.ac.uk/geoserver2/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=rsg:areas&maxFeatures=1"
    wcsurl = "http://www.bnhelp.cz/cgi-bin/crtopo?service=WMS&request=GetMap&LAYERS=sitwgs&TRANSPARENT=true&FORMAT=image%2Ftiff&EXCEPTIONS=application%2Fvnd.ogc.se_xml&VERSION=1.1.1&STYLES=default&SRS=EPSG%3A4326&BBOX=-10,-10,10,10&WIDTH=50&HEIGHT=50"
    wpsns = "http://www.opengis.net/wps/1.0.0"
    owsns = "http://www.opengis.net/ows/1.1"
    ogrns = "http://ogr.maptools.org/"
    
    #Generic external data
    simplePolyURL="http://rsg.pml.ac.uk/wps/testdata/single_point.gml"
    simpleJPG="http://rsg.pml.ac.uk/wps/testdata/basin_50K_nc.jpg"
    simpleLine="http://openlayers.org/dev/examples/gml/line.xml"
    
    #FTP parameters for test20FTPSupport
    #Pure PyWPS ftp configuration
    ftpLogin="user"
    ftpPasswd="12345"
    ftpPort=6666 # something above 1024 to avoid root permission
    outputPath="ftp://localhost"
    outputURL="ftp://localhost"
    #ftpServer variables
    ftpPath=pywps.config.getConfigValue("server","tempPath")
    ftpHost="127.0.0.1"
    ftpPerm="elradfmw"
    
    xmldom = None

    def setUp(self):
        #Silence PyWPS Warning:       from pywps.Process.Process import WPSProcess
        sys.stderr=open("/dev/null","w")

    def testT00Assync(self):
        """Test asynchronous mode for the first time"""
  
        self._setFromEnv()
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest("service=wps&request=execute&version=1.0.0&identifier=asyncprocess&status=true&storeExecuteResponse=true")
        self.assertEquals(mypywps.inputs["request"], "execute")
        self.assertTrue("asyncprocess" in mypywps.inputs["identifier"])
        mypywps.performRequest()
        xmldom = minidom.parseString(mypywps.response)
        self.assertTrue(mypywps.response)
  
        if len(xmldom.getElementsByTagNameNS(self.wpsns,"ProcessAccepted")) == 1:
            self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"ProcessAccepted")) == 1)
        else:
            self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"ProcessSucceeded")))
            self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"ProcessSucceeded")))
    
  
    def testT01PerformGetCapabilities(self):
        """Test if GetCapabilities request returns Capabilities document"""
        self._setFromEnv()
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        
        getCapabilitiesRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request.xml"))
        postinputs = postpywps.parseRequest(getCapabilitiesRequestFile)
        postpywps.performRequest(postinputs)
        xmldom = minidom.parseString(postpywps.response)
        self.assertEquals(xmldom.firstChild.nodeName, "wps:Capabilities")
        
        inputs = getpywps.parseRequest(self.getcapabilitiesrequest)
        getpywps.performRequest(inputs)
        xmldom = minidom.parseString(getpywps.response)
        self.assertEquals(xmldom.firstChild.nodeName, "wps:Capabilities")
  
  
  
    def testT02ProcessesLengthGetCapabilities(self):
        """Test, if any processes are listed in the Capabilities document
        """
        self._setFromEnv()
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = getpywps.parseRequest(self.getcapabilitiesrequest)
        getpywps.performRequest(inputs)
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request.xml"))
        postinputs = postpywps.parseRequest(getCapabilitiesRequestFile)
        postpywps.performRequest(postinputs)
        xmldom = minidom.parseString(postpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)
        
    
  
    def testT03PerformDescribeProcess(self):
        """Test if DescribeProcess request returns ProcessDescription document"""
        self._setFromEnv()
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        getpywps.parseRequest(self.getdescribeprocessrequest)
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
        self.assertEquals(xmldom.firstChild.nodeName, "wps:ProcessDescriptions")
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        describeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_request_dummyprocess.xml"))
        postinputs = postpywps.parseRequest(describeRequestFile)
        postpywps.performRequest(postinputs)
        xmldom = minidom.parseString(postpywps.response)
        self.assertEquals(xmldom.firstChild.nodeName, "wps:ProcessDescriptions")
  
    def testT04ProcessesLengthDescribeProcess(self):
        """Test, if any processes are listed in the DescribeProcess document
        """
        self._setFromEnv()
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        getpywps.parseRequest(self.getdescribeprocessrequest)
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagName("ProcessDescription"))>0)
        self.assertEquals(len(xmldom.getElementsByTagName("ProcessDescription")),
                len(getpywps.inputs["identifier"]))
       
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        getpywps.parseRequest(self.getdescribeprocessallrequest)
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
        self.assertEquals(len(xmldom.getElementsByTagName("ProcessDescription")),len(getpywps.request.processes))
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        describeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_request_dummyprocess.xml"))
        postinputs = postpywps.parseRequest(describeRequestFile)
        postpywps.performRequest(postinputs)
        xmldom = minidom.parseString(postpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagName("ProcessDescription"))>0)
        self.assertEquals(len(xmldom.getElementsByTagName("ProcessDescription")),
                len(postpywps.inputs["identifier"]))
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        describeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_request_all.xml"))
        postinputs = postpywps.parseRequest(describeRequestFile)
        postpywps.performRequest(postinputs)
        xmldom = minidom.parseString(postpywps.response)
        self.assertEquals(len(xmldom.getElementsByTagName("ProcessDescription")),len(postpywps.request.processes))
        
        
  
    ######################################################################################)
    def testT05ParseExecute(self):
        """Test if Execute request is parsed and performed"""
        self._setFromEnv()
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getexecuterequest)
        self.assertEquals(mypywps.inputs["request"], "execute")
        self.assertTrue("dummyprocess" in mypywps.inputs["identifier"])
        mypywps.performRequest()
        xmldom = minidom.parseString(mypywps.response)
        self.assertEquals(len(xmldom.getElementsByTagNameNS(self.wpsns,"LiteralData")),2)
    
  
    def testT06ParseExecuteLiteralInput(self):
        """Test if Execute with LiteralInput and Output is executed"""
        
        #Note, bool input should be checked for False, if there is something like this in the code: bool("False")
        #Then the output will be True and the test will fail
        self._setFromEnv()
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=literalprocess&datainputs=[int=1;string=spam%40foo.com;float=1.1;zeroset=0.0;bool=False]")
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-literalinput.xml"))
        postinputs = postpywps.parseRequest(executeRequestFile)
  
        getpywps.performRequest(getinputs)
        postpywps.performRequest(postinputs)
        getxmldom = minidom.parseString(getpywps.response)
        postxmldom = minidom.parseString(postpywps.response)
  
        getliteraldata = getxmldom.getElementsByTagNameNS(self.wpsns,"LiteralData")
        postliteraldata = postxmldom.getElementsByTagNameNS(self.wpsns,"LiteralData")
        self.assertEquals(len(getliteraldata),4)
        self.assertEquals(len(postliteraldata),4)
  
        self.assertEquals(getliteraldata[0].firstChild.nodeValue,
                postliteraldata[0].firstChild.nodeValue)
        self.assertEquals(getliteraldata[1].firstChild.nodeValue,
                postliteraldata[1].firstChild.nodeValue)
        self.assertEquals(getliteraldata[2].firstChild.nodeValue,
                postliteraldata[2].firstChild.nodeValue)
        self.assertEquals(getliteraldata[3].firstChild.nodeValue,
                postliteraldata[3].firstChild.nodeValue)
        #1,1.1,False,spam
        self.assertEquals(getliteraldata[0].firstChild.nodeValue, "1")
        self.assertEquals(getliteraldata[1].firstChild.nodeValue, "1.1")
        self.assertEquals(getliteraldata[2].firstChild.nodeValue, "False")
        self.assertEquals(getliteraldata[3].firstChild.nodeValue, "spam@foo.com")
        
    
  
    def testT07ParseExecuteComplexInput(self):
        """Test if Execute with ComplexInput and Output, given directly with input XML request is executed"""
        self._setFromEnv()
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-direct.xml"))
        postinputs = postpywps.parseRequest(executeRequestFile)
  
        postpywps.performRequest(postinputs)
        postxmldom = minidom.parseString(postpywps.response)
        # compare the raster files
        rasterOrig = open(os.path.join(pywpsPath,"tests","datainputs","dem.tiff"))
        rasterOrigData = rasterOrig.read()
        outputs =  postxmldom.getElementsByTagNameNS(self.wpsns,"ComplexData")
        rasterWpsData = base64.decodestring(outputs[1].firstChild.nodeValue)
        self.assertTrue(rasterWpsData, rasterOrigData)
  
        if os.name != "java":
            # compare the vector files
            gmlDriver = ogr.GetDriverByName("GML")
            origDs = gmlDriver.Open(os.path.join(pywpsPath,"tests","datainputs","lakes.gml"))
  
            wpsFile = tempfile.mktemp(prefix="pywps-test")
            wpsFile = open(wpsFile,"w")
            wpsFile.write(postinputs["datainputs"][1]["value"])
            wpsFile.close()
            wpsDs = gmlDriver.Open(wpsFile.name)
  
            wpslayer = wpsDs.GetLayerByIndex(0)
            origlayer = origDs.GetLayerByIndex(0)
  
            self.assertTrue(wpslayer.GetFeatureCount(), origlayer.GetFeatureCount())
  
            # enough  here
            # for f in range(wpslayer.GetFeatureCount()):
            #     origFeature = origlayer.GetFeature(f)
            #     wpsFeature = wpslayer.GetFeature(f)
            #     self.assertTrue(origFeature.Equal(wpsFeature))
   
    def testT08ParseExecuteComplexInputRawDataOutput(self):
        """Test if Execute with ComplexInput and Output, given directly with input XML request is executed, with raster file requested as
        raw data output"""
        self._setFromEnv()
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-direct-rawdata-output.xml"))
        postinputs = postpywps.parseRequest(executeRequestFile)
  
        postpywps.performRequest(postinputs)
        origData = open(os.path.join(pywpsPath,"tests","datainputs","dem.tiff"),"rb")
        rasterWpsData = base64.encodestring(origData.read())
        resp =  base64.encodestring(postpywps.response.read())
        self.assertEquals(resp.strip(),rasterWpsData.strip())
   
    def test09ParseExecuteComplexVectorInputs(self):
        """Test, if pywps can parse complex vector input values, given as reference, output given directly"""
        
        self._setFromEnv()
        import urllib
        import tempfile
        gmlFile = tempfile.mktemp(prefix="pywps-test-wfs")
        gmlFile = open(gmlFile,"w")
        gmlFile.write(urllib.urlopen(self.wfsurl).read())
        gmlFile.close()
  
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        request = "service=wps&request=execute&version=1.0.0&identifier=complexVector&datainputs=[indata=%s]" % (urllib.quote(self.wfsurl))
        inputs = mypywps.parseRequest(request)
        mypywps.performRequest()
        
        
        xmldom = minidom.parseString(mypywps.response)
        self.assertFalse(len(xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport")), 0)
        xmldom2 = minidom.parse(gmlFile.name)
        
        # try to separte the GML file from the response document
        outputgml = None
        for elem in xmldom.getElementsByTagNameNS(self.wpsns,"ComplexData")[0].childNodes:
            if elem.nodeName == "FeatureCollection":
                outputgml = elem
                break
  
        # output GML should be the same, as input GML
        self.assertTrue(xmldom, outputgml)
  
   
    def testT11ParseExecuteComplexVectorAndRasterInputsAsReferenceOutpu(self):
        """Test, if pywps can store complex values as reference"""
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-output-as-reference.xml"))
        postinputs = postpywps.parseRequest(executeRequestFile)
  
        postpywps.performRequest()
        
        #print postpywps.request.process.outputs["rasterout"].value
  
    def testsT12ExecuteBBox(self):
        """Parsing Bounding Box Input"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-bbox.xml"))
        getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=bboxprocess&datainputs=[bboxin=%s]"
                % ("-11,-12,13,14"))
        postpywps.parseRequest(executeRequestFile)
  
        postpywps.performRequest()
        getpywps.performRequest()
  
        postinput = postpywps.request.process.getInput("bboxin")
        getinput = getpywps.request.process.getInput("bboxin")
        self.assertEquals(getinput.getValue().coords,
                          postinput.getValue().coords)
  
  
    ######################################################################################
    
    def test13ParseExecuteComplexVectorInputsAsReferenceMapServer(self):
        """Test if PyWPS can return correct WFS and WCS services for output
        data reference, if mapserver module is not present the test will fail """
        
        self._setFromEnv()
        import urllib
        import tempfile
        
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        #Outputs will be generated accordint to the order in responsedocument
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexprocessows&datainputs=[rasterin=%s;vectorin=%s]&responsedocument=[vectorout=@asreference=true;rasterout=@asreference=true]" % (urllib.quote(self.wcsurl), urllib.quote(self.wfsurl)))
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
       
        self.assertFalse(len(xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport")), 0)
  
        # try to get out the Reference elemengt
        wfsurl = xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[0].getAttribute("href")
        wcsurl = xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[1].getAttribute("href")
        
        # test, if there are WFS and WCS request strings
        self.assertTrue(wfsurl.find("WFS") > -1)
        self.assertTrue(wcsurl.find("WCS") > -1)
        #print urllib.unquote(wfsurl)
        #print urllib.unquote(wcsurl)
    
    def test14ParseExecuteResponseDocumentGET(self):
         """Return a response document that only containts the requested ouputs """
         self._setFromEnv()
         import urllib
        
         getpywps = pywps.Pywps(pywps.METHOD_GET)
         
         #1 output only vectorout
         inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexprocess&datainputs=[rasterin=%s;vectorin=%s]&responsedocument=[vectorout=@asreference=true]" % (urllib.quote(self.wcsurl), urllib.quote(self.wfsurl)))
         getpywps.performRequest()
         xmldom = minidom.parseString(getpywps.response)  
         self.assertEquals(len(xmldom.getElementsByTagNameNS(self.wpsns,"Output")),1)
        
         #check that it is vectorout
         outputNodes=xmldom.getElementsByTagNameNS(self.wpsns,"Output")
         identifierNodes=outputNodes[0].getElementsByTagNameNS(self.owsns,"Identifier")
         self.assertEquals(identifierNodes[0].firstChild.nodeValue,"vectorout")
         
         
         #all outputs --> blank responseDocument
         inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexprocess&datainputs=[rasterin=%s;vectorin=%s]&responsedocument=[]" % (urllib.quote(self.wcsurl), urllib.quote(self.wfsurl)))
         getpywps.performRequest()
         
         xmldom = minidom.parseString(getpywps.response)
         self.assertEquals(len(xmldom.getElementsByTagNameNS(self.wpsns,"Output")),2)
    
    def test15ParseExecuteResponseDocumentPOST(self):
        """Return a response document that only containts the requested ouputs, from an XML request 
        lineage output will also be checked
        """
        
        self._setFromEnv()
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-one-output-as-reference.xml"))
        postinputs = postpywps.parseRequest(executeRequestFile)
        postpywps.performRequest()
        #The response linage contains URLs with & that will crash the DOM parser
        xmldom = minidom.parseString(postpywps.response.replace("&","%26"))
        
        #1 OutputDefintions only and that is rasterout
        outputDefNodes=xmldom.getElementsByTagNameNS(self.wpsns,"OutputDefinitions")
        self.assertEquals(len(outputDefNodes),1)
        identifierNodes=outputDefNodes[0].getElementsByTagNameNS(self.owsns,"Identifier")
        self.assertEquals(identifierNodes[0].firstChild.nodeValue,"rasterout")
        
        #1 ProcessOutput only check that is rasterout
        processOutNodes=xmldom.getElementsByTagNameNS(self.wpsns,"ProcessOutputs")
        self.assertEquals(len(processOutNodes),1)
        identifierNodes=processOutNodes[0].getElementsByTagNameNS(self.owsns,"Identifier")
        self.assertEquals(identifierNodes[0].firstChild.nodeValue,"rasterout")
               
    def test16ParseLineageResponseDocumentPost(self):
        """if Return response document contain lineage, lineage shall be identical to Execute input, even for multiple inputs"""
        
        self._setFromEnv()
        import hashlib
  
        imgPNGHashOriginal="b95e7e25c8c3897452a1f164da6d8c83"
        imgBMPHashOriginal="ed3a7fa929dc5236dd12667eb19c6a6c"
        
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request_lineage.xml"))
        postpywps.parseRequest(executeRequestFile)
        postpywps.performRequest()
        postxmldom = minidom.parseString(postpywps.response)
        dataInputsDom=postxmldom.getElementsByTagNameNS(self.wpsns,"DataInputs")
        #Check lineage presence
        self.assertTrue(len(dataInputsDom)>0)
        
        inputDom=dataInputsDom[0].getElementsByTagNameNS(self.wpsns,"Input")
        
        #Check lineage size (number elements)
        self.assertEquals(len(inputDom),6)
        
        idNameList=[input.getElementsByTagNameNS(self.owsns,"Identifier")[0].childNodes[0].nodeValue for input in  inputDom ]
        
        #Check number lineage for raster,vector,bboxin (2 of each)
        len([id for id in idNameList if id=="rasterin"])
        self.assertEquals(len([id for id in idNameList if id=="rasterin"]),2)
        self.assertEquals(len([id for id in idNameList if id=="vectorin"]),2)
        self.assertEquals(len([id for id  in idNameList if id=="bboxin"]),2)
        
        complexDataDom=dataInputsDom[0].getElementsByTagNameNS(self.wpsns,"ComplexData")
        xmlNodes=[item for item in complexDataDom if (item.getAttribute("mimeType")=="text/xml" or item.getAttribute("mimeType")=="application/xml")]
        ogrNodes=[node.getElementsByTagNameNS(self.ogrns,"FeatureCollection") for node in xmlNodes]
  
        #Checking FeatureCollection in XML payload
        self.assertEquals(len(ogrNodes),2)
        
        #getting png image
        imgPNGLineage=[item.childNodes[0].toxml().strip() for item in complexDataDom if item.getAttribute("mimeType")=="image/png"][0]
        imgBMPLineage=[item.childNodes[0].toxml().strip() for item in complexDataDom if item.getAttribute("mimeType")=="image/bmp"][0]
        imgPNGHash=hashlib.md5(imgPNGLineage).hexdigest() #b95e7e25c8c3897452a1f164da6d8c83
        imgBMPHash=hashlib.md5(imgBMPLineage).hexdigest() #ed3a7fa929dc5236dd12667eb19c6a6c
        
        self.assertEquals(imgPNGHash,imgPNGHashOriginal)
        self.assertEquals(imgBMPHash,imgBMPHashOriginal)
        
        #ATTENTION BUG with ticket #2551 not checked in unittest
        bboxDom=dataInputsDom[0].getElementsByTagNameNS(self.wpsns,"BoundingBoxData")
        #dimSet has to be identifical to LowerCorner/UpperCorner dim
        dimSet=set(map(int,[item.getAttribute("dimensions") for item in bboxDom]) )
        lowerSet=set([len(coord.split(" ")) for coord in [item.getElementsByTagNameNS(self.owsns,"LowerCorner")[0].childNodes[0].nodeValue for item in bboxDom]])
        upperSet=set([len(coord.split(" ")) for coord in [item.getElementsByTagNameNS(self.owsns,"UpperCorner")[0].childNodes[0].nodeValue for item in bboxDom]])
        self.assertEquals(len(dimSet.difference(lowerSet)),0) #0
        self.assertEquals(len(dimSet.difference(upperSet)),0) #0
    
    def test17LiteralBBOXasReference(self):
        """BBOX and Literal as ReferenceOutput"""
        self._setFromEnv()
        #Testing BBOX as reference
        getpywps=pywps.Pywps(pywps.METHOD_GET)
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=Execute&identifier=bboxprocess&datainputs=[bboxin=12,45,56,67]&responsedocument=bboxout=@asReference=true")
        getpywps.performRequest(getinputs)
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))>0)
        #Testing 2 string output
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=literalprocess&datainputs=[int=1;string=spam%40foo.com;float=1.1;zeroset=0.0;bool=False]&responsedocument=bool=@asReference=True;string=@asReference=True")
        getpywps.performRequest(getinputs)
  
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))==2)
    
    def test18ReferenceAsDefault(self):
        """asReference output as default and user overwrite"""
        self._setFromEnv()
        
        getpywps=pywps.Pywps(pywps.METHOD_GET)
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=Execute&identifier=referencedefault")
        getpywps.performRequest(getinputs)
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))==3)
  
        #Testing overwrite by responsedocument
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=Execute&identifier=referencedefault&responsedocument=vectorout=@asReference=False;string=@asReference=False;bboxout=@asReference=False")
        getpywps.performRequest(getinputs)
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))==0)
  
    def test19AssyncSpawned(self):
        """Spawned async subprocess"""
        #NOTE: testT00Assync, just checks the status document. If the spawned failed the status document will retain in ProcessAccepted
        self._setFromEnv()
        import time
              
        getpywps=pywps.Pywps(pywps.METHOD_GET)
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=Execute&identifier=ultimatequestionprocess&storeExecuteResponse=True&status=True")
        getpywps.performRequest(getinputs)
            
        xmldom = minidom.parseString(getpywps.response)
        executeNode=xmldom.getElementsByTagNameNS(self.wpsns,"ExecuteResponse")
        #Checking for ExecuteResponse
        self.assertTrue(len(executeNode)>0)
        #building file path
        baseFile=os.path.basename(executeNode[0].getAttribute("statusLocation"))
        outputPath = pywps.config.getConfigValue("server","outputPath")
        
        #sleep for a while.....
        time.sleep(10)
        
        statusdom=minidom.parse(open(os.path.join(outputPath,baseFile)))
        
        self.assertTrue(bool(statusdom.getElementsByTagNameNS(self.wpsns,"ProcessStarted")) or bool(statusdom.getElementsByTagNameNS(self.wpsns,"ProcessSucceeded")))
        #BAD
        #bool(statusdom.getElementsByTagNameNS(wpsns,"ProcessAccepted"))
        
    def test20FTPSupport(self):
        """Testing FTP support"""
        #NOTE: pyftpdlib uses a pure Python thread to work, if using the normal Thread class thins get blocked
        #Better to use mutiprocessor or a suprocess.Popen call 
        try:
            from pyftpdlib import ftpserver
        except:
            assert False, "Please install pyftpdlib from http://code.google.com/p/pyftpdlib/" 
        
        from multiprocessing import Process
        import time,os.path
        import hashlib
        import pywps
       
        #PyWPS configuration -- setConfiguration added to in SVN - pywps-soap:1260
        pywps.config.setConfigValue("server","outputPath", self.outputPath)
        pywps.config.setConfigValue("server","outputUrl",self.outputURL)
        pywps.config.setConfigValue("server","ftplogin",self.ftpLogin)
        pywps.config.setConfigValue("server","ftppasswd",self.ftpPasswd)
        #ATTENTION EVERYTHING HAS TO BE STRING OTHERWISE IT DOESNT WORK
        pywps.config.setConfigValue("server","ftpport",str(self.ftpPort))
        
        p=Process(target=ftpServer,args=(self.ftpHost,self.ftpPort,self.ftpLogin,self.ftpPasswd,self.ftpPath,self.ftpPerm,))
        p.start()
        time.sleep(20)
        #running the WPS
        getpywps=pywps.Pywps(pywps.METHOD_GET)
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=Execute&identifier=referencedefault&responsedocument=vectorout=@asReference=True;string=@asReference=True;bboxout=@asReference=True")
        getpywps.performRequest(getinputs)
        xmldom = minidom.parseString(getpywps.response)
        time.sleep(3)# give some time to sync all code, maybe it's not necessary
        p.terminate()
        #SEE: if there is some error
        exceptionText=xmldom.getElementsByTagNameNS(self.owsns,"Reference")
        if len(exceptionText)>0:
            #We have an error, probably no FTP connection
            self.assertTrue(False,self.exceptionText.childNodes[0].nodeValue)
        
        #RESET FTP parameters
        pywps.config.loadConfiguration()
        
        #ASSIGNED PROCESS OUTPUT
        # 2nd part output interactor, 1st part lambda case ComplexOutput then open file and read content
        
        processOutputs=list(map(lambda output:open(os.path.join(self.ftpPath,output.value)).read() if isinstance(output,pywps.Process.InAndOutputs.ComplexOutput) else output.value,getpywps.request.process.outputs.values() ))
        processOutputsMD5=[hashlib.md5(item).hexdigest() for item in processOutputs]
        
        #FTP PROCESS OUTPUT
        referenceNodes=xmldom.getElementsByTagNameNS(self.wpsns,"Reference")
        urlList=[node.getAttribute("href") for node in referenceNodes]
        #getContent from folfer, FTP is already dead
        outputFTP=[open(os.path.join(self.ftpPath,os.path.basename(url))).read() for url in urlList]
        outputFTPMD5=[hashlib.md5(item).hexdigest() for item in outputFTP]
        #assertFalse (empty array)
        self.assertFalse(bool([item in outputFTP for item in outputFTPMD5 if not item]))
  
    def test21GetParseXLinkURL(self):
        """check for correct parsing of input as reference"""
        
        self._setFromEnv()
        import urllib
        import types
        #[simple URL,SimpleURL+aatributes,xlink=URL,xlink=URL+attributes,]
        requests=["service=wps&request=execute&version=1.0.0&identifier=complexVector&datainputs=[indata=%s]" % (urllib.quote_plus(self.simplePolyURL)),
                  "service=wps&request=execute&version=1.0.0&identifier=complexVector&datainputs=[indata=%s@method=POST@mimeType=%s]" % (urllib.quote_plus(self.simplePolyURL),urllib.quote_plus("text/xml")),
                  "service=wps&request=execute&version=1.0.0&identifier=complexVector&datainputs=[indata=@xlink:href=%s]" % (urllib.quote_plus(self.simplePolyURL)),
                  "service=wps&request=execute&version=1.0.0&identifier=complexVector&datainputs=[indata=@xlink:href=%s@method=POST@mimeType=%s]" % (urllib.quote_plus(self.simplePolyURL),urllib.quote_plus("text/xml"))]
        keysAtt=[None,['method','mimetype'],None,['method','mimetype']]
        valueAtt=[None,['POST','text/xml'],None,['POST','text/xml']]
        zipRequests=zip(requests,keysAtt,valueAtt)
        
        for index,requestStructure in enumerate(zipRequests):
            
            mypywps = pywps.Pywps(pywps.METHOD_GET)    
            inputs = mypywps.parseRequest(requestStructure[0])
            mypywps.performRequest()
            xmldom = minidom.parseString(mypywps.response)
            self.assertFalse(len(xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport")),msg="request number %s failed" % index)
            outputGML=xmldom.getElementsByTagNameNS(self.ogrns,"FeatureCollection")
            self.assertTrue(bool(outputGML))
            #Check if the attributes are being passed
            if not (type(requestStructure[1]) is types.NoneType):
                inputKeys=set(inputs["datainputs"][0].keys())
                inputValues=set(inputs["datainputs"][0].values())
                #Any missing elements in inputKey will raise a FALSE statment
                self.assertTrue((inputKeys & set(requestStructure[1])) == set(requestStructure[1]))
                self.assertTrue((inputValues & set(requestStructure[2])) == set(requestStructure[2]))
    
    def test23GetInputReferenceMimeType(self):
        """mimeType included in reference input, validated and understood"""
        
        #USE urllib.quote_lus
        #'urllib.quote_plus("http://rsg.pml.ac.uk/wps/testdata/single_point.gml")
        
        self._setFromEnv()
        import urllib
        import tempfile
        getpywps=pywps.Pywps(pywps.METHOD_GET)  
        #raise exception if sending wrong mimetype  
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexVector&datainputs=[indata=%s@method=POST@mimeType=%s]&responsedocument=[outdata=@asreference=true;outdata2=@asreference=true]" % (self.simplePolyURL,urllib.quote_plus("image/tiff")))
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport"))==1)
        
        #Correct mimetype process goes as normal
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexVector&datainputs=[indata=%s@method=POST@mimeType=%s]&responsedocument=[outdata=@asreference=true;outdata2=@asreference=true]" % (self.simplePolyURL,urllib.quote_plus("text/xml")))
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))>0)
        #<wps:Reference href="http://localhost/wpsoutputs/outdata-163877NiZFb" mimeType="text/xml" />
        
        #no mimetype
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexVector&datainputs=[indata=%s]&responsedocument=[outdata=@asreference=true;outdata2=@asreference=true]" % self.simplePolyURL)
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))>0)
  
  
    def test24OutputMimeType(self):
        """mimeType output validated and understood mimeTypeOut()"""
        
        #USE urllib.quote_lus
        #'urllib.quote_plus("http://rsg.pml.ac.uk/wps/testdata/single_point.gml")
        
        self._setFromEnv()
        import urllib
        import tempfile
        getpywps=pywps.Pywps(pywps.METHOD_GET)  
        #everything ok  
        
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexVector&datainputs=[indata=%s@method=POST@mimeType=%s]&responsedocument=[outdata=@mimeType=%s;outdata2=@asreference=true@mimeType=%s]" % (self.simplePolyURL,urllib.quote_plus("text/xml"),urllib.quote_plus("application/xml"),urllib.quote_plus("application/xml")))
        #ALL INPUTS CORRECT
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.ogrns,"FeatureCollection"))==1)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))==1)
        
        #ONE INPUT WRONG
        
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexVector&datainputs=[indata=%s@method=POST@mimeType=%s]&responsedocument=[outdata=@mimeType=%s;outdata2=@asreference=true@mimeType=%s]" % (self.simplePolyURL,urllib.quote_plus("text/xml"),urllib.quote_plus("application/xml"),urllib.quote_plus("image/png")))
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)
        try:
            nodeValue=xmldom.getElementsByTagNameNS("http://www.opengis.net/ows/1.1","Exception")[0].getAttributeNode("locator").nodeValue
  
        except:
            nodeValue=None
       
        self.assertTrue(nodeValue=="outdata2");
        
        #NO OUTPUT MIMETYPE, but process has a list of processes ()
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexVector&datainputs=[indata=%s@method=POST@mimeType=%s]&responsedocument=[outdata;outdata2=@asreference=true]" % (self.simplePolyURL,urllib.quote_plus("text/xml")))
        getpywps.performRequest()
        xmldom=minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))==1)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.ogrns,"FeatureCollection"))==1)
        #<wps:Reference href="http://localhost/wpsoutputs/outdata-163877NiZFb" mimeType="text/xml" />
        #NO MIMETYPE NO PROBLEM
        getpywps.parseRequest("service=wps&version=1.0.0&request=Execute&identifier=nomimetypesprocess&datainputs=[rasterin=%s;pause=1;vectorin=%s]&responsedocument=[vectorout=@asreference=true;rasterout=@asreference=true]" % (self.simpleJPG,self.simplePolyURL))
        getpywps.performRequest()
        xmldom=minidom.parseString(getpywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Reference"))==2)
        
    def test25WFSComplexOutput(self):
        """Test if PyWPS can return a correct WFS service content with projs"""
       #XML being checked by GDAL will raise an error, the unttest wil still be ok
       #ERROR 4: `/var/www/html/wpsoutputs/vectorout-26317EUFxeb' not recognised as a supported file format. 
        #USE urllib.quote_lus
        #'urllib.quote_plus("http://rsg.pml.ac.uk/wps/testdata/single_point.gml")
        self._setFromEnv()
        import osgeo.ogr
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        #Outputs will be generated accordint to the order in responsedocument
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=ogrbuffer&datainputs=[data=%s;size=0.1]&responsedocument=[buffer=@asreference=true]" % urllib.quote(self.simpleLine))
        getpywps.performRequest()
        
        xmldom = minidom.parseString(getpywps.response)
        self.assertFalse(len(xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport")), 0)
  
        # try to get out the Reference elemengt
        wfsurl = xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[0].getAttribute("href")
        print wfsurl
        #wcsurl = xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[1].getAttribute("href")
        wfsurl=urllib.unquote(wfsurl)
        inSource=osgeo.ogr.Open(wfsurl)
        self.assertTrue(isinstance(inSource,osgeo.ogr.DataSource))
        inLayer=inSource.GetLayer()
        self.assertTrue(isinstance(inLayer,osgeo.ogr.Layer))
        self.assertTrue(isinstance(inLayer.GetNextFeature(),osgeo.ogr.Feature))
        
        #check for mutiple projections from config file
        projs=pywps.config.getConfigValue("mapserver","projs")
        #convert to list 
        projs=re.findall(r'\d+',projs)
        wfs110url=wfsurl.lower().replace("1.0.0","1.1.0").replace("getfeature","getcapabilities")
        try:
            wfsDom=minidom.parse(urllib.urlopen(wfs110url))
            defaultProj=wfsDom.getElementsByTagName("DefaultSRS")[0].firstChild.nodeValue #urn:ogc:def:crs:EPSG::4326
        except:
            assert False
        
        self.assertTrue(projs[0] in defaultProj)
        try:
            otherProjs=wfsDom.getElementsByTagName("OtherSRS") #urn:ogc:def:crs:EPSG::4326
        except:
            assert False
        self.assertTrue(len(otherProjs)==(len(projs)-1))    
        
    def test26WCSComplexOutput(self):
        """Test if PyWPS can return a correct WCS service contents with proj"""
       #XML being checked by GDAL will raise an error, the unttest wil still be ok
       #ERROR 4: `/var/www/html/wpsoutputs/vectorout-26317EUFxeb' not recognised as a supported file format. 
        self._setFromEnv()
        import osgeo.gdal
        self.simpleGeoTiff="http://rsg.pml.ac.uk/wps/testdata/elev_srtm_30m.tif"
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        #Outputs will be generated accordint to the order in responsedocument
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=returnWCS&datainputs=[input=%s]&responsedocument=[output=@asreference=true]" % urllib.quote(self.simpleGeoTiff))
        #getpywps.UUID 
        getpywps.performRequest()
        
        tmp=getpywps.response
        xmldom = minidom.parseString(tmp)
        self.assertFalse(len(xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport")), 0)
  
        # try to get out the Reference elemengt
        #wfsurl = xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[0].getAttribute("href")
        wcsurl = xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[0].getAttribute("href")
        wcsurl=urllib.unquote(wcsurl)
        inSource=osgeo.gdal.Open(wcsurl)
        self.assertTrue(isinstance(inSource,osgeo.gdal.Dataset),msg="Check if server path is correct in the conf file")
        self.assertTrue(isinstance(inSource.GetRasterBand(1),osgeo.gdal.Band))    
        
        #check multiple projections
        projs=pywps.config.getConfigValue("mapserver","projs")
        projs=re.findall(r'\d+',projs)    
        wcsDom=minidom.parse(urllib.urlopen(wcsurl.lower().replace("getcoverage","describecoverage")))
        projNodes=wcsDom.getElementsByTagName("requestResponseCRSs")
        self.assertTrue(len(projs)==len(projNodes))
  
    def test27NoLimitInput(self):  
        """Test if PyWPS accepts inputs without size limit"""
        self._setFromEnv()
        pywps.config.setConfigValue("server","maxfilesize", str(0))
        getpywps = pywps.Pywps(pywps.METHOD_GET) 
         #1 output only vectorout
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexprocess&datainputs=[rasterin=%s;vectorin=%s]&responsedocument=[vectorout=@asreference=true]" % (urllib.quote(self.wcsurl), urllib.quote(self.wfsurl)))
        getpywps.performRequest()
        try:
            xmldom = minidom.parseString(getpywps.response)
        except:
            assert False , "Raised a WPSException, not possible to use maxfilesize=0"  
        #reset
        listNode=xmldom.getElementsByTagNameNS(self.wpsns,"Reference")
        self.assertTrue(len(listNode)==1)
        pywps.config.loadConfiguration()          
  
    def test28MetadataOutputDescribeProcessAndExecute(self):
        """Test if Metatadata Output in describeProcess and Execute"""
        self._setFromEnv()
        getpywps = pywps.Pywps(pywps.METHOD_GET) 
        getpywps.parseRequest("service=wps&version=1.0.0&request=describeProcess&identifier=ogrbuffer")
        wpsTree=etree.fromstring(getpywps.performRequest())
        #metadata in processdescriont, and I/O
        self.assertTrue(len(wpsTree.xpath("//ProcessDescription/ows:Metadata",namespaces=wpsTree.nsmap))>0)
        self.assertTrue(len(wpsTree.xpath("//Input/ows:Metadata",namespaces=wpsTree.nsmap))>0)
        self.assertTrue(len(wpsTree.xpath("//Output/ows:Metadata",namespaces=wpsTree.nsmap))>0)
        
        getpywps.parseRequest("service=wps&version=1.0.0&request=Execute&identifier=ogrbuffer&datainputs=[data=%s;size=0.1]" % urllib.quote(self.simpleLine))
        wpsTree=etree.fromstring(getpywps.performRequest())
        
        self.assertTrue(len(wpsTree.xpath("//wps:Process/ows:Metadata",namespaces=wpsTree.nsmap))>0)
        self.assertTrue(len(wpsTree.xpath("//wps:ProcessOutputs/wps:Output/ows:Metadata",namespaces=wpsTree.nsmap))>0)
    
    def test29LanguageTranslation(self):
        """Test if title,abstract of process and I/O is translated"""
        self._setFromEnv()
        pywps.config.setConfigValue("wps","lang","en-CA,pt-PT")
        from pywps.Wps import Request
        
        wps=pywps.Pywps(pywps.METHOD_GET)
        wps.inputs={'request': 'getCapabilities', 'version': '1.0.0', 'service': 'wps'}
        request=Request(wps)
        returnerProcess=request.getProcess("returner")
        #process related
        returnerProcess.lang.strings["pt-PT"]["Return process"]="Processo de retorno"
        returnerProcess.lang.strings["pt-PT"]["This is demonstration process of PyWPS, returns the same file, it gets on input, as the output."]="Este eh um processo de demonstracao de PyWPS, retorna o mesmo ficheiro, o que ele recebe como entrada sai como saida"
        #inputs: data-->ComplexInput, text--: literal
        returnerProcess.lang.strings["pt-PT"]["Input vector data"]="Dados vectoriais de entrada"
        returnerProcess.lang.strings["pt-PT"]["Some width"]="Alguma largura"
        
        returnerProcess.inputs["data"].abstract="Complex data abstract dummy"
        returnerProcess.inputs["text"].abstract="Literal abstract dummy"
        returnerProcess.lang.strings["pt-PT"]["Complex data abstract dummy"]="Resumo teste de dados complexos"
        returnerProcess.lang.strings["pt-PT"]["Literal abstract dummy"]="Resumo teste de sequencia de caracteres"
        
        #outputs: output-->complexOutput, text-->literal data
        returnerProcess.lang.strings["pt-PT"]["Output vector data"]="Dados vectoriais de saida"
        returnerProcess.lang.strings["pt-PT"]["Output literal data"]="Sequencia de caracteres de saida"
        
        returnerProcess.outputs["output"].abstract="Complex output data abstract dummy"
        returnerProcess.outputs["text"].abstract="Literal output data abstract dummy"
        returnerProcess.lang.strings["pt-PT"]["Complex output data abstract dummy"]="Resumo teste de dados de saida complexos"
        returnerProcess.lang.strings["pt-PT"]["Literal output data abstract dummy"]="Resumo teste de sequencia de caracteres de saida"
           
        ptTranslations=[]
        for key in returnerProcess.lang.strings["pt-PT"].keys():
            ptTranslations.append(returnerProcess.lang.strings["pt-PT"][key])
    
        resultWPS=wps.performRequest(wps.parseRequest("service=wps&version=1.0.0&request=describeProcess&identifier=returner&language=pt-PT"),processes=[returnerProcess])
        wpsTree=etree.fromstring(resultWPS)
        
        #print wps.performRequest(wps.parseRequest("service=wps&version=1.0.0&request=describeProcess&identifier=returner&language=pt-PT"),processes=[returnerProcess])
        
        self.assertTrue(wpsTree.xpath("//ProcessDescription/ows:Title/text()",namespaces=wpsTree.nsmap)[0] in ptTranslations)
        self.assertTrue(wpsTree.xpath("//ProcessDescription/ows:Abstract/text()",namespaces=wpsTree.nsmap)[0] in ptTranslations)
        inputTitles=wpsTree.xpath("//DataInputs/Input/ows:Title/text()",namespaces=wpsTree.nsmap)
        inputAbstracts=wpsTree.xpath("//DataInputs/Input/ows:Abstract/text()",namespaces=wpsTree.nsmap)
        self.assertTrue((set(inputTitles) <= set(ptTranslations)) and len(inputTitles)!=0)
        self.assertTrue((set(inputAbstracts) <= set(ptTranslations)) and len(inputAbstracts)!=0)
        outputTitles=wpsTree.xpath("//ProcessOutputs/Output/ows:Title/text()",namespaces=wpsTree.nsmap)
        outputAbstracts=wpsTree.xpath("//DataInputs/Input/ows:Abstract/text()",namespaces=wpsTree.nsmap)
        self.assertTrue((set(outputTitles) <= set(ptTranslations)) and len(outputTitles)!=0)
        
        
           
    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")

if __name__ == "__main__":
   # unittest.main()
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestGetTestCase)
   unittest.TextTestRunner(verbosity=2).run(suite)
