"""
Tests for pywps.extent.Extent class
"""

import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.extent import Extent

class ExtentTestCase(unittest.TestCase):
    """Test case extent object """

    def testExtent(self):

        extent = Extent(1,2,3,4)

        self.assertTupleEqual(extent.toArray(),(1,2,3,4))
        self.assertEqual(extent.toString(),"1,2,3,4")

def load_tests():
    return unittest.TestLoader().loadTestsFromTestCase(ExtentTestCase)

def main():
   unittest.TextTestRunner(verbosity=4).run(load_tests())

if __name__ == "__main__":
    main()
