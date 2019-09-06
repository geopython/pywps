##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps import Process
from pywps.inout import LiteralInput, LiteralOutput
from pywps.inout.literaltypes import ValuesReference


class SimpleProcess(Process):
    identifier = "simpleprocess"

    def __init__(self):
        self.add_input(LiteralInput())


class UltimateQuestion(Process):
    def __init__(self):
        super(UltimateQuestion, self).__init__(
            self._handler,
            identifier='ultimate_question',
            title='Ultimate Question',
            outputs=[LiteralOutput('outvalue', 'Output Value', data_type='string')])

    @staticmethod
    def _handler(request, response):
        response.outputs['outvalue'].data = '42'
        return response


class Greeter(Process):
    def __init__(self):
        super(Greeter, self).__init__(
            self.greeter,
            identifier='greeter',
            title='Greeter',
            inputs=[LiteralInput('name', 'Input name', data_type='string')],
            outputs=[LiteralOutput('message', 'Output message', data_type='string')]
        )

    @staticmethod
    def greeter(request, response):
        name = request.inputs['name'][0].data
        assert type(name) is text_type
        response.outputs['message'].data = "Hello {}!".format(name)
        return response


class InOut(Process):
    def __init__(self):
        super(InOut, self).__init__(
            self.inout,
            identifier='inout',
            title='In and Out',
            inputs=[
                LiteralInput('string', 'String', data_type='string'),
                LiteralInput('time', 'Time', data_type='time',
                             default='12:00:00'),
                LiteralInput('ref_value', 'Referenced Value', data_type='string',
                    allowed_values=ValuesReference(reference="https://en.wikipedia.org/w/api.php?action=opensearch&search=scotland&format=json"),  # noqa
                    default='Scotland',),
            ],
            outputs=[
                LiteralOutput('string', 'Output', data_type='string')
            ]
        )

    @staticmethod
    def inout(request, response):
        a_string = request.inputs['string'][0].data
        response.outputs['string'].data = "".format(a_string)
        return response
