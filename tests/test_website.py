# -*- coding: utf-8 -*-
import unittest

from flask_testing import TestCase
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from pywps.server.app import application, db


class WebsiteTest(TestCase):
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

    def test_home_page_status_code(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_manage_page_status_code(self):
        response = self.client.get('/manage')

        self.assertEqual(response.status_code, 200)


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(WebsiteTest),
    ]
    return unittest.TestSuite(suite_list)


if __name__ == '__main__':
    unittest.main()