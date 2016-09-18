"""Unit tests for dblog
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

import unittest

from pywps import configuration
from pywps.dblog import get_session
from pywps.dblog import ProcessInstance


class DBLogTest(unittest.TestCase):
    """DBGLog test cases"""

    def setUp(self):

        self.database = configuration.get_config_value('logging', 'database')

    def test_0_dblog(self):
        """Test pywps.formats.Format class
        """
        session = get_session()
        self.assertTrue(session)

    def test_db_content(self):
        session = get_session()
        null_time_end = session.query(ProcessInstance).filter(ProcessInstance.time_end == None)
        self.assertEqual(null_time_end.count(), 0,
                         'There are no unfinished processes loged')

        null_status = session.query(ProcessInstance).filter(ProcessInstance.status == None)
        self.assertEqual(null_status.count(), 0,
                         'There are no processes without status loged')

        null_percent = session.query(ProcessInstance).filter(ProcessInstance.percent_done == None)
        self.assertEqual(null_percent.count(), 0,
                         'There are no processes without percent loged')

def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DBLogTest)
    ]
    return unittest.TestSuite(suite_list)
