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
    def _loadGetCapabilities(self):
        self.inputs = self.pywps.parseRequest(self.getcapabilitiesrequest)
        self.pywps.performRequest(self.inputs)
        self.xmldom = minidom.parseString(self.pywps.response)

    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
        

if __name__ == "__main__":
    unittest.main()
