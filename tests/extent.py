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
    
if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(ExtentTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
