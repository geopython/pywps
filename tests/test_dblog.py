##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Unit tests for dblog
"""

import unittest

from pywps.app import WPSRequest
from pywps import configuration
from pywps.dblog import get_session, store_request, pop_first_stored
from pywps.dblog import ProcessInstance, RequestInstance
from pywps.processing.job import Job
import uuid
import tempfile
import json

class DBStoreRequestTest(unittest.TestCase):
    """Store process request to database and retrieve it again"""

    def setUp(self):

        self.database = configuration.get_config_value('logging', 'database')

        #self.tempfile_db = tempfile.mktemp(prefix="pywps-db", suffix=".sqlite")
        #self.database = "sqlite://{}".format(self.tempfile_db)
        self.session = get_session()
        assert self.session


    def test_insert_request(self):

        requests = self.session.query(RequestInstance)
        assert  requests.count() == 0

        obj = {
            'operation': 'execute',
            'version': '1.0.0',
            'language': 'eng',
            'identifier': 'multiple-outputs',
            'store_execute': True,
            'status': True,
            'lineage': True,
            'inputs': {
                'count': [{
                    'identifier': 'count',
                    'type': 'literal',
                    'data': 3
                }]
            },
            'outputs': {},
            'raw': False
        }

        request = WPSRequest()
        request.json = obj

        from .processes.metalinkprocess import MultipleOutputs
        process = MultipleOutputs()
        process.uuid = uuid.uuid4()
        store_request(process.uuid, request, process)

        requests = self.session.query(RequestInstance)
        assert requests.count() == 1
        stored_request = pop_first_stored()

        job = Job.from_json({
            "process": json.loads(stored_request.process),
            "wps_request": json.loads(stored_request.request)
        })

        assert job.process.identifier == "multiple-outputs"
        assert str(job.process.uuid) == str(process.uuid)

        requests = self.session.query(RequestInstance)
        assert  requests.count() == 0


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

        null_percent = session.query(ProcessInstance).filter(ProcessInstance.percent_done < 100)
        self.assertEqual(null_percent.count(), 0,
                         'There are no unfinished processes')

def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DBLogTest),
        loader.loadTestsFromTestCase(DBStoreRequestTest)
    ]
    return unittest.TestSuite(suite_list)
