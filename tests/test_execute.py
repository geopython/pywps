import unittest
from pywps.app import Service, Process, WPSResponse
from tests.common import client_for


class ExecuteTest(unittest.TestCase):

    def test_returns_function_response(self):
        def increment_handler(request):
            return WPSResponse({'outvalue': '13'})
        increment = Process(
            identifier='increment',
            handler=increment_handler)
        client = client_for(Service(processes=[increment]))
        resp = client.get('?Request=Execute'
                           '&identifier=increment'
                           '&DataInputs=invalue=13')
        assert resp.status_code == 200
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
        assert out_value == '13'

def load_tests():
    loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTest),
    ]
    return unittest.TestSuite(suite_list)
