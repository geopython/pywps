##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Unit tests for dblog
"""

from basic import TestBase

from pywps import configuration
from pywps.dblog import get_session
from pywps.dblog import ProcessInstance


class DBLogTest(TestBase):
    """DBGLog test cases"""

    def setUp(self):
        super().setUp()
        self.database = configuration.get_config_value('logging', 'database')
        # Ensure a clean slate: other tests may have left rows in the
        # process-instance table, which would make the content assertions
        # below fail when the suite runs in a different order.
        session = get_session()
        session.query(ProcessInstance).delete()
        session.commit()

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

        null_percent = session.query(ProcessInstance).filter(ProcessInstance.percent_done < 100)
        self.assertEqual(null_percent.count(), 0,
                         'There are no unfinished processes')

def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    import unittest

    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DBLogTest)
    ]
    return unittest.TestSuite(suite_list)
