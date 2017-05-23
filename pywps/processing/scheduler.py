##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import pywps.configuration as config
from pywps.processing.basic import Processing
from pywps.exceptions import SchedulerNotAvailable

import logging
LOGGER = logging.getLogger("PYWPS")


def run_batch(filename):
    LOGGER.info("Submitting job to scheduler ...")
    try:
        import drmaa
        session = drmaa.Session()
        # init session
        session.initialize()
        jt = session.createJobTemplate()
        jt.remoteCommand = os.path.join(
            config.get_config_value('processing', 'path'),
            'joblauncher')
        if os.getenv("PYWPS_CFG"):
            jt.args = ['-c', os.getenv('PYWPS_CFG'), filename]
        else:
            jt.args = [filename]
        jt.joinFiles = True
        jt.outputPath = "{0}:job.out".format(config.get_config_value('processing', 'remotehost'))
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

    def start(self):
        self.job.wps_response.update_status('Submitting job ...', 0)
        # dump job to file
        dump_file_name = self.job.dump()
        # run remote pywps process
        response = run_batch(filename=dump_file_name)
        self.job.wps_response.update_status('Submitted: %s'.format(response), 0)
