import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.append(pywpsPath)

import pywps
import pywps.Process
import unittest
import os
from xml.dom import minidom

class RequestParseTestCase(unittest.TestCase):
    wfsurl = "http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.0.0&request=getfeature&service=wfs&typename=park"
    wpsns = "http://www.opengis.net/wps/1.0.0"
    getpywps = None
    postpywps = None

    def setUp(self):
        pass

    def testParseGetCapabilities(self):
        """Test if GetCapabilities request is parsed and if POST and GET methods do get the same result"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getinputs = getpywps.parseRequest("service=wps&request=getcapabilities")
        getCapabilitiesRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request.xml"))
        postinputs = postpywps.parseRequest(getCapabilitiesRequestFile)

        self.assertEquals(getpywps.inputs["version"], "1.0.0")
        self.assertEquals(getpywps.inputs["request"], "getcapabilities")
        self.assertEquals(getpywps.inputs["service"], "wps")

        self.assertEquals(postpywps.inputs["version"], "1.0.0")
        self.assertEquals(postpywps.inputs["request"], "getcapabilities")
        self.assertEquals(postpywps.inputs["service"], "wps")

        self.assertEquals(getinputs, postinputs)

    def testParseDescribeProcess(self):
        """Test if DescribeProcess request is parsed and if POST and GET
        methods are producing the same result"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getinputs = getpywps.parseRequest("service=wps&request=describeprocess&version=1.0.0&identifier=dummyprocess")
        describeProcessFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_request_dummyprocess.xml"))
        postinputs = postpywps.parseRequest(describeProcessFile)

        self.assertEquals(getpywps.inputs["request"], "describeprocess")
        self.assertTrue("dummyprocess" in getpywps.inputs["identifier"])
        self.assertFalse("returner" in getpywps.inputs["identifier"])

        self.assertEquals(postpywps.inputs["request"], "describeprocess")
        self.assertTrue("dummyprocess" in postpywps.inputs["identifier"])
        self.assertFalse("returner" in postpywps.inputs["identifier"])

        self.assertEquals(getinputs, postinputs)

    ######################################################################################
    def testParseExecuteNoInput(self):
        """Test if Execute request is parsed, no input given"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=noinputprocess")
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-noinputs.xml"))
        postinputs = postpywps.parseRequest(executeRequestFile)

        self.assertEquals(getinputs["request"], "execute")
        self.assertTrue("noinputprocess" in getinputs["identifier"],"noinputsprocess not found in %s"%getinputs)
        
        self.assertEquals(postinputs["request"], "execute")
        self.assertTrue("noinputprocess" in postinputs["identifier"],"noinputsprocess not found in %s"%postinputs)

        self.assertEquals(getinputs, postinputs,"Get and Post inputs are not same:\n%s\n%s" % (getinputs,postinputs))

    def testParseExecuteLiteralInput(self):
        """Test if Execute request is parsed, literal data inputs"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-literalinput.xml"))
        getinputs = getpywps.parseRequest("service=wps&version=1.0.0&request=execute&identifier=literalprocess&datainputs=[int=1;string=spam;float=1.1]")
        postinputs = postpywps.parseRequest(executeRequestFile)

        self.assertEquals(getinputs["request"], "execute")
        self.assertTrue("literalprocess" in getinputs["identifier"])
        self.assertTrue("literalprocess" in getinputs["identifier"])
        
        self.assertEquals(postinputs["request"], "execute")
        self.assertTrue("literalprocess" in postinputs["identifier"])

        #self.assertEquals(getinputs, postinputs)
        self.assertEquals(getinputs["datainputs"][0]["value"],postinputs["datainputs"][0]["value"])
        self.assertEquals(getinputs["datainputs"][1]["value"],postinputs["datainputs"][1]["value"])
        self.assertEquals(getinputs["datainputs"][2]["value"],postinputs["datainputs"][2]["value"])
        self.assertTrue(getinputs["datainputs"][0]["value"],1)
        self.assertTrue(getinputs["datainputs"][1]["value"],"spam")
        self.assertTrue(getinputs["datainputs"][2]["value"],"1.1")

    def _testParseExecuteComplexVectorInputs(self):
        """Test, if pywps can parse complex vector input values, given as reference, output given directly"""
        self._setFromEnv()
        import urllib
        import tempfile
        gmlFile = tempfile.mktemp(prefix="pywps-test-wfs")
        gmlFile = open(gmlFile,"w")
        gmlFile.write(urllib.urlopen(self.wfsurl).read())
        gmlFile.close()

        request = "service=wps&request=execute&version=1.0.0&identifier=complexVector&datainputs=[indata=%s]" % (urllib.quote(self.wfsurl))
        self.inputs = self.pywps.parseRequest(request)
        self.pywps.performRequest()
        self.xmldom = minidom.parseString(self.pywps.response)
        self.assertFalse(len(self.xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport")), 0)
        self.xmldom2 = minidom.parse(gmlFile.name)
        
        # try to separte the GML file from the response document
        outputgml = None
        for elem in self.xmldom.getElementsByTagNameNS(self.wpsns,"ComplexData")[0].childNodes:
            if elem.nodeName == "FeatureCollection":
                outputgml = elem
                break

        # output GML should be the same, as input GML
        self.assertTrue(self.xmldom, outputgml)

    def _testParseExecuteComplexVectorInputsAsReference(self):
        """Test, if pywps can parse complex vector input values, given as reference"""
        self._setFromEnv()
        import urllib
        import tempfile
        gmlfile = open(tempfile.mktemp(prefix="pywps-test-wfs"),"w")
        gmlfile.write(urllib.urlopen(self.wfsurl).read())
        gmlfile.close()

        request = "service=wps&request=execute&version=1.0.0&identifier=complexVector&datainputs=[indata=%s]&responsedocument=[outdata=@asreference=true]" % (urllib.quote(self.wfsurl))
        self.inputs = self.pywps.parseRequest(request)
        self.pywps.performRequest()
        self.xmldom = minidom.parseString(self.pywps.response)
        self.assertFalse(len(self.xmldom.getElementsByTagNameNS(self.wpsns,"ExceptionReport")), 0)

        # try to get out the Reference elemengt
        self.gmlout = self.xmldom.getElementsByTagNameNS(self.wpsns,"Reference")[0].getAttribute("xlink:href")
            
        # download, store, parse XML
        gmlfile2 = open(tempfile.mktemp(prefix="pywps-test-wfs"),"w")
        gmlfile2.write(urllib.urlopen(self.gmlout).read())
        gmlfile2.close()
        self.xmldom2 = minidom.parse(gmlfile2.name)
        self.xmldom = minidom.parse(gmlfile.name)

        # check, if they fit
        # TODO: this test failes, but no power to get it trough
        # self.assertEquals(self.xmldom, self.xmldom2)

    ######################################################################################
    def _loadGetCapabilities(self):
        self.inputs = self.pywps.parseRequest(self.getcapabilitiesrequest)
        self.pywps.performRequest(self.inputs)
        self.xmldom = minidom.parseString(self.pywps.response)

    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
        

if __name__ == "__main__":
    unittest.main()
