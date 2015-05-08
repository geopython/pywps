from pywps import Process, LiteralInput, LiteralOutput


class Sleep(Process):
    def __init__(self):
        inputs = [LiteralInput('delay', 'Delay between every update', data_type='float')]
        outputs = [LiteralOutput('sleep_output', 'Sleep Output', data_type='string')]

        super(Sleep, self).__init__(
            self._handler,
            identifier='sleep',
            version='None',
            title='Sleep Process',
            abstract='This process will sleep for a given delay or 10 seconds if not a valid value',
            profile='',
            wsdl='',
            metadata=['Sleep', 'Wait', 'Delay'],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    @staticmethod
    def _handler(request, response):
        import time

        sleep_delay = request.inputs['delay'].data
        if sleep_delay:
            sleep_delay = float(sleep_delay)
        else:
            sleep_delay = 10

        time.sleep(sleep_delay)
        response.update_status('PyWPS Process started. Waiting...', 20)
        time.sleep(sleep_delay)
        response.update_status('PyWPS Process started. Waiting...', 40)
        time.sleep(sleep_delay)
        response.update_status('PyWPS Process started. Waiting...', 60)
        time.sleep(sleep_delay)
        response.update_status('PyWPS Process started. Waiting...', 80)
        time.sleep(sleep_delay)
        response.outputs['sleep_output'].data = 'done sleeping'

        return response