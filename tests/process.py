"""Test process
"""

import os
import sys
from io import StringIO
from lxml import objectify

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.process import Process
from pywps.process.inout.standards import LiteralLengthInput
from pywps.process.inout.standards import BBoxInput
from pywps.process.inout.standards import ComplexVectorInput

class ProcessTestCase(unittest.TestCase):

    def test_get_input_type(self):
        """Test returning the proper input type"""

        # configure
        process = Process("process")
        process.add_input(LiteralLengthInput())
        process.add_input(BBoxInput())
        process.add_input(ComplexVectorInput())
        
        self.assertEquals("literal",process.get_input_type("length"))
        self.assertEquals("bbox",process.get_input_type("bbox"))
        self.assertEquals("complex",process.get_input_type("vector"))

if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ProcessTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
