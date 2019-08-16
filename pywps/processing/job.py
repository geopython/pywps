##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import tempfile
import pywps.configuration as config
from pywps import Process, WPSRequest
from pywps.response.execute import ExecuteResponse

import json

import logging
LOGGER = logging.getLogger("PYWPS")


class Job(object):
    """
    :class:`Job` represents a processing job.
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

    @property
    def json(self):
        """Return JSON encoded representation of the request
        """
        obj = {
            'process': self.process.json,
            'wps_request': self.wps_request.json,
        }

        return json.dumps(obj, allow_nan=False)

    @classmethod
    def from_json(cls, value):
        """init this request from json back again

        :param value: the json (not string) representation
        """
        process = Process.from_json(value['process'])
        wps_request = WPSRequest()
        wps_request.json = json.loads(value['wps_request'])
        wps_response = ExecuteResponse(
            wps_request=wps_request,
            uuid=process.uuid,
            process=process)
        wps_response.store_status_file = True
        new_job = Job(
            process=Process.from_json(value['process']),
            wps_request=wps_request,
            wps_response=wps_response)
        return new_job

    def dump(self):
        LOGGER.debug('dump job ...')
        filename = tempfile.mkstemp(prefix='job_', suffix='.dump', dir=self.workdir)[1]
        with open(filename, 'w') as fp:
            fp.write(self.json)
            LOGGER.debug("dumped job status to {}".format(filename))
            return filename
        return None

    @classmethod
    def load(cls, filename):
        LOGGER.debug('load job ...')
        with open(filename, 'r') as fp:
            job = Job.from_json(json.load(fp))
            return job
        return None

    def run(self):
        getattr(self.process, self.method)(self.wps_request, self.wps_response)


class JobLauncher(object):
    """
    :class:`JobLauncher` is a command line tool to launch a job from a file
    with a dumped job state.

    Example call: ``joblauncher -c /etc/pywps.cfg job-1001.dump``
    """
    def create_parser(self):
        import argparse
        parser = argparse.ArgumentParser(prog="joblauncher")
        parser.add_argument("-c", "--config", help="Path to pywps configuration.")
        parser.add_argument("filename", help="File with dumped pywps job object.")
        return parser

    def run(self, args):
        if args.config:
            LOGGER.debug("using pywps_cfg={}".format(args.config))
            os.environ['PYWPS_CFG'] = args.config
        self._run_job(args.filename)

    def _run_job(self, filename):
        job = Job.load(filename)
        # init config
        if 'PYWPS_CFG' in os.environ:
            config.load_configuration(os.environ['PYWPS_CFG'])
        # update PATH
        os.environ['PATH'] = "{0}:{1}".format(
            config.get_config_value('processing', 'path'),
            os.environ.get('PATH'))
        # cd into workdir
        os.chdir(job.workdir)
        # init logger ... code copied from app.Service
        if config.get_config_value('logging', 'file') and config.get_config_value('logging', 'level'):
            LOGGER.setLevel(getattr(logging, config.get_config_value('logging', 'level')))
            if not LOGGER.handlers:  # hasHandlers in Python 3.x
                fh = logging.FileHandler(config.get_config_value('logging', 'file'))
                fh.setFormatter(logging.Formatter(config.get_config_value('logging', 'format')))
                LOGGER.addHandler(fh)
        else:  # NullHandler
            if not LOGGER.handlers:
                LOGGER.addHandler(logging.NullHandler())
        job.run()


def launcher():
    """
    Run job launcher command line.
    """
    job_launcher = JobLauncher()
    parser = job_launcher.create_parser()
    args = parser.parse_args()
    job_launcher.run(args)
