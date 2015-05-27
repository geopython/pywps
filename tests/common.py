import lxml.etree
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from pywps import NAMESPACES


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