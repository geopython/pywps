# -*- coding: utf-8 -*-
import json
import unittest

from flask_testing import TestCase
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from pywps.server.app import application, db


class ProcessesTest(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        return application

    def setUp(self):
        db.create_all()

        self.client = Client(application, BaseResponse)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def testGetRequest(self):
        response = self.client.get('/processes')

        self.assertEqual(response.status_code, 200)

    def testPostRequest(self):
        response = self.client.post('/processes')

        self.assertEqual(response.status_code, 405)

    def testPutRequest(self):
        response = self.client.put('/processes')

        self.assertEqual(response.status_code, 405)

    def testDeleteRequest(self):
        response = self.client.delete('/processes')

        self.assertEqual(response.status_code, 405)


class ProcessesUUIDTest(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        return application

    def setUp(self):
        db.create_all()

        self.client = Client(application, BaseResponse)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_request_status_code(self):
        response = self.client.get('/processes/12345')

        self.assertEqual(response.status_code, 200)

    def test_post_request_status_code(self):
        response = self.client.post('/processes/12345')

        self.assertEqual(response.status_code, 405)

    def test_put_request_status_code(self):
        response = self.client.put('/processes/12345')

        self.assertEqual(response.status_code, 200)

    def test_delete_request_status_code(self):
        response = self.client.delete('/processes/12345')

        self.assertEqual(response.status_code, 200)

    def test_get_request_success_parameter(self):
        response = self.client.get('/processes/12345')

        data = json.loads(response.data)

        self.assertIn('success', data)

    def test_put_request_success_parameter(self):
        response = self.client.put('/processes/12345')

        data = json.loads(response.data)

        self.assertIn('success', data)

    def test_delete_request_success_parameter(self):
        response = self.client.delete('/processes/12345')

        data = json.loads(response.data)

        self.assertIn('success', data)

    def test_get_request_returning_response(self):
        response = self.client.get('/processes/12345')

        data = json.loads(response.data)

        self.assertFalse(data['success'])

    def test_put_request_returning_response(self):
        response = self.client.put('/processes/12345')

        data = json.loads(response.data)

        self.assertFalse(data['success'])

    def test_delete_request_returning_response(self):
        response = self.client.delete('/processes/12345')

        data = json.loads(response.data)

        self.assertFalse(data['success'])


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ProcessesTest),
        loader.loadTestsFromTestCase(ProcessesUUIDTest),
    ]
    return unittest.TestSuite(suite_list)


if __name__ == '__main__':
    unittest.main()