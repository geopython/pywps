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
        sys.stderr=open("/dev/null","w")
        
    def testLoadProcessesFromClass(self):
        """Test, if we can load process as classes"""
        class newClassProcess(pywps.Process.WPSProcess):
            def __init__(self):
                pywps.Process.WPSProcess.__init__(self,identifier="foo", title="bar")

        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getcapabilitiesrequest)
        mypywps.performRequest(self.inputs,[newClassProcess])
        xmldom = minidom.parseString(mypywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)

    def testLoadProcessesAsInstance(self):
        """Test, if we can load process as instances"""
        class newClassProcess(pywps.Process.WPSProcess):
            def __init__(self):
                pywps.Process.WPSProcess.__init__(self,identifier="foo", title="bar")

        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getcapabilitiesrequest)
        mypywps.performRequest(self.inputs,[newClassProcess()])
        xmldom = minidom.parseString(mypywps.response)
        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)

    def testLoadProcessesFromEnvVar(self):
        """Test, if we can load processes set from PYWPS_PROCESSES
        environment variable"""
        self._setFromEnv()
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getcapabilitiesrequest)
        mypywps.performRequest(inputs)
        xmldom = minidom.parseString(mypywps.response)
        self.assertEquals(len(mypywps.request.processes), 14)
        self.assertTrue(mypywps.request.getProcess("dummyprocess"))

    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
        

if __name__ == "__main__":
    # unittest.main()
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestGetTestCase)
   unittest.TextTestRunner(verbosity=2).run(suite)
