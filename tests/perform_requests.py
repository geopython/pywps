import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.append(pywpsPath)

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
    getexecuterequest = "service=wps&request=execute&version=1.0.0&identifier=dummyprocess&datainputs=[input1=20;input2=10]"
    wfsurl = "http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.0.0&request=getfeature&service=wfs&typename=park"
    wcsurl = "http://www.bnhelp.cz/cgi-bin/crtopo?service=WMS&request=GetMap&LAYERS=sitwgs&TRANSPARENT=true&FORMAT=image%2Ftiff&EXCEPTIONS=application%2Fvnd.ogc.se_xml&VERSION=1.1.1&STYLES=default&SRS=EPSG%3A4326&BBOX=-10,-10,10,10&WIDTH=50&HEIGHT=50"
    wpsns = "http://www.opengis.net/wps/1.0.0"
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
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getcapabilitiesrequest)
        mypywps.performRequest(inputs)
        xmldom = minidom.parseString(mypywps.response)
        self.assertEquals(xmldom.firstChild.nodeName, "wps:Capabilities")


    def testT02ProcessesLengthGetCapabilities(self):
        """Test, if any processes are listed in the Capabilities document
        """
        self._setFromEnv()
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getcapabilitiesrequest)
        mypywps.performRequest(inputs)
        xmldom = minidom.parseString(mypywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)
    

    def testT03PerformDescribeProcess(self):
        """Test if DescribeProcess request returns ProcessDescription document"""
        self._setFromEnv()
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        mypywps.parseRequest(self.getdescribeprocessrequest)
        mypywps.performRequest()
        xmldom = minidom.parseString(mypywps.response)
        self.assertEquals(xmldom.firstChild.nodeName, "wps:ProcessDescriptions")
    

    def testT04ProcessesLengthDescribeProcess(self):
        """Test, if any processes are listed in the DescribeProcess document
        """
        self._setFromEnv()
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        mypywps.parseRequest(self.getdescribeprocessrequest)
        mypywps.performRequest()
        xmldom = minidom.parseString(mypywps.response)
        self.assertTrue(len(xmldom.getElementsByTagName("ProcessDescription"))>0)
        self.assertEquals(len(xmldom.getElementsByTagName("ProcessDescription")),
                len(mypywps.inputs["identifier"]))

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
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=literalprocess&datainputs=[int=1;string=spam;float=1.1;zeroset=0.0]")
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-literalinput.xml"))
        postinputs = postpywps.parseRequest(executeRequestFile)

        getpywps.performRequest(getinputs)
        postpywps.performRequest(postinputs)
        getxmldom = minidom.parseString(getpywps.response)
        postxmldom = minidom.parseString(postpywps.response)

        getliteraldata = getxmldom.getElementsByTagNameNS(self.wpsns,"LiteralData")
        postliteraldata = postxmldom.getElementsByTagNameNS(self.wpsns,"LiteralData")
        self.assertEquals(len(getliteraldata),3)
        self.assertEquals(len(postliteraldata),3)

        self.assertEquals(getliteraldata[0].firstChild.nodeValue,
                postliteraldata[0].firstChild.nodeValue)
        self.assertEquals(getliteraldata[1].firstChild.nodeValue,
                postliteraldata[1].firstChild.nodeValue)
        self.assertEquals(getliteraldata[2].firstChild.nodeValue,
                postliteraldata[2].firstChild.nodeValue)

        self.assertEquals(getliteraldata[0].firstChild.nodeValue, "1")
        self.assertEquals(getliteraldata[2].firstChild.nodeValue, "spam")
        self.assertEquals(getliteraldata[1].firstChild.nodeValue, "1.1")
    

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
        inputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexprocessows&datainputs=[rasterin=%s;vectorin=%s]&responsedocument=[rasterout=@asreference=true;vectorout=@asreference=true]" % (urllib.quote(self.wcsurl), urllib.quote(self.wfsurl)))
        getpywps.performRequest()
        xmldom = minidom.parseString(getpywps.response)

        self.assertFalse(len(xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport")), 0)

        # try to get out the Reference elemengt
        wfsurl = xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[0].getAttribute("xlink:href")
        wcsurl = xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[1].getAttribute("xlink:href")

        # test, if there are WFS and WCS request strings
        self.assertTrue(wfsurl.find("WFS") > -1)
        self.assertTrue(wcsurl.find("WCS") > -1)
        #print urllib.unquote(wfsurl)
        #print urllib.unquote(wcsurl)
            

    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
        

if __name__ == "__main__":
   # unittest.main()
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestGetTestCase)
   unittest.TextTestRunner(verbosity=2).run(suite)
