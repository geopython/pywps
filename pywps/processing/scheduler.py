##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import sys
import tempfile
import pywps.configuration as config
from pywps.processing.basic import Processing
from pywps.exceptions import SchedulerNotAvailable

import logging
LOGGER = logging.getLogger("PYWPS")


BATCH_JOB_TMPL = """\
#!/bin/bash
export PYWPS_CFG="{pywps_cfg}"
export PATH="{path}":$PATH
joblauncher "{filename}"
"""


def run_batch(filename):
    LOGGER.info("Submitting job to scheduler ...")
    try:
        import drmaa
        session = drmaa.Session()
        # init session
        session.initialize()
        jt = session.createJobTemplate()
        jt.remoteCommand = filename
        # jt.args = ['42', 'Simon says:']
        jt.joinFiles = True
        jt.outputPath = "{0}:output".format(config.get_config_value('processing', 'remotehost'))
        jobid = session.runJob(jt)
        LOGGER.info('Your job has been submitted with ID %s', jobid)
        # Cleaning up
        session.deleteJobTemplate(jt)
        # close session
        session.exit()
    except Exception as e:
        raise SchedulerNotAvailable("Could not submit job to scheduler: %s" % str(e))
    return jobid


class Scheduler(Processing):
    """
    :class:`Scheduler` is processing implementation to run jobs on schedulers
    like slurm, grid-engine and torque. It uses the drmaa python library
    as client to launch jobs on a scheduler system.
    """
    @property
    def workdir(self):
        return self.job.workdir

    def _build_submit_file(self, dump_file_name):
        submit_file_name = tempfile.mkstemp(prefix='batch_', suffix='.sh', dir=self.workdir)[1]
        with open(submit_file_name, 'w') as fp:
            fp.write(BATCH_JOB_TMPL.format(
                workdir=self.workdir,
                pywps_cfg=os.getenv('PYWPS_CFG'),
                path=config.get_config_value('processing', 'path'),
                filename=dump_file_name))
            return submit_file_name
        return None

    def start(self):
        self.job.wps_response.update_status('Submitting job ...', 0)
        # dump job to file
        dump_file_name = self.job.dump()
        # write submit script
        submit_file_name = self._build_submit_file(dump_file_name)
        # run remote pywps process
        response = run_batch(filename=submit_file_name)
        self.job.wps_response.update_status('Submitted: %s'.format(response), 0)
