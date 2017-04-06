##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import tempfile
import pywps.configuration as config


class Job(object):
    def __init__(self, process, wps_request, wps_response):
        self.process = process
        self.method = '_run_process'
        self.wps_request = wps_request
        self.wps_response = wps_response

    @property
    def workdir(self):
        return self.process.workdir

    @property
    def uuid(self):
        return self.process.uuid

    def dump(self):
        import dill
        filename = tempfile.mkstemp(prefix='job_', suffix='.dump', dir=self.workdir)[1]
        with open(filename, 'w') as fp:
            dill.dump(self, fp)
            return filename
        return None

    @classmethod
    def load(cls, filename):
        import dill
        with open(filename) as fp:
            job = dill.load(fp)
            return job
        return None

    def run(self):
        getattr(self.process, self.method)(self.wps_request, self.wps_response)


class Processing(object):

    def __init__(self, process, wps_request, wps_response):
        self.job = Job(process, wps_request, wps_response)

    def start(self):
        raise NotImplementedError("Needs to be implemented in subclass.")

    def cancel(self):
        raise NotImplementedError("Needs to be implemented in subclass.")


class MultiProcessing(Processing):

    def start(self):
        import multiprocessing
        process = multiprocessing.Process(
            target=getattr(self.job.process, self.job.method),
            args=(self.job.wps_request, self.job.wps_response)
        )
        process.start()
