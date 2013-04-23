import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.request.describeprocess import DescribeProcess

class RequestParseDescribeProcessTestCase(unittest.TestCase):

    test_values = {
            "version":"1.0.0",
            "language":"eng",
            "request":"describeprocess",
            "service":"wps",
            "identifier":["intersection","union"]
    }

    def setUp(self):
        self.dp = DescribeProcess()
        self.dp.validate = True

    def testParseDescribeProcessGET(self):
        """Test if DescribeProcess request is parsed and if GET
        methods are producing the same result"""

        self.dp.parse("service=wps&request=describeprocess&version=1.0.0&identifier=intersection,union")

        self.assertEquals(self.dp.service, self.test_values["service"])
        self.assertEquals(self.dp.version, self.test_values["version"])
        self.assertEquals(self.dp.language, self.test_values["language"])
        self.assertEquals(self.dp.identifier, self.test_values["identifier"])

    def testParseDescribeProcessPOST(self):
        """Test if DescribeProcess request is parsed and if GET
        methods are producing the same result"""

        rfile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_request.xml"))

        self.dp.parse(rfile)

        self.assertEquals(self.dp.service, self.test_values["service"])
        self.assertEquals(self.dp.version, self.test_values["version"])
        self.assertEquals(self.dp.language, self.test_values["language"])
        self.assertEquals(self.dp.identifier, self.test_values["identifier"])
        print "############################x"


if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseDescribeProcessTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
