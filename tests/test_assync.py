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
import time
from pywps import Service, Process, LiteralInput, LiteralOutput
from pywps import WPS, OWS
from tests.common import client_for, assert_response_accepted


def create_sleep():

    def sleep(request, response):
        seconds = request.inputs['seconds']
        assert type(seconds) is type(1.0)

        step = seconds / 10
        for i in range(10):
            # How is status working in version 4 ?
            #self.status.set("Waiting...", i * 10)
            time.sleep(step)

        response.outputs['finished'] = "True"
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
                            "120"
                        )
                    )
                )
            ),
            version="1.0.0"
        )
        resp = client.post_xml(doc=request_doc)
        assert_response_accepted(resp)

        # To Do:
        # . extract the status URL from the response
        # . send a status request
