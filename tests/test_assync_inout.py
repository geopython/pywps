##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps import Service, Process, LiteralInput, ComplexOutput
from pywps import FORMATS
from pywps import get_ElementMakerForVersion
from pywps.tests import client_for

VERSION = "1.0.0"

WPS, OWS = get_ElementMakerForVersion(VERSION)


def create_inout():

    def inout(request, response):
        response.outputs['text'].data = request.inputs['text'][0].data
        return response

    return Process(handler=inout,
                   identifier='inout',
                   title='InOut',
                   inputs=[
                       LiteralInput('text', 'Text', data_type='string')
                   ],
                   outputs=[
                        ComplexOutput(
                            'text',
                            title='Text',
                            supported_formats=[FORMATS.TEXT, ]
                            ),
                   ],
                   store_supported=True,
                   status_supported=True
                   )


def test_assync_inout():
    client = client_for(Service(processes=[create_inout()]))
    request_doc = WPS.Execute(
        OWS.Identifier('inout'),
        WPS.DataInputs(
            WPS.Input(
                OWS.Identifier('text'),
                WPS.Data(
                    WPS.LiteralData(
                        "Hello World"
                    )
                )
            )
        ),
        WPS.ResponseForm(
            WPS.ResponseDocument(
                WPS.Output(
                    OWS.Identifier("text")
                ),
            ),
        ),
        version="1.0.0"
    )
    resp = client.post_xml(doc=request_doc)
    print(resp.data)
    assert resp.status_code == 200

    # TODO:
    # . extract the status URL from the response
    # . send a status request
