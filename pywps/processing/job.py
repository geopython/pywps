##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import tempfile


class Job(object):
    """
    Job represents the processing job.
    """
    def __init__(self, process, wps_request, wps_response):
        self.process = process
        self.method = '_run_process'
        self.wps_request = wps_request
        self.wps_response = wps_response

    @property
    def name(self):
        return self.process.identifier

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


class JobLauncher(object):
    """
    JobLauncher is a script to launch a job from a file with the dumped job state.

    Call it with: joblauncher job-1001.txt
    """
    def create_parser(self):
        import argparse
        parser = argparse.ArgumentParser(prog="joblauncher")
        parser.add_argument("filename", help="File with dumped pywps job object.")
        return parser

    def run(self, args):
        self._run_job(args.filename)

    def _run_job(self, filename):
        job = Job.load(filename)
        job.run()


def launcher():
    job_launcher = JobLauncher()
    parser = job_launcher.create_parser()
    args = parser.parse_args()
    job_launcher.run(args)
