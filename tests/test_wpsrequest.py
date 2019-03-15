##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
import lxml.etree
from pywps.app import WPSRequest
import tempfile
import datetime
import json

from pywps.inout.literaltypes import AnyValue


class WPSRequestTest(unittest.TestCase):

    def setUp(self):

        self.request = WPSRequest()
        self.tempfile = tempfile.mktemp()

        x = open(self.tempfile, 'w')
        x.write("ahoj")
        x.close()

    def test_json_in(self):

        obj = {
            'operation': 'getcapabilities',
            'version': '1.0.0',
            'language': 'eng',
            'identifier': 'ahoj',
            'identifiers': 'ahoj',  # TODO: why identifierS?
            'store_execute': True,
            'status': True,
            'lineage': True,
            'inputs': {
                'myin': [{
                    'identifier': 'myin',
                    'type': 'complex',
                    'supported_formats': [{
                        'mime_type': 'tralala'
                    }],
                    'file': self.tempfile,
                    'data_format': {'mime_type': 'tralala'}
                }],
                'myliteral': [{
                    'identifier': 'myliteral',
                    'type': 'literal',
                    'data_type': 'integer',
                    'allowed_values': [{'type': 'anyvalue'}],
                    'data': 1
                }]
            },
            'outputs': {},
            'raw': False
        }

        self.request = WPSRequest()
        self.request.json = obj

        self.assertEqual(self.request.inputs['myliteral'][0].data, 1, 'Data are in the file')
        self.assertEqual(self.request.inputs['myin'][0].data, 'ahoj', 'Data are in the file')
        self.assertListEqual(self.request.inputs['myliteral'][0].allowed_values, [AnyValue()], 'Any value not set')
        self.assertTrue(self.request.inputs['myliteral'][0].any_value, 'Any value set')

    def test_json_inout_datetime(self):
        obj = {
            'operation': 'getcapabilities',
            'version': '1.0.0',
            'language': 'eng',
            'identifier': 'moinmoin',
            'identifiers': 'moinmoin',  # TODO: why identifierS?
            'store_execute': True,
            'status': True,
            'lineage': True,
            'inputs': {
                'datetime': [{
                    'identifier': 'datetime',
                    'type': 'literal',
                    'data_type': 'dateTime',
                    'data': '2017-04-20T12:00:00',
                    'allowed_values': [{'type': 'anyvalue'}],
                }],
                'date': [{
                    'identifier': 'date',
                    'type': 'literal',
                    'data_type': 'date',
                    'data': '2017-04-20',
                    'allowed_values': [{'type': 'anyvalue'}],
                }],
                'time': [{
                    'identifier': 'time',
                    'type': 'literal',
                    'data_type': 'time',
                    'data': '09:00:00',
                    'allowed_values': [{'type': 'anyvalue'}],
                }],
            },
            'outputs': {},
            'raw': False
        }

        self.request = WPSRequest()
        self.request.json = obj

        self.assertEqual(self.request.inputs['datetime'][0].data, datetime.datetime(2017, 4, 20, 12), 'Datatime set')
        self.assertEqual(self.request.inputs['date'][0].data, datetime.date(2017, 4, 20), 'Data set')
        self.assertEqual(self.request.inputs['time'][0].data, datetime.time(9, 0, 0), 'Time set')

        # dump to json and reload
        dump = self.request.json
        self.request.json = json.loads(dump)

        self.assertEqual(self.request.inputs['datetime'][0].data, datetime.datetime(2017, 4, 20, 12), 'Datatime set')
        self.assertEqual(self.request.inputs['date'][0].data, datetime.date(2017, 4, 20), 'Data set')
        self.assertEqual(self.request.inputs['time'][0].data, datetime.time(9, 0, 0), 'Time set')


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(WPSRequestTest)
    ]
    return unittest.TestSuite(suite_list)
