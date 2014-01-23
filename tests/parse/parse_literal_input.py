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

class ParseLiteralInputTestCase(unittest.TestCase):

    def setUp(self):
        self.skipTest("Parser changed")
        self.inpt = LiteralInput("BufferDistance")

    def test_parse_literal_input_GET(self):
        """Parse GET KVP literal input"""

        # testing basic parsing
        request="BufferDistance=400"
        self.inpt.parse_url(request)
        self.assertEquals(400,self.inpt.get_value())

        # parse uoms
        request="BufferDistance=400@uom=m"
        self.inpt.parse_url(request)
        self.assertEquals("m",self.inpt.get_uom(1))

        # check input type
        self.inpt.set_datatype("string")
        self.inpt.parse_url(request)
        self.assertEquals("400",self.inpt.get_value(2))

        # check for input length
        self.assertEquals(3, len(self.inpt))

        # check for max_occurs
        self.inpt.max_occurs = 3
        self.inpt.parse_url(request)
        self.assertEquals(3, len(self.inpt))

    def test_parse_literal_input_POST(self):
        """parse xml POST literal input
        """

        # test basic parsing
        requeststr=StringIO(u"""<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
        		<ows:Identifier>BufferDistance</ows:Identifier>
        		<ows:Title>Distance which people will walk to get to a playground .</ows:Title>
        		<wps:Data>
        			<wps:LiteralData>400</wps:LiteralData>
        		</wps:Data>
        	</wps:Input>""")
        request = objectify.parse(requeststr)
        self.inpt.parse_xml(request.getroot())
        self.assertEquals(400,self.inpt.get_value())

        # parse uoms
        requeststr=StringIO(u"""<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
        		<ows:Identifier>BufferDistance</ows:Identifier>
        		<ows:Title>Distance which people will walk to get to a playground .</ows:Title>
        		<wps:Data>
        			<wps:LiteralData uom="m">400</wps:LiteralData>
        		</wps:Data>
        	</wps:Input>""")
        request = objectify.parse(requeststr)
        self.inpt.parse_xml(request.getroot())
        self.assertEquals("m",self.inpt.get_uom(1))

        # check input type
        requeststr=StringIO(u"""<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1">
        		<ows:Identifier>BufferDistance</ows:Identifier>
        		<ows:Title>Distance which people will walk to get to a playground .</ows:Title>
        		<wps:Data>
        			<wps:LiteralData uom="m">400</wps:LiteralData>
        		</wps:Data>
        	</wps:Input>""")
        request = objectify.parse(requeststr)
        self.inpt.set_datatype("string")
        self.inpt.parse_xml(request.getroot())
        self.assertEquals("400",self.inpt.get_value(2))

if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseLiteralInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
