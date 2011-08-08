import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
#sys.path.append(pywpsPath)
sys.path.insert(0,pywpsPath)
import pywps
import pywps.Process
import unittest
import os
from xml.dom import minidom
import base64
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

class RequestGetTestCase(unittest.TestCase):
    inputs = None
    getcapabilitiesrequest = "service=wps&request=getcapabilities"
    getdescribeprocessrequest = "service=wps&request=describeprocess&version=1.0.0&identifier=dummyprocess"
    getdescribeprocessrequestall = "service=wps&request=describeprocess&version=1.0.0&identifier=all"
    getexecuterequest = "service=wps&request=execute&version=1.0.0&identifier=dummyprocess&datainputs=[input1=20;input2=10]"
    #wfsurl = "http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.0.0&request=getfeature&service=wfs&typename=park"
    wfsurl = "http://rsg.pml.ac.uk/geoserver2/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=rsg:areas_pw&maxFeatures=1"
    wcsurl = "http://www.bnhelp.cz/cgi-bin/crtopo?service=WMS&request=GetMap&LAYERS=sitwgs&TRANSPARENT=true&FORMAT=image%2Ftiff&EXCEPTIONS=application%2Fvnd.ogc.se_xml&VERSION=1.1.1&STYLES=default&SRS=EPSG%3A4326&BBOX=-10,-10,10,10&WIDTH=50&HEIGHT=50"
    wpsns = "http://www.opengis.net/wps/1.0.0"
    owsns = "http://www.opengis.net/ows/1.1"
    ogrns = "http://ogr.maptools.org/"
    xmldom = None


    def testT00Assync(self):
        """Test assynchronous mode for the first time"""
       

        self._setFromEnv()
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest("service=wps&request=execute&version=1.0.0&identifier=assyncprocess&status=true&storeExecuteResponse=true")
        self.assertEquals(mypywps.inputs["request"], "execute")
        self.assertTrue("assyncprocess" in mypywps.inputs["identifier"])
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
        getpywps.parseRequest(self.getdescribeprocessrequestall)
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
        
        import urllib
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
        #print postxmldom.toxml()         
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
  
    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
        

if __name__ == "__main__":
   #unittest.main()
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestGetTestCase)
   unittest.TextTestRunner(verbosity=2).run(suite)
