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


class Scheduler(Processing):
    """
    :class:`Scheduler` is processing implementation to run jobs on schedulers
    like slurm, grid-engine and torque. It uses the drmaa python library
    as client to launch jobs on a scheduler system.

    See: http://drmaa-python.readthedocs.io/en/latest/index.html
    """

    def start(self):
        self.job.wps_response.update_status('Submitting job ...', 0)
        # run remote pywps process
        jobid = self.run_job()
        self.job.wps_response.update_status('Your job has been submitted with ID %s'.format(jobid), 0)

    def run_job(self):
        LOGGER.info("Submitting job ...")
        try:
            import drmaa
            session = drmaa.Session()
            # init session
            session.initialize()
            # dump job to file
            dump_filename = self.job.dump()
            if not dump_filename:
                raise Exception("Could not dump job status.")
            # prepare remote command
            jt = session.createJobTemplate()
            jt.remoteCommand = os.path.join(
                config.get_config_value('processing', 'path'),
                'joblauncher')
            if os.getenv("PYWPS_CFG"):
                jt.args = ['-c', os.getenv('PYWPS_CFG'), dump_filename]
            else:
                jt.args = [filename]
            jt.joinFiles = True
            jt.outputPath = "{0}:job.out".format(config.get_config_value('processing', 'remotehost'))
            # run job
            jobid = session.runJob(jt)
            LOGGER.info('Your job has been submitted with ID %s', jobid)
            # Cleaning up
            session.deleteJobTemplate(jt)
            # close session
            session.exit()
        except Exception as e:
            raise SchedulerNotAvailable("Could not submit job: %s" % str(e))
        return jobid
