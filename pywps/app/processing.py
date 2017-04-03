def Process(process, wps_request, wps_response):
    return MultiProcessing(process, wps_request, wps_response)
    #return Slurm(process, wps_request, wps_response)


class BaseProcessor(object):

    def __init__(self, process, wps_request, wps_response):
        self.process = process
        self.method = '_run_process'
        self.wps_request = wps_request
        self.wps_response = wps_response

    def start(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def terminate(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def pause(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def resume(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")


class MultiProcessing(BaseProcessor):

    def start(self):
        import multiprocessing
        process = multiprocessing.Process(
            target=getattr(self.process, self.method),
            args=(self.wps_request, self.wps_response)
        )
        process.start()


class Slurm(BaseProcessor):

    def run(self):
        getattr(self.process, self.method)(self.wps_request, self.wps_response)

    def start(self):
        import pickle
        marshalled = pickle.dumps(self)
        obj = pickle.loads(marshalled)
        obj.run()
