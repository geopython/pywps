import unittest
import lxml.etree
from pywps.app import Service, Process, WPSResponse, WPS, OWS
from tests.common import client_for


def create_ultimate_question():
    return Process(identifier='ultimate_question',
                   handler=lambda request: WPSResponse({'outvalue': '42'}))


class ExecuteTest(unittest.TestCase):

    def check_ultimate_question_response(self, resp):
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'text/xml'
        success = resp.xpath_text('/wps:ExecuteResponse'
                                  '/wps:Status'
                                  '/wps:ProcessSucceeded')
        assert success == "great success"

        out_id = resp.xpath_text('/wps:ExecuteResponse'
                                 '/wps:ProcessOutputs'
                                 '/wps:Output'
                                 '/ows:Identifier')
        assert out_id == 'outvalue'

        out_value = resp.xpath_text('/wps:ExecuteResponse'
                                    '/wps:ProcessOutputs'
                                    '/wps:Output'
                                    '/ows:Data'
                                    '/wps:LiteralData')
        assert out_value == '42'

    def test_get_with_no_inputs(self):
        client = client_for(Service(processes=[create_ultimate_question()]))
        resp = client.get('?Request=Execute&identifier=ultimate_question')
        self.check_ultimate_question_response(resp)

    def test_post_with_no_inputs(self):
        client = client_for(Service(processes=[create_ultimate_question()]))
        request_doc = WPS.Execute(OWS.Identifier('ultimate_question'))
        resp = client.post('', data=lxml.etree.tostring(
            request_doc, pretty_print=True))
        self.check_ultimate_question_response(resp)


def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTest),
    ]
    return unittest.TestSuite(suite_list)
