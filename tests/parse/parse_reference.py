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

from pywps.process.inout.reference import Reference

class ParseReferenceTestCase(unittest.TestCase):

    def setUp(self):

        self.ref = Reference()

    def test_parse_reference_GET(self):
        """Parse complex input KVP reference"""

        url = "http://foo/bar.tif@schema=http://foo/xsd@encoding=utf-8@mimetype=image/tiff"
        self.ref.set_from_url(url)

        self.assertEquals(self.ref.schema,"http://foo/xsd")
        self.assertEquals(self.ref.encoding,"utf-8")
        self.assertEquals(self.ref.mimetype,"image/tiff")
        self.assertEquals(self.ref.href,"http://foo/bar.tif")
        self.assertEquals(self.ref.method,"GET")

        pass

    def test_parse_reference_GET_href(self):
        """Parse complex input KVP reference with href attribut"""

        url = "@schema=http://foo/xsd@encoding=utf-8@mimetype=image/tiff@href=http://foo/bar.tif"
        self.ref.set_from_url(url)

        self.assertEquals(self.ref.schema,"http://foo/xsd")
        self.assertEquals(self.ref.encoding,"utf-8")
        self.assertEquals(self.ref.mimetype,"image/tiff")
        self.assertEquals(self.ref.href,"http://foo/bar.tif")
        self.assertEquals(self.ref.method,"GET")

        pass

    def test_parse_reference_POST(self):
        """Parse complex input XML reference, post method"""
        
        strin = StringIO("""<wps:Reference xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wps="http://www.opengis.net/wps/1.0.0" xlink:href="http://foo/bar.tif" method="GET"/>""")

        req = objectify.parse(strin)
        self.ref.set_from_xml(req.getroot())

        self.assertEquals(self.ref.href,"http://foo/bar.tif")
        self.assertEquals(self.ref.method,"GET")

    def _test_parse_reference_POST_body(self):
        """Parse complex input XML reference, post method"""
        
        strin = StringIO("""<wps:Reference xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wps="http://www.opengis.net/wps/1.0.0" xlink:href="http://foo/bar.tif" method="GET">
                            <wps:Header key1="value1" key2="value2" key3="value3" />
                            <wps:Body><body /></wps:Body>
                """)

        req = objectify.parse(strin)
        self.ref.set_from_xml(req.getroot())

        self.assertEquals(self.ref.href,"http://foo/bar.tif")
        self.assertEquals(self.ref.method,"GET")


        pass

    def _test_parse_reference_POST_bodyref(self):
        """Parse complex input XML reference, post method, body reference"""
        
        strin = StringIO("""<wps:Reference xmlns:xlink="" xmlns:wps="" xlink:href="http://foo/bar.tif" method="GET">
                            <wps:BodyReference href="http://foo/bar/reference" />
                """)

        req = objectify.parse(strin)
        self.ref.set_from_xml(req.getroot())

        self.assertEquals(self.ref.href,"http://foo/bar.tif")
        self.assertEquals(self.ref.method,"GET")

if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseReferenceTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
