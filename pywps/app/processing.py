def Process(process, wps_request, wps_response):
    return MultiProcessing(process, wps_request, wps_response)


class BaseProcessor(object):

    def __init__(self, process, wps_request, wps_response):
        self.process = process
        self.wps_request = wps_request
        self.wps_response = wps_response

    def start(self):
        raise NotImplementedError("Needs to implemented in a base class.")


class MultiProcessing(BaseProcessor):

    def start(self):
        import multiprocessing
        process = multiprocessing.Process(
            target=getattr(self.process, '_run_process'),
            args=(self.wps_request, self.wps_response)
        )
        process.start()


class Slurm(BaseProcessor):

    def start(self):
        pass
