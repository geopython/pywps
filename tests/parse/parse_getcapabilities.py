import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],"..",".."))
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

    def _setFromEnv(self):
        os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath,"tests","processes"))
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
    
if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseGetCapabilitiesTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
