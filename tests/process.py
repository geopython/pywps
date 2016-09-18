"""Test process
"""

###############################################################################
#
# Copyright (C) 2014-2016 PyWPS Development Team, represented by
# PyWPS Project Steering Committee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
###############################################################################

import os
import sys
from io import StringIO
from lxml import objectify

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps import Process
from pywps.inout import LiteralInput
from pywps.inout import BoundingBoxInput
from pywps.inout import ComplexInput

class ProcessTestCase(unittest.TestCase):

    def test_get_input_title(self):
        """Test returning the proper input title"""

        # configure
        def donothing(*args, **kwargs):
            pass
        process = Process(donothing, "process", title="Process",
                          inputs=[
                              LiteralInput("length", title="Length"),
                              BoundingBoxInput("bbox", title="BBox", crss=[]),
                              ComplexInput("vector", title="Vector")
                          ],
                          outputs=[]
        )
        inputs = {
            input.identifier: input.title
            for input
            in process.inputs
        }
        self.assertEqual("Length", inputs['length'])
        self.assertEqual("BBox", inputs["bbox"])
        self.assertEqual("Vector", inputs["vector"])

if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ProcessTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
