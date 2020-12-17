##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import pywps.configuration as config
from pywps.processing.basic import Processing
from pywps.exceptions import SchedulerNotAvailable
from pywps.response.status import WPS_STATUS

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
        self.job.wps_response._update_status(WPS_STATUS.ACCEPTED, 'Submitting job ...', 0)
        # run remote pywps process
        jobid = self.run_job()
        self.job.wps_response._update_status(WPS_STATUS.ACCEPTED,
                                             'Your job has been submitted with ID {}'.format(jobid), 0)

    def run_job(self):
        LOGGER.info("Submitting job ...")
        try:
            import drmaa
            with drmaa.Session() as session:
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
                    import shutil
                    cfg_file = os.path.join(self.job.workdir, "pywps.cfg")
                    shutil.copy2(os.getenv('PYWPS_CFG'), cfg_file)
                    LOGGER.debug("Copied pywps config: {}".format(cfg_file))
                    jt.args = ['-c', cfg_file, dump_filename]
                else:
                    jt.args = [dump_filename]
                drmaa_native_specification = config.get_config_value('processing', 'drmaa_native_specification')
                if drmaa_native_specification:
                    jt.nativeSpecification = drmaa_native_specification
                jt.joinFiles = False
                jt.errorPath = ":{}".format(os.path.join(self.job.workdir, "job-error.txt"))
                jt.outputPath = ":{}".format(os.path.join(self.job.workdir, "job-output.txt"))
                # run job
                jobid = session.runJob(jt)
                LOGGER.info('Your job has been submitted with ID {}'.format(jobid))
                # show status
                import time
                time.sleep(1)
                LOGGER.info('Job status: {}'.format(session.jobStatus(jobid)))
                # Cleaning up
                session.deleteJobTemplate(jt)
        except Exception as e:
            raise SchedulerNotAvailable("Could not submit job: {}".format(str(e)))
        return jobid
