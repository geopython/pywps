import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.request.describeprocess import DescribeProcess

class RequestParseDescribeProcessTestCase(unittest.TestCase):

    def setUp(self):
        self.dp = DescribeProcess()


    def testParseDescribeProcessGET(self):
        """Test if DescribeProcess request is parsed and if GET
        methods are producing the same result"""

        return
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


if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseDescribeProcessTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
