import unittest
import time
from pywps import Service, Process, LiteralInput, LiteralOutput
from pywps.app import WPS, OWS
from tests.common import client_for

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
    success = resp.xpath_text('/wps:ExecuteResponse'
                              '/wps:Status'
                              '/wps:ProcessSucceeded')
    assert success != None

def create_sleep():
    
    def sleep(request, response):
        seconds = request.inputs['seconds']
        assert type(seconds) is type(1.0)
        
        step = seconds / 10
        for i in range(10):
            # How is status working in version 4 ?
            self.status.set("Waiting...", i * 10)
            time.sleep(step)
        
        response.outputs['finished'] = "True"
        return response
    
        return Process(handler=sleep,
                   inputs=[LiteralInput('seconds', mimeType='text/xml')],
                   outputs=[LiteralOutput('finished', mimeType='text/xml')])
        
class ExecuteTest(unittest.TestCase):
            
    def test_assync(self):
        client = client_for(Service(processes=[create_sleep()]))
        request_doc = WPS.Execute(
            OWS.Identifier('sleep'),
            WPS.DataInputs(
                WPS.Input(OWS.Identifier('seconds'), 120)))
        resp = client.post_xml(doc=request_doc)
        assert_response_accepted(resp) 
        
        # To Do: 
        # . extract the status URL from the response
        # . send a status request
    