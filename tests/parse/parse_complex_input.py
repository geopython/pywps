"""Test parsing of ComplexInput
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

class ParseComplexInputTestCase(unittest.TestCase):

    def setUp(self):
        self.inpt = ComplexInput("")

    def test_parse_complex_input_GET_1(self):
        """Parse GET KVP complex input"""

        # @xlink:href at beginning
        request="InputPolygon=@xlink:href=http%3A%2F%2Ffoo.bar%2Fsome_WFS_request.xml"
        self.inpt.set_from_url(request)
        self.assertTrue(self.inpt.reference)
        self.assertEquals(self.inpt.reference.href,"http://foo.bar/some_WFS_request.xml")

    def test_parse_complex_input_GET_2(self):
        # @xlink:href and other attributes
        request="InputPolygon=@xlink:href=http%3A%2F%2Ffoo.bar%2Fsome_WFS_request.xml@method=POST@mimeType=text/xml@encoding=UTF-8@schema=http%3A%2F%2Ffoo.bar%2Fgml_polygon_schema.xsd"
        self.inpt.set_from_url(request)
        self.assertTrue(self.inpt.reference)
        self.assertEquals(self.inpt.reference.href,"http://foo.bar/some_WFS_request.xml")
        self.assertEquals(self.inpt.reference.method,"POST")
        self.assertEquals(self.inpt.mimetype,"text/xml")
        self.assertEquals(self.inpt.schema,"http://foo.bar/gml_polygon_schema.xsd")
        self.assertEquals(self.inpt.encoding,"UTF-8")

    #def test_parse_complex_input_GET_3(self):
    #    # href at beginning as value
    #    request="InputPolygon=http%3A%2F%2Ffoo.bar%2Fsome_WFS_request.xml@schema=http://foo/bar/xsd"
    #    self.inpt.set_from_url(request)
    #    self.assertTrue(self.inpt.reference)
    #    self.assertEquals(self.inpt.reference.href,"http://foo.bar/some_WFS_request.xml")
    #    self.assertEquals(self.inpt.reference.method,"POST")

    def test_parse_complex_input_GET_json(self):
        from urllib.parse import quote
        poly = '{"type":"FeatureCollection","features":[{"geometry":{"type":"GeometryCollection","geometries":[{"type":"LineString","coordinates":[[11.0878902207,45.1602390564],[15.01953125,48.1298828125]]},{"type":"Polygon","coordinates":[[[11.0878902207,45.1602390564],[14.931640625,40.9228515625],[0.8251953125,41.0986328125],[7.63671875,48.96484375],[11.0878902207,45.1602390564]]]},{"type":"Point","coordinates":[15.87646484375,44.1748046875]}]},"type":"Feature","properties":{}}]}'
        request="""InputPolygon=%s@mimeType=application/geojson"""% quote(poly)

        self.inpt.set_from_url(request)
        self.assertFalse(self.inpt.reference)
        self.assertEquals(self.inpt.getValue(),poly)
        self.assertEquals(self.inpt.mimetype,"application/geojson")

    def test_parse_complex_input_GET_gml_collection(self):

        from urllib.parse import quote
        poi = '''<wfs:FeatureCollection xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd http://mapserver.gis.umn.edu/mapserver http://aneto.oco/cgi-bin/worldwfs?SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=DescribeFeatureType&amp;TYPENAME=point&amp;OUTPUTFORMAT=XMLSCHEMA" xmlns:ms="http://mapserver.gis.umn.edu/mapserver" xmlns:wfs="http://www.opengis.net/wfs" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ms:msGeometry><gml:Point srsName="EPSG:4326"><gml:coordinates>-0.608315,44.857522</gml:coordinates></gml:Point></ms:msGeometry><ms:ogc_fid>1</ms:ogc_fid><ms:name>Bordeaux</ms:name><ms:id>124</ms:id></ms:point></gml:featureMember>'''

        request="""InputPolygon=%s@mimeType=application/gml@schema=http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd http://mapserver.gis.umn.edu/mapserver http://aneto.oco/cgi-bin/worldwfs?SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=DescribeFeatureType&amp;TYPENAME=point&amp;OUTPUTFORMAT=XMLSCHEMA"""% quote(poi)

        self.inpt.set_from_url(request)
        self.assertFalse(self.inpt.reference)
        self.assertEquals(self.inpt.getValue(),poi)
        self.assertEquals(self.inpt.mimetype,"application/gml")
        self.assertEquals(self.inpt.schema,"http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd http://mapserver.gis.umn.edu/mapserver http://aneto.oco/cgi-bin/worldwfs?SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=DescribeFeatureType&amp;TYPENAME=point&amp;OUTPUTFORMAT=XMLSCHEMA")


if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseComplexInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
