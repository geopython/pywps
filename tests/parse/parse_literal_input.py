"""Test parsing of LiteralInput
"""

import os
import sys
from io import StringIO
from lxml import objectify

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],"..",".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.process.inout.literal import LiteralInput

class ParseLiteralInputTestCase(unittest.TestCase):

    def setUp(self):
        self.inpt = LiteralInput("BufferDistance")

    def test_parse_literal_input_GET(self):
        """Parse GET KVP literal input"""

        # testing basic parsing
        request="BufferDistance=400"
        self.inpt.set_from_url(request)
        self.assertEquals(400,self.inpt.value)

        # parse uoms
        request="BufferDistance=400@uom=m"
        self.inpt.set_from_url(request)
        self.assertEquals("m",self.inpt.uom)

        # check input type
        self.inpt.set_datatype("string")
        self.inpt.set_from_url(request)
        self.assertEquals("400",self.inpt.value)

    def test_parse_literal_input_POST(self):
        """parse xml POST literal input
        """

        # test basic parsing
        requeststr=StringIO("""<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
			<ows:Identifier>BufferDistance</ows:Identifier>
			<ows:Title>Distance which people will walk to get to a playground .</ows:Title>
			<wps:Data>
				<wps:LiteralData>400</wps:LiteralData>
			</wps:Data>
		</wps:Input>""")
        request = objectify.parse(requeststr)
        self.inpt.set_from_xml(request.getroot())
        self.assertEquals(400,self.inpt.value)

        # parse uoms
        requeststr=StringIO("""<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
			<ows:Identifier>BufferDistance</ows:Identifier>
			<ows:Title>Distance which people will walk to get to a playground .</ows:Title>
			<wps:Data>
				<wps:LiteralData uom="m">400</wps:LiteralData>
			</wps:Data>
		</wps:Input>""")
        request = objectify.parse(requeststr)
        self.inpt.set_from_xml(request.getroot())
        self.assertEquals("m",self.inpt.uom)

        # check input type
        requeststr=StringIO("""<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
			<ows:Identifier>BufferDistance</ows:Identifier>
			<ows:Title>Distance which people will walk to get to a playground .</ows:Title>
			<wps:Data>
				<wps:LiteralData uom="m">400</wps:LiteralData>
			</wps:Data>
		</wps:Input>""")
        request = objectify.parse(requeststr)
        self.inpt.set_from_xml(request.getroot())
        self.inpt.set_datatype("string")
        self.assertEquals("400",self.inpt.value)

if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseLiteralInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
