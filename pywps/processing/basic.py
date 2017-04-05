##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


class Processing(object):

    def __init__(self, process, wps_request, wps_response):
        self.process = process
        self.method = '_run_process'
        self.wps_request = wps_request
        self.wps_response = wps_response

    def start(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def cancel(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def suspend(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def resume(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")


class MultiProcessing(Processing):

    def start(self):
        import multiprocessing
        process = multiprocessing.Process(
            target=getattr(self.process, self.method),
            args=(self.wps_request, self.wps_response)
        )
        process.start()
