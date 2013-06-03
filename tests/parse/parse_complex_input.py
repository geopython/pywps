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

from pywps.request.execute.complex import ComplexInput

class ParseComplexInputTestCase(unittest.TestCase):

    def setUp(self):
        self.inpt = ComplexInput("InputPolygon")

    def test_parse_complex_input_GET_json(self):
        from urllib.parse import quote
        poly = '{"type":"FeatureCollection","features":[{"geometry":{"type":"GeometryCollection","geometries":[{"type":"LineString","coordinates":[[11.0878902207,45.1602390564],[15.01953125,48.1298828125]]},{"type":"Polygon","coordinates":[[[11.0878902207,45.1602390564],[14.931640625,40.9228515625],[0.8251953125,41.0986328125],[7.63671875,48.96484375],[11.0878902207,45.1602390564]]]},{"type":"Point","coordinates":[15.87646484375,44.1748046875]}]},"type":"Feature","properties":{}}]}'
        request="""InputPolygon=%s@mimeType=application/geojson"""% quote(poly)

        self.inpt.parse_url(request)

        inpt = self.inpt.get_input(len(self.inpt)-1)

        self.assertFalse(inpt.get_reference())
        self.assertEquals(inpt.get_value(),poly)
        self.assertEquals(inpt.get_mimetype(),"application/geojson")

    def test_parse_complex_input_GET_gml_collection(self):

        from urllib.parse import quote
        poi = '''<wfs:FeatureCollection xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd http://mapserver.gis.umn.edu/mapserver http://aneto.oco/cgi-bin/worldwfs?SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=DescribeFeatureType&amp;TYPENAME=point&amp;OUTPUTFORMAT=XMLSCHEMA" xmlns:ms="http://mapserver.gis.umn.edu/mapserver" xmlns:wfs="http://www.opengis.net/wfs" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ms:msGeometry><gml:Point srsName="EPSG:4326"><gml:coordinates>-0.608315,44.857522</gml:coordinates></gml:Point></ms:msGeometry><ms:ogc_fid>1</ms:ogc_fid><ms:name>Bordeaux</ms:name><ms:id>124</ms:id></ms:Point></gml:featureMember>'''

        request="""InputPolygon=%s@mimeType=application/gml@schema=http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd http://mapserver.gis.umn.edu/mapserver http://aneto.oco/cgi-bin/worldwfs?SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=DescribeFeatureType&amp;TYPENAME=point&amp;OUTPUTFORMAT=XMLSCHEMA"""% quote(poi)

        self.inpt.parse_url(request)

        inpt = self.inpt.get_input(len(self.inpt)-1)

        self.assertFalse(inpt.reference)
        self.assertEquals(inpt.get_value(),poi)
        self.assertEquals(inpt.get_mimetype(),"application/gml")
        self.assertEquals(inpt.get_schema(),"http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-basic.xsd http://mapserver.gis.umn.edu/mapserver http://aneto.oco/cgi-bin/worldwfs?SERVICE=WFS&amp;VERSION=1.0.0&amp;REQUEST=DescribeFeatureType&amp;TYPENAME=point&amp;OUTPUTFORMAT=XMLSCHEMA")


if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseComplexInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
