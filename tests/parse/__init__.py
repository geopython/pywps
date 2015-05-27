import os,sys,io

import unittest
from lxml import etree
from lxml import objectify

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],"..",".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

from pywps import request

#from parse.parse_getcapabilities import *
#from parse.parse_describeprocess import *
from parse.parse_input import *
from parse.parse_literal_input import *
from parse.parse_bbox_input import *
from parse.parse_complex_input import *
from parse.parse_reference import *

class RequestParse(unittest.TestCase):
    """Test input parsing"""

#     def test_capabilities_request(self):
#         self.skipTest("Parser changed")
# 
#         root = objectify.Element("{http://www.opengis.net/wps/1.0.0}GetCapabilities")
#         url = "requesT=GetCApabilities"
# 
# 
#         # test xml
#         r = request.get_request(io.BytesIO(etree.tostring(root)))
#         self.assertTrue(isinstance(r,getcapabilities.GetCapabilities))
# 
#         # test url
#         r = request.get_request(url)
#         self.assertTrue(isinstance(r,getcapabilities.GetCapabilities))

#     def test_describeprocess_request(self):
#         self.skipTest("Parser changed")
#         root = objectify.Element("{http://www.opengis.net/wps/1.0.0}DescribeProcess",version="1.0.0")
#         url = "requesT=DescribePROCESS&identifier=all"
# 
#         from pywps.request import describeprocess
# 
#          test xml
#         r = request.get_request(io.BytesIO(etree.tostring(root)))
#         self.assertTrue(isinstance(r,describeprocess.DescribeProcess))
# 
#          test url
#         r = request.get_request(url)
#         self.assertTrue(isinstance(r,describeprocess.DescribeProcess))

    def test_execute_request(self):
        self.skipTest("Parser changed")
        root = objectify.Element("{http://www.opengis.net/wps/1.0.0}Execute")
        url = "requesT=ExecuTe&identifier=all"

        # test xml
        r = request.get_request(io.BytesIO(etree.tostring(root)))
        self.assertTrue(isinstance(r,execute.Execute))

        # test url
        r = request.get_request(url)
        self.assertTrue(isinstance(r,execute.Execute))

def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(RequestParse),
        #loader.loadTestsFromTestCase(RequestParseGetCapabilitiesTestCase),
        #loader.loadTestsFromTestCase(RequestParseDescribeProcessTestCase),
        #loader.loadTestsFromTestCase(RequestParseDescribeProcessTestCase),
        loader.loadTestsFromTestCase(RequestInputTestCase),
        loader.loadTestsFromTestCase(ParseLiteralInputTestCase),
        loader.loadTestsFromTestCase(ParseBBoxInputTestCase),
        loader.loadTestsFromTestCase(ParseComplexInputTestCase),
        loader.loadTestsFromTestCase(ParseReferenceTestCase),
    ]
    return unittest.TestSuite(suite_list)

def main():
    unittest.TextTestRunner(verbosity=2).run(load_tests())

if __name__ == "__main__":
    main()
