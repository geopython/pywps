"""Unit tests for dblog
"""
import unittest

from pywps import configuration
from pywps.dblog import get_connection, check_db_table, check_db_columns


class DBLogTest(unittest.TestCase):
    """DBGLog test cases"""

    def setUp(self):

        self.database = configuration.get_config_value('server', 'logdatabase')
        if not self.database:
            self.database = ':memory:'

    def test_0_dblog(self):
        """Test pywps.formats.Format class
        """
        connection = get_connection()
        self.assertTrue(connection)
        self.assertTrue(check_db_table(connection))
        #self.assertTrue(check_db_columns(self.database))

    def test_db_content(self):
        connection = get_connection()
        cur = connection.cursor()
        cur.execute("Select * from pywps_requests WHERE time_end IS NULL")
        null_time_end = cur.fetchall()
        self.assertEqual(len(null_time_end), 0,
                         'There are no unfinished processes loged')
        cur.execute("Select * from pywps_requests WHERE status IS NULL")
        null_status = cur.fetchall()
        self.assertEqual(len(null_status), 0,
                         'There are no processes without status loged')

        cur.execute("Select * from pywps_requests WHERE percent_done IS NULL")
        null_percent = cur.fetchall()
        self.assertEqual(len(null_percent), 0,
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
