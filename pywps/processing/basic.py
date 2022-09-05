##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
import os

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


class DetachProcessing(Processing):
    """
    :class:`DetachProcessing` run job as detached process. The process will be run as child of pid 1
    """

    def start(self):
        pid = os.fork()
        if pid != 0:
            # Wait that the children get detached.
            os.waitpid(pid, 0)
            return

        # Detach ourself.

        # Ensure that we are the session leader to avoid to be zombified.
        os.setsid()
        if os.fork():
            # Stop running now
            os._exit(0)

        # We are the detached child, run the actual process
        try:
            getattr(self.job.process, self.job.method)(self.job.wps_request, self.job.wps_response)
        except Exception:
            pass
        # Ensure to stop ourself here what ever append.
        os._exit(0)
