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
import lxml.etree
from pywps.app import WPSRequest
import tempfile


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
            'identifiers': 'ahoj',
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
                    'allowed_values': [ {'type':'anyvalue'} ],
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
        self.assertListEqual(self.request.inputs['myliteral'][0].allowed_values, [], 'Any value set')
        self.assertTrue(self.request.inputs['myliteral'][0].any_value, 'Any value set')


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(WPSRequestTest)
    ]
    return unittest.TestSuite(suite_list)
