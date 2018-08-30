##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
import time
from pywps import Service, Process, LiteralInput, LiteralOutput
from pywps import get_ElementMakerForVersion
from pywps.tests import client_for, assert_response_accepted

VERSION = "1.0.0"

WPS, OWS = get_ElementMakerForVersion(VERSION)


def create_sleep():

    def sleep(request, response):
        seconds = request.inputs['seconds'][0].data
        assert isinstance(seconds, float)

        step = seconds / 3
        for i in range(3):
            # How is status working in version 4 ?
            #self.status.set("Waiting...", i * 10)
            time.sleep(step)

        response.outputs['finished'].data = "True"
        return response

    return Process(handler=sleep,
                   identifier='sleep',
                   title='Sleep',
                   inputs=[
                       LiteralInput('seconds', title='Seconds', data_type='float')
                   ],
                   outputs=[
                       LiteralOutput('finished', title='Finished', data_type='boolean')
                   ]
    )


class ExecuteTest(unittest.TestCase):

    def test_assync(self):
        client = client_for(Service(processes=[create_sleep()]))
        request_doc = WPS.Execute(
            OWS.Identifier('sleep'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('seconds'),
                    WPS.Data(
                        WPS.LiteralData(
                            "0.3"
                        )
                    )
                )
            ),
            version="1.0.0"
        )
        resp = client.post_xml(doc=request_doc)
        assert_response_accepted(resp)

        # TODO:
        # . extract the status URL from the response
        # . send a status request


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTest),
    ]
    return unittest.TestSuite(suite_list)
