import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.request.getcapabilities import GetCapabilities
from pywps import request

class RequestParseGetCapabilitiesTestCase(unittest.TestCase):
    """Test case for input parsing"""
    
    test_values = {
            "version":"1.0.0",
            "service":"wps",
            "request":"getcapabilities",
            "language":"cz"
    }
    
    def setUp(self):
        self.gc = GetCapabilities()
        self.gc.validate = True

    def testParseGetCapabilitiesGET(self):
        """Test if GetCapabilities request is parsed and if GET methods do 
        get the same result"""
        

        self.gc.set_from_url(request.parse_params(
                                "service=wps&request=getcapabilities&language=cz"))

        self.assertEquals(self.gc.version, self.test_values["version"])
        self.assertEquals(self.gc.request, self.test_values["request"])
        self.assertEquals(self.gc.service, self.test_values["service"])
        self.assertEquals(self.gc.lang,self.test_values["language"])

    def testParseGetCapabilitiesPOST(self):
        """Test if GetCapabilities request is parsed and if POST methods do get the same result"""

        getCapabilitiesRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request.xml"))

        self.gc.set_from_xml(request.parse_xml(getCapabilitiesRequestFile))

        self.assertEquals(self.gc.version, self.test_values["version"])
        self.assertEquals(self.gc.request, self.test_values["request"])
        self.assertEquals(self.gc.service, self.test_values["service"])
        self.assertEquals(self.gc.lang,self.test_values["language"])
#
#    ######################################################################################
#    def testParseExecuteNoInput(self):
#        """Test if Execute request is parsed, no input given"""
#        
#        getpywps = pywps.Pywps(pywps.METHOD_GET)
#        postpywps = pywps.Pywps(pywps.METHOD_POST)
#        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=noinputprocess")
#        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-noinputs.xml"))
#        postinputs = postpywps.parseRequest(executeRequestFile)
#
#        self.assertEquals(getinputs["request"], "execute")
#        self.assertTrue("noinputprocess" in getinputs["identifier"],"noinputsprocess not found in %s"%getinputs)
#        
#        self.assertEquals(postinputs["request"], "execute")
#        self.assertTrue("noinputprocess" in postinputs["identifier"],"noinputsprocess not found in %s"%postinputs)
#
#        self.assertEquals(getinputs, postinputs,"Get and Post inputs are not same:\n%s\n%s" % (getinputs,postinputs))
#
#    def testParseExecuteLiteralInput(self):
#        """Test if Execute request is parsed, literal data inputs, including '@' in GET """
#        
#        #NOTE: Unittest changed after SVN: 1146 to check for the parsing of "@"
#        
#        getpywps = pywps.Pywps(pywps.METHOD_GET)
#        postpywps = pywps.Pywps(pywps.METHOD_POST)
#        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-literalinput.xml"))
#        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=literalprocess&datainputs=[int=1;string=spam%40foo.com@mimetype=text/plain@xlink:href=http%3A//www.w3.org/TR/xmlschema-2/%23string;float=1.1]")
#        postinputs = postpywps.parseRequest(executeRequestFile)
#
#        self.assertEquals(getinputs["request"], "execute")
#        self.assertTrue("literalprocess" in getinputs["identifier"])
#        
#        self.assertEquals(postinputs["request"], "execute")
#        self.assertTrue("literalprocess" in postinputs["identifier"])
#
#        #self.assertEquals(getinputs, postinputs)
#        self.assertEquals(getinputs["datainputs"][0]["value"],postinputs["datainputs"][0]["value"])
#        self.assertEquals(getinputs["datainputs"][1]["value"],postinputs["datainputs"][1]["value"])
#        self.assertEquals(getinputs["datainputs"][2]["value"],postinputs["datainputs"][2]["value"])
#        self.assertTrue(getinputs["datainputs"][0]["value"],1)
#        self.assertTrue(getinputs["datainputs"][1]["value"],"spam%40foo.com")
#        self.assertTrue(getinputs["datainputs"][2]["value"],"1.1")
#
#
#    def testParseExecuteComplexInputAsReference(self):
#        """Test if Execute request is parsed, complex data inputs, given as reference"""
#        
#        getpywps = pywps.Pywps(pywps.METHOD_GET)
#        postpywps = pywps.Pywps(pywps.METHOD_POST)
#        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-as-reference.xml"))
#        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=complexprocess&datainputs=[rasterin=%s;vectorin=%s]" %\
#                (urllib.quote(self.wfsurl), urllib.quote(self.wcsurl)))
#        #print "service=wps&version=1.0.0&request=execute&identifier=complexprocess&datainputs=[rasterin=%s;vectorin=%s]" % (urllib.quote(self.wfsurl), urllib.quote(self.wcsurl))
#        postinputs = postpywps.parseRequest(executeRequestFile)
#
#        self.assertEquals(getinputs["request"], "execute")
#        self.assertEquals(postinputs["request"], "execute")
#        self.assertTrue("complexprocess" in getinputs["identifier"])
#        self.assertTrue("complexprocess" in postinputs["identifier"])
#        
#        #self.assertEquals(getinputs, postinputs)
#        self.assertEquals(getinputs["datainputs"][0]["value"],postinputs["datainputs"][0]["value"])
#        self.assertEquals(getinputs["datainputs"][1]["value"],postinputs["datainputs"][1]["value"])
#
#    def testParseBBoxInput(self):
#        """Parsing Bounding Box Input"""
#        getpywps = pywps.Pywps(pywps.METHOD_GET)
#        postpywps = pywps.Pywps(pywps.METHOD_POST)
#        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-bbox.xml"))
#        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=bboxprocess&datainputs=[bboxin=%s]" %\
#                ("-11,-12,13,14"))
#        postinputs = postpywps.parseRequest(executeRequestFile)
#
#        self.assertTrue("bboxprocess" in getinputs["identifier"])
#        self.assertTrue("bboxprocess" in postinputs["identifier"])
#
#        self.assertEquals(getinputs["datainputs"][0]["value"],"-11,-12,13,14")
#        self.assertEquals(postinputs["datainputs"][0]["value"],[-11,-12,13,14])
#
#    def testParseRawDataOutput(self):
#        """Test, if PyWPS parsers RawData output request correctly"""
#        postpywps = pywps.Pywps(pywps.METHOD_POST)
#        getpywps = pywps.Pywps(pywps.METHOD_GET)
#        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-direct-rawdata-output.xml"))
#        postinputs = postpywps.parseRequest(executeRequestFile)
#        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=literalprocess&datainputs=[int=1;string=spam;float=1.1]&rawdataoutput=string")
#
#        self.assertFalse(postinputs["responseform"]["responsedocument"])
#        self.assertTrue(postinputs["responseform"]["rawdataoutput"]["rasterout"])
#
#        self.assertFalse(getinputs["responseform"]["responsedocument"])
#        self.assertTrue(getinputs["responseform"]["rawdataoutput"]["string"])
#
#    def testParseExecuteComplexInputDirectly(self):
#        """Test if Execute request is parsed, complex data inputs, given as """
#
#        postpywps = pywps.Pywps(pywps.METHOD_POST)
#        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-direct.xml"))
#        postinputs = postpywps.parseRequest(executeRequestFile)
#
#        self.assertEquals(postinputs["request"], "execute")
#        self.assertTrue("complexprocess" in postinputs["identifier"])
#        rasterOrig = open(os.path.join(pywpsPath,"tests","datainputs","dem.tiff"))
#        rasterOrigData = rasterOrig.read()
#        rasterWpsData = base64.decodestring(postinputs["datainputs"][0]["value"])
#
#        self.assertEquals(rasterOrigData, rasterWpsData)
#
#
#        gmlDriver = ogr.GetDriverByName("GML")
#        origDs = gmlDriver.Open(os.path.join(pywpsPath,"tests","datainputs","lakes.gml"))
#
#        wpsFile = tempfile.mktemp(prefix="pywps-test")
#        wpsFile = open(wpsFile,"w")
#        wpsFile.write(postinputs["datainputs"][1]["value"])
#        wpsFile.close()
#        wpsDs = gmlDriver.Open(wpsFile.name)
#
#        wpslayer = wpsDs.GetLayerByIndex(0)
#        origlayer = origDs.GetLayerByIndex(0)
#
#        self.assertTrue(wpslayer.GetFeatureCount(), origlayer.GetFeatureCount())
#
#        # enough  here
#        # for f in range(wpslayer.GetFeatureCount()):
#        #     origFeature = origlayer.GetFeature(f)
#        #     wpsFeature = wpslayer.GetFeature(f)
#        #     self.assertTrue(origFeature.Equal(wpsFeature))
#
#    def testParseExecuteComplexAsReferenceOut(self):
#        """Test if Execute request is parsed, we want data outputs as reference"""
#        self._setFromEnv()
#        postpywps = pywps.Pywps(pywps.METHOD_POST)
#        getpywps = pywps.Pywps(pywps.METHOD_GET)
#        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-output-as-reference.xml"))
#        postinputs = postpywps.parseRequest(executeRequestFile)
#        getinputs = getpywps.parseRequest("service=wps&request=execute&version=1.0.0&identifier=complexprocess&datainputs=[rasterin=http://foo/bar/raster.tif;vectorin=http://foo/bar/vector.gml]&responsedocument=[rasterout=@asreference=true;vectorout=@asreference=true]")
#
#        self.assertTrue(postinputs["responseform"]["responsedocument"]["outputs"][0]["asreference"] == \
#                        postinputs["responseform"]["responsedocument"]["outputs"][0]["asreference"] == \
#                        True)
#
#        self.assertTrue(postinputs["responseform"]["responsedocument"]["outputs"][1]["asreference"] == \
#                        postinputs["responseform"]["responsedocument"]["outputs"][1]["asreference"] == \
#                        True)


    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
  

    
if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseGetCapabilitiesTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
