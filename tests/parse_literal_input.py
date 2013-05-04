"""Test parsing of LiteralInput
"""

import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.process.inout.literal import LiteralInput

class ParseLiteralInputTestCase(unittest.TestCase):

    def setUp(self):
        self.inpt = LiteralInput("BufferDistance")

    def test_parse_literal_input_GET(self):

        request="BufferDistance=400"
        self.inpt.set_from_url(request)
        self.assertEquals(400,self.inpt.value)

        request="BufferDistance=400@uom=m"
        self.inpt.set_from_url(request)
        self.assertEquals("m",self.inpt.uom)

        self.inpt.set_datatype("string")
        self.inpt.set_from_url(request)
        self.assertEquals("400",self.inpt.value)

    def test_parse_literal_input_POST(self):
        """TO BE DONE - parse node
        """
        pass


if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseLiteralInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
