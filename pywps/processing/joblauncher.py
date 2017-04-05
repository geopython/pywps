##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps.processing.basic import Job


class JobLauncher(object):
    def create_parser(self):
        import argparse
        parser = argparse.ArgumentParser(prog="launch")
        parser.add_argument("filename", help="File with dumped pywps job object.")
        return parser

    def run(self, args):
        self._run_job(args.filename)

    def _run_job(self, filename):
        job = Job.load(filename)
        job.run()


def main():
    launcher = JobLauncher()
    parser = launcher.create_parser()
    args = parser.parse_args()
    launcher.run(args)
