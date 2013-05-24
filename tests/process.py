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

class ProcessTestCase(unittest.TestCase):

    def test_get_input_type(self):
        """Test returning the proper input type"""

        # configure
        process = Process("process")
        
        # TODO: get_input_type should return one of 
        # 'literal', 'bbox', 'complex'
        process.get_input_type("literalinput")
