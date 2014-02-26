"""Test parsing of BoundingBoxInput
"""

import os
import sys
from io import StringIO
from lxml import objectify

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],"..",".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

class ParseBBoxInputTestCase(unittest.TestCase):

    def setUp(self):
        self.skipTest("BoundingBoxInput api has changed")
        self.inpt = BoundingBoxInput("bbox")

    def test_parse_bbox_input_GET(self):

        # testing basic parsing
        request="bbox=1,2,3,4"
        self.inpt.parse_url(request)
        self.assertEquals(1,self.inpt.get_value().left)
        self.assertEquals(2,self.inpt.get_value().dimensions)

        # parse crs
        request="bbox=1,2,3,4,epsg:4326"
        self.inpt.parse_url(request)
        self.assertEquals("EPSG:4326",self.inpt.get_crs(1).getcode())

    def test_parse_bbox_input_POST(self):
        """Parse bounding box input XML"""

        req_str = StringIO("""<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
			<ows:Identifier>bbox</ows:Identifier>
			<ows:Title>Bounding box title</ows:Title>
                        <ows:BoundingBox xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                            xsi:schemaLocation="http://www.opengis.net/ows/1.1 owsCommon.xsd"
                            crs="urn:ogc:crs:EPSG:6.3:26986" dimensions="2">
                            <!-- Example. Primary editor: Arliss Whiteside. Last updated 2005- 01-25 -->
                            <ows:LowerCorner>189000 834000</ows:LowerCorner>
                            <ows:UpperCorner>285000 962000</ows:UpperCorner>
                            </ows:BoundingBox>
                        </wps:Input>""")

        request = objectify.parse(req_str)
        self.inpt.parse_xml(request.getroot())
        self.assertEquals(189000,self.inpt.get_value(2).left)
        self.assertEquals(962000,self.inpt.get_value(2).top)
        self.assertEquals(26986,self.inpt.get_crs(2).code)
        self.assertEquals(2,self.inpt.get_dimensions(2))
        pass

    def test_parse_bbox_wgs84_POST(self):
        """Parse bounding box input XML as WGS84"""

        req_str = StringIO("""<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
			<ows:Identifier>bbox</ows:Identifier>
			<ows:Title>Bounding box WGS84 title</ows:Title>
             <ows:WGS84BoundingBox xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/ows/1.1 owsCommon.xsd">
            <!-- Example. Primary editor: Arliss Whiteside. Last updated 2004/10/13. -->
            <ows:LowerCorner>-71.63 41.75</ows:LowerCorner>
            <ows:UpperCorner>-70.78 42.90</ows:UpperCorner>
            </ows:WGS84BoundingBox>
            </wps:Input>""")

        request = objectify.parse(req_str)
        self.inpt.parse_xml(request.getroot())
        self.assertEquals(-71.63,self.inpt.get_value(3).left)
        self.assertEquals(42.90,self.inpt.get_value(3).top)
        self.assertEquals("EPSG:4326",self.inpt.get_value(3).get_crs().getcode())
        pass


if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseBBoxInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
