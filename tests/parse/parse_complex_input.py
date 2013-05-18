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

    def test_parse_complex_input_GET_reference(self):
        """Parse complex input KVP reference"""

        url = "InputLayer=http://foo/bar.tif@schema=http://foo/xsd@encoding=utf-8@mimetype=image/tiff"
        self.inpt.set_from_url(url)

        pass

    def test_parse_complex_input_GET_reference_href(self):
        """Parse complex input KVP reference with href attribut"""

        url = "InputLayer=@schema=http://foo/xsd@encoding=utf-8@mimetype=image/tiff@href=http://foo/bar.tif"
        self.inpt.set_from_url(url)

        pass

    def test_parse_complex_input_POST_reference(self):
        """Parse complex input XML reference"""
        
        strin = StringIO("""<wps:Input>
			<ows:Identifier>InputLayer</ows:Identifier>
			<ows:Title>The layer which's values shall be reclassified</ows:Title>
			<wps:Reference xlink:href="http://orchestra.pisa.intecs.it/geoserver/test/height.tif" method="GET"/>
		</wps:Input>""")

        req = objectify.parse(strin)
        self.inpt.set_from_xml(req.getroot())


        pass

if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseComplexInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
