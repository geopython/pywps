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

import lxml.etree
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from pywps import __version__, NAMESPACES

import logging

logging.disable(logging.CRITICAL)

class WpsClient(Client):

    def post_xml(self, *args, **kwargs):
        doc = kwargs.pop('doc')
        data = lxml.etree.tostring(doc, pretty_print=True)
        kwargs['data'] = data
        return self.post(*args, **kwargs)


class WpsTestResponse(BaseResponse):

    def __init__(self, *args):
        super(WpsTestResponse, self).__init__(*args)
        if self.headers.get('Content-Type') == 'text/xml':
            self.xml = lxml.etree.fromstring(self.get_data())

    def xpath(self, path):
        return self.xml.xpath(path, namespaces=NAMESPACES)

    def xpath_text(self, path):
        return ' '.join(e.text for e in self.xpath(path))


def client_for(service):
    return WpsClient(service, WpsTestResponse)


def assert_response_accepted(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    success = resp.xpath_text('/wps:ExecuteResponse'
                              '/wps:Status'
                              '/wps:ProcessAccepted')
    assert success != None
    # To Do: assert status URL is present

def assert_process_started(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    success = resp.xpath_text('/wps:ExecuteResponse'
                              '/wps:Status'
                              'ProcessStarted')
    # Is it still like this in PyWPS-4 ?
    assert success.split[0] == "processstarted"


def assert_response_success(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    success = resp.xpath('/wps:ExecuteResponse/wps:Status/wps:ProcessSucceeded')
    assert len(success) == 1


def assert_pywps_version(resp):
    # get first child of root element
    root_firstchild = resp.xpath('/*')[0].getprevious()
    assert isinstance(root_firstchild, lxml.etree._Comment)
    tokens = root_firstchild.text.split()
    assert len(tokens) == 2
    assert tokens[0] == 'PyWPS'
    assert tokens[1] == __version__
