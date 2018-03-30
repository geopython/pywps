##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps.processing.job import Job


class Processing(object):
    """
    :class:`Processing` is an interface for running jobs.
    """

    def __init__(self, process, wps_request, wps_response):
        self.job = Job(process, wps_request, wps_response)

    def start(self):
        raise NotImplementedError("Needs to be implemented in subclass.")

    def cancel(self):
        raise NotImplementedError("Needs to be implemented in subclass.")


class MultiProcessing(Processing):
    """
    :class:`MultiProcessing` is the default implementation to run jobs using the
    :module:`multiprocessing` module.
    """

    def start(self):
        import multiprocessing
        process = multiprocessing.Process(
            target=getattr(self.job.process, self.job.method),
            args=(self.job.wps_request, self.job.wps_response)
        )
        process.start()
