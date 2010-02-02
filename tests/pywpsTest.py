import pywps
from  pywps import Process
import unittest

class ProcessTestCase(unittest.TestCase):

    def setUp(self):
        self.process =  pywps.Process.WPSProcess(identifier="testProcess")
        self.complexInput = None

    def testCreateWPSProcess(self):
        self.assertTrue(self.process)
    
    def testAddComplexInput(self):
        self.complexInput = self.process.addComplexInput(identifier="complexinput",
                title="Complex input")

    def testAddLiteralInput(self):
        self.literalInput = self.process.addComplexInput(identifier="literalinput",
                title="Complex input")

    def testProcessFromEnvironmentVariable(self):
        import os
        os.environ["PYWPS_PROCESS"] = "processes"
        os.putenv("PYWPS_PROCESS","processes")

        wps = pywps.Pywps(pywps.METHOD_GET)
        wps.inputs = {"request":"getcapabilities","version":"1.0.0","language":"eng"}
        from pywps.Wps.GetCapabilities import GetCapabilities
        request = GetCapabilities(wps)

if __name__ == "__main__":
    unittest.main()
