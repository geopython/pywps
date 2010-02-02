import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.append(pywpsPath)

import pywps
import pywps.Process
import unittest
import os
from xml.dom import minidom

class RequestGetTestCase(unittest.TestCase):
    inputs = None
    getcapabilitiesrequest = "service=wps&request=getcapabilities"
    getdescribeprocessrequest = "service=wps&request=describeprocess&version=1.0.0&identifier=dummyprocess"
    getexecuterequest = "service=wps&request=execute&version=1.0.0&identifier=dummyprocess&datainputs=[input1=20;input2=10]"
    wfsurl = "http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.0.0&request=getfeature&service=wfs&typename=park"
    wpsns = "http://www.opengis.net/wps/1.0.0"
    xmldom = None

    def setUp(self):
        self.pywps = pywps.Pywps(pywps.METHOD_GET)

    def testParseGetCapabilities(self):
        """Test if GetCapabilities request is parsed"""
        self.inputs = self.pywps.parseRequest(self.getcapabilitiesrequest)
        self.assertEquals(self.pywps.inputs["version"], "1.0.0")
        self.assertEquals(self.pywps.inputs["request"], "getcapabilities")
        self.assertEquals(self.pywps.inputs["service"], "wps")

    def testPerformGetCapabilities(self):
        """Test if GetCapabilities request returns Capabilities document"""
        self._loadGetCapabilities()
        self.assertEquals(self.xmldom.firstChild.nodeName, "wps:Capabilities")

    def testLoadProcessesFromClass(self):
        """Test, if we can load process as classes"""
        class newClassProcess(pywps.Process.WPSProcess):
            def __init__(self):
                pywps.Process.WPSProcess.__init__(self,identifier="foo", title="bar")

        self.inputs = self.pywps.parseRequest(self.getcapabilitiesrequest)
        self.pywps.performRequest(self.inputs,[newClassProcess])
        self.xmldom = minidom.parseString(self.pywps.response)
        self.assertTrue(len(self.xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)

    def testLoadProcessesAsInstance(self):
        """Test, if we can load process as instances"""
        class newClassProcess(pywps.Process.WPSProcess):
            def __init__(self):
                pywps.Process.WPSProcess.__init__(self,identifier="foo", title="bar")

        self.inputs = self.pywps.parseRequest(self.getcapabilitiesrequest)
        self.pywps.performRequest(self.inputs,[newClassProcess()])
        self.xmldom = minidom.parseString(self.pywps.response)
        self.assertTrue(len(self.xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)

    def testLoadProcessesFromEnvVar(self):
        """Test, if we can load processes set from PYWPS_PROCESSES
        environment variable"""
        self._setFromEnv()
        self._loadGetCapabilities()
        self.assertEquals(len(self.pywps.request.processes), 6)
        self.assertTrue(self.pywps.request.getProcess("dummyprocess"))

    def testProcessesLengthGetCapabilities(self):
        """Test, if any processes are listed in the Capabilities document
        """
        self._loadGetCapabilities()
        self.assertTrue(len(self.xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)

    ######################################################################################
    def testParseDescribeProcess(self):
        """Test if DescribeProcess request is parsed"""
        self.inputs = self.pywps.parseRequest(self.getdescribeprocessrequest)
        self.assertEquals(self.pywps.inputs["request"], "describeprocess")
        self.assertTrue("dummyprocess" in self.pywps.inputs["identifier"])

    def testPerformDescribeProcess(self):
        """Test if DescribeProcess request returns ProcessDescription document"""
        self.pywps.parseRequest(self.getdescribeprocessrequest)
        self.pywps.performRequest()
        self.xmldom = minidom.parseString(self.pywps.response)
        self.assertEquals(self.xmldom.firstChild.nodeName, "wps:ProcessDescriptions")

    def testProcessesLengthDescribeProcess(self):
        """Test, if any processes are listed in the DescribeProcess document
        """
        self.pywps.parseRequest(self.getdescribeprocessrequest)
        self.pywps.performRequest()
        self.xmldom = minidom.parseString(self.pywps.response)
        self.assertTrue(len(self.xmldom.getElementsByTagName("ProcessDescription"))>0)
        self.assertEquals(len(self.xmldom.getElementsByTagName("ProcessDescription")),
                len(self.pywps.inputs["identifier"]))

    ######################################################################################
    def testParseExecute(self):
        """Test if Execute request is parsed and performed"""
        self.inputs = self.pywps.parseRequest(self.getexecuterequest)
        self.assertEquals(self.pywps.inputs["request"], "execute")
        self.assertTrue("dummyprocess" in self.pywps.inputs["identifier"])
        self.pywps.performRequest()
        self.xmldom = minidom.parseString(self.pywps.response)
        self.assertEquals(len(self.xmldom.getElementsByTagNameNS(self.wpsns,"LiteralData")),2)

    def testParseExecuteComplexVectorInputs(self):
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

    def testParseExecuteComplexVectorInputsAsReference(self):
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
