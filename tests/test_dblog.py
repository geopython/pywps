##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Unit tests for dblog
"""

import unittest

from pywps import configuration
import pywps.dblog as dblog

from types import SimpleNamespace as ns
import json

fake_request = ns(
    version = '1.0.0',
    operation = 'execute',
    identifier = 'dummy_identifier'
)

fake_process = ns(
    uuid="0bf3cd00-0102-11ed-8421-e4b97ac7e08e",
    json=json.dumps({"identifier": "something"})
)

class DBLogTest(unittest.TestCase):
    """DBGLog test cases"""

    def setUp(self):

        self.database = configuration.get_config_value('logging', 'database')

    def test_log_request(self):
        dblog.log_request("0bf3cd00-0102-11ed-8421-e4b97ac7e02e", fake_request)
        dblog.log_request("0bf3cd00-0102-11ed-8421-e4b97ac7e03e", fake_request)
        dblog.log_request("0bf3cd00-0102-11ed-8421-e4b97ac7e04e", fake_request)

        running, stored = dblog.get_process_counts()
        assert running == 0
        assert stored == 0

        dblog.store_status("0bf3cd00-0102-11ed-8421-e4b97ac7e03e", dblog.WPS_STATUS.ACCEPTED, "accepted", 10)

        running, stored = dblog.get_process_counts()
        assert running == 0
        assert stored == 0

        dblog.store_status("0bf3cd00-0102-11ed-8421-e4b97ac7e04e", dblog.WPS_STATUS.STARTED, "started", 10)
        dblog.update_pid("0bf3cd00-0102-11ed-8421-e4b97ac7e04e", 10)

        running, stored = dblog.get_process_counts()
        assert running == 1
        assert stored == 0

        dblog.store_status(fake_process.uuid, dblog.WPS_STATUS.ACCEPTED, "accepted", 10)
        dblog.store_process(fake_process)

        running, stored = dblog.get_process_counts()
        assert running == 1
        assert stored == 1

        p = dblog.pop_first_stored()
        assert p.uuid == fake_process.uuid

        running, stored = dblog.get_process_counts()
        assert running == 1
        assert stored == 0

    def test_storage(self):
        fake_storage = ns(
            uuid="ebf3cd00-0102-11ed-8421-e4b97ac7e02e",
            pretty_filename = "pretty_filename.txt",
            mimetype="text/plain",
            dump=lambda: b'somedata'
        )

        dblog.update_storage_record(fake_storage)

        s = dblog.get_storage_record(fake_storage.uuid)

        assert s.uuid == fake_storage.uuid
        assert s.pretty_filename == fake_storage.pretty_filename
        assert s.mimetype == fake_storage.mimetype
        assert s.data == fake_storage.dump()

    def test_status(self):
        dblog.update_status_record("fbf3cd00-0102-11ed-8421-e4b97ac7e02e", "somedata")
        s = dblog.get_status_record("fbf3cd00-0102-11ed-8421-e4b97ac7e02e")
        assert s.uuid == "fbf3cd00-0102-11ed-8421-e4b97ac7e02e"
        assert s.data == "somedata"


def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DBLogTest)
    ]
    return unittest.TestSuite(suite_list)
