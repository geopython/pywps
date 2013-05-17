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

    def test_parse_complex_input_GET(self):
        """Parse complex input KVP"""

        pass

    def test_parse_complex_input_POST(self):
        """Parse complex input XML"""

        pass

if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ParseComplexInputTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
