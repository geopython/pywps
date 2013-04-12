import unittest

from parse_getcapabilities import *

suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseGetCapabilitiesTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)

from parse_describeprocess import *
suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseDescribeProcessTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
