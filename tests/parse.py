import os,sys,io

import unittest
from lxml import etree
from lxml import objectify

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

from pywps import request

from parse_getcapabilities import *
from parse_describeprocess import *
from parse_describeprocess import *
from parse_input import *

class RequestParse(unittest.TestCase):
    """Test input parsing"""

    def test_capabilities_request(self):
        
        root = objectify.Element("{http://www.opengis.net/wps/1.0.0}GetCapabilities")
        url = "requesT=GetCApabilities"

        from pywps.request import getcapabilities

        # test xml
        r = request.get_request(io.BytesIO(etree.tostring(root)))
        self.assertTrue(isinstance(r,getcapabilities.GetCapabilities))

        # test url
        r = request.get_request(url)
        self.assertTrue(isinstance(r,getcapabilities.GetCapabilities))

    def test_describeprocess_request(self):
        root = objectify.Element("{http://www.opengis.net/wps/1.0.0}DescribeProcess",version="1.0.0")
        url = "requesT=DescribePROCESS&identifier=all"

        from pywps.request import describeprocess

        # test xml
        r = request.get_request(io.BytesIO(etree.tostring(root)))
        self.assertTrue(isinstance(r,describeprocess.DescribeProcess))

        # test url
        r = request.get_request(url)
        self.assertTrue(isinstance(r,describeprocess.DescribeProcess))

    def test_execute_request(self):
        root = objectify.Element("{http://www.opengis.net/wps/1.0.0}Execute")
        url = "requesT=ExecuTe&identifier=all"

        from pywps.request import execute

        # test xml
        r = request.get_request(io.BytesIO(etree.tostring(root)))
        self.assertTrue(isinstance(r,execute.Execute))

        # test url
        r = request.get_request(url)
        self.assertTrue(isinstance(r,execute.Execute))
        
def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(RequestParse)
    unittest.TextTestRunner(verbosity=2).run(suite)

    
    suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseGetCapabilitiesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseDescribeProcessTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseDescribeProcessTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(RequestInputTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
