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

from pywps.process.inout.bbox import BoundingBoxInput

class ParseBBoxInputTestCase(unittest.TestCase):

    def setUp(self):
        self.inpt = BoundingBoxInput("BufferDistance")

    def test_parse_bbox_input_GET(self):

        # testing basic parsing
        request="bbox=1,2,3,4"
        self.inpt.set_from_url(request)
        self.assertEquals(1,self.inpt.left)
        self.assertEquals(2,self.inpt.dimensions)

        # parse crs
        request="bbox=1,2,3,4,epsg:4326"
        self.inpt.set_from_url(request)
        self.assertEquals("EPSG:4326",self.inpt.crs.getcode())

    def test_parse_bbox_input_POST(self):
        TODO FIXME
        pass


if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseBBoxInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
