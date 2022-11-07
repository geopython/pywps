##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Unit tests for processing
"""

from basic import TestBase

import json
import uuid

from pywps import configuration
import pywps.processing
from pywps.processing.job import Job
from pywps.processing.basic import MultiProcessing
from pywps.app import WPSRequest
from pywps.response.execute import ExecuteResponse
from pywps.app.WPSExecuteResponse import WPSExecuteResponse

from processes import Greeter, InOut, BBox


class GreeterProcessingTest(TestBase):
    """Processing test case with Greeter process"""

    def setUp(self):
        super().setUp()

        self.workdir = pywps.configuration.get_config_value('server', 'workdir')

        self.uuid = uuid.uuid1()
        self.dummy_process = Greeter()
        self.dummy_process._set_uuid(self.uuid)
        self.dummy_process.set_workdir(self.workdir)
        self.wps_request = WPSRequest()
        self.wps_response = ExecuteResponse(WPSExecuteResponse(self.dummy_process,
                                            self.wps_request, self.uuid))
        self.job = Job(
            process=self.dummy_process,
            wps_request=self.wps_request,
            wps_response=self.wps_response)

    def test_default_mode(self):
        """Test pywps.formats.Format class
        """
        self.assertEqual(configuration.get_config_value('processing', 'mode'),
                         'default')
        process = pywps.processing.Process(
            process=self.dummy_process,
            wps_request=self.wps_request,
            wps_response=self.wps_response)
        # process.start()
        self.assertTrue(isinstance(process, MultiProcessing))

    def test_job_json(self):
        new_job = Job.from_json(json.loads(self.job.json))
        self.assertEqual(new_job.name, 'greeter')
        self.assertEqual(new_job.uuid, str(self.uuid))
        self.assertEqual(new_job.workdir, self.workdir)
        self.assertEqual(len(new_job.process.inputs), 1)

    def test_job_dump(self):
        new_job = Job.load(self.job.dump())
        self.assertEqual(new_job.name, 'greeter')
        self.assertEqual(new_job.uuid, str(self.uuid))
        self.assertEqual(new_job.workdir, self.workdir)
        self.assertEqual(len(new_job.process.inputs), 1)


class InOutProcessingTest(TestBase):
    """Processing test case with InOut process"""

    def setUp(self):
        super().setUp()

        self.workdir = pywps.configuration.get_config_value('server', 'workdir')

        self.uuid = uuid.uuid1()
        self.dummy_process = InOut()
        self.dummy_process._set_uuid(self.uuid)
        self.dummy_process.set_workdir(self.workdir)
        self.wps_request = WPSRequest()
        self.wps_response = ExecuteResponse(WPSExecuteResponse(self.dummy_process,
                                            self.wps_request, self.uuid))
        self.job = Job(
            process=self.dummy_process,
            wps_request=self.wps_request,
            wps_response=self.wps_response)

    def test_job_json(self):
        new_job = Job.from_json(json.loads(self.job.json))
        self.assertEqual(new_job.name, 'inout')
        self.assertEqual(new_job.uuid, str(self.uuid))
        self.assertEqual(new_job.workdir, self.workdir)
        self.assertEqual(len(new_job.process.inputs), 3)
        self.assertEqual(new_job.json, self.job.json)  # idempotent test

    def test_job_dump(self):
        new_job = Job.load(self.job.dump())
        self.assertEqual(new_job.name, 'inout')
        self.assertEqual(new_job.uuid, str(self.uuid))
        self.assertEqual(new_job.workdir, self.workdir)
        self.assertEqual(len(new_job.process.inputs), 3)
        self.assertEqual(new_job.json, self.job.json)  # idempotent test


class BBoxProcessingTest(TestBase):
    """Processing test case with BBox input and output process"""

    def setUp(self):
        super().setUp()

        self.workdir = pywps.configuration.get_config_value('server', 'workdir')

        self.uuid = uuid.uuid1()
        self.dummy_process = BBox()
        self.dummy_process._set_uuid(self.uuid)
        self.dummy_process.set_workdir(self.workdir)
        self.wps_request = WPSRequest()
        self.wps_response = ExecuteResponse(WPSExecuteResponse(self.dummy_process,
                                            self.wps_request, self.uuid))
        self.job = Job(
            process=self.dummy_process,
            wps_request=self.wps_request,
            wps_response=self.wps_response)

    def test_job_json(self):
        new_job = Job.from_json(json.loads(self.job.json))
        self.assertEqual(new_job.name, 'bbox_test')
        self.assertEqual(new_job.uuid, str(self.uuid))
        self.assertEqual(new_job.workdir, self.workdir)
        self.assertEqual(len(new_job.process.inputs), 1)
        self.assertEqual(new_job.json, self.job.json)  # idempotent test

    def test_job_dump(self):
        new_job = Job.load(self.job.dump())
        self.assertEqual(new_job.name, 'bbox_test')
        self.assertEqual(new_job.uuid, str(self.uuid))
        self.assertEqual(new_job.workdir, self.workdir)
        self.assertEqual(len(new_job.process.inputs), 1)
        self.assertEqual(new_job.json, self.job.json)  # idempotent test


def load_tests(loader=None, tests=None, pattern=None):
    """Load local tests
    """
    import unittest

    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(GreeterProcessingTest),
        loader.loadTestsFromTestCase(InOutProcessingTest),
        loader.loadTestsFromTestCase(BBoxProcessingTest)
    ]
    return unittest.TestSuite(suite_list)
