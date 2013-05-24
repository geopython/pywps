"""Test parsing of Reference
"""

import os
import sys
from io import StringIO
from lxml import objectify

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],"..",".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.process.inout.complex import ComplexInput

class ParseReferenceTestCase(unittest.TestCase):

    def setUp(self):

        self.inpt = ComplexInput("input")

    def test_parse_reference_GET(self):
        """Parse complex input KVP reference"""

        url = "http://foo/bar.tif@schema=http://foo/xsd@encoding=utf-8@mimetype=image/tiff"
        self.inpt.set_from_url(url)

        self.assertEquals(self.inpt.reference.href,"http://foo/bar.tif")
        self.assertEquals(self.inpt.reference.method,"GET")
        self.assertEquals(self.inpt.schema,"http://foo/xsd")
        self.assertEquals(self.inpt.encoding,"utf-8")
        self.assertEquals(self.inpt.mimetype,"image/tiff")
        pass

    def test_parse_reference_GET_href(self):
        """Parse complex input KVP reference with href attribut"""

        url = "@schema=http://foo/xsd@encoding=utf-8@mimetype=image/tiff@href=http://foo/bar.tif"
        self.inpt.set_from_url(url)

        self.assertEquals(self.inpt.schema,"http://foo/xsd")
        self.assertEquals(self.inpt.encoding,"utf-8")
        self.assertEquals(self.inpt.mimetype,"image/tiff")
        self.assertEquals(self.inpt.reference.href,"http://foo/bar.tif")
        self.assertEquals(self.inpt.reference.method,"GET")

        pass

    def test_parse_reference_POST(self):
        """Parse complex input XML reference, post method"""
        
        strin = StringIO("""<wps:Reference xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wps="http://www.opengis.net/wps/1.0.0" xlink:href="http://foo/bar.tif" method="GET"/>""")

        req = objectify.parse(strin)
        self.inpt.set_from_xml(req.getroot())

        self.assertEquals(self.inpt.reference.href,"http://foo/bar.tif")
        self.assertEquals(self.inpt.reference.method,"GET")

    def test_parse_reference_POST_body(self):
        """Parse complex input XML reference, post method"""
        
        strin = StringIO("""<wps:Reference xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wps="http://www.opengis.net/wps/1.0.0" xlink:href="http://foo/bar.tif" method="GET">
                            <wps:Header key1="value1" key2="value2" key3="value3" />
                            <wps:Body><body /></wps:Body>
                            </wps:Reference>
                """)

        req = objectify.parse(strin)
        self.inpt.set_from_xml(req.getroot())

        self.assertEquals(self.inpt.reference.href,"http://foo/bar.tif")
        self.assertDictEqual({"key1":"value1",'key2': 'value2','key3': 'value3'}, self.inpt.reference.header)
        self.assertEquals(b"""<wps:Body xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xlink="http://www.w3.org/1999/xlink"><body/></wps:Body>""", self.inpt.reference.body)

        pass

    def test_parse_reference_POST_bodyref(self):
        """Parse complex input XML reference, post method, body reference"""
        
        strin = StringIO("""<wps:Reference xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wps="http://www.opengis.net/wps/1.0.0" xlink:href="http://foo/bar.tif" method="GET">
                            <wps:BodyReference xlink:href="http://foo/bar/reference" />
                        </wps:Reference>""")

        req = objectify.parse(strin)
        self.inpt.set_from_xml(req.getroot())

        self.assertEqual("http://foo/bar/reference", self.inpt.reference.bodyref)

if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseReferenceTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
