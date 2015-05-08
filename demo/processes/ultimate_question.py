from pywps import Process, LiteralInput, LiteralOutput


class UltimateQuestion(Process):
    def __init__(self):
        inputs = []
        outputs = [LiteralOutput('answer', 'Answer to Ultimate Question', data_type='string')]

        super(UltimateQuestion, self).__init__(
            self._handler,
            identifier='ultimate_question',
            version='1.3.3.7',
            title='Answer to the ultimate question',
            abstract='This process gives the answer to the ultimate question of "What is the meaning of life?',
            profile='',
            wsdl='',
            metadata=['Ultimate Question', 'What is the meaning of life'],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False
        )

    @staticmethod
    def _handler(request, response):
        response.outputs['answer'].data = '42'
        return response