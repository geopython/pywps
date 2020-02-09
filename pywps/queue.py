import time
import logging

from pywps import dblog
import pywps.processing
import pywps.configuration as config
from pywps.log import get_logger
import json

# Configure logging
LOGGER = logging.getLogger("PYWPS")


class JobQueueService(object):
    def __init__(self, cfgfiles=None):
        global LOGGER

        config.load_configuration(cfgfiles)

        LOGGER = get_logger(
            file=config.get_config_value('logging', 'file'),
            level=config.get_config_value('logging', 'level'),
            format=config.get_config_value('logging', 'format'))

        self.max_time = int(config.get_config_value('jobqueue', 'pause'))
        self.maxparallel = int(config.get_config_value('server', 'parallelprocesses'))

    def run(self):
        old_running = old_stored = 0
        while True:
            # Logging errors and exceptions
            try:
                running, stored = dblog.get_process_counts()
                if old_running != running or old_stored != stored:
                    old_running = running
                    old_stored = stored
                    LOGGER.info('PyWPS job queue: {} running processes {} stored requests'.format(
                        running, stored))

                while (running < self.maxparallel or self.maxparallel == -1) and stored > 0:
                    launch_process()
                    running, stored = dblog.get_process_counts()

            except Exception as e:
                LOGGER.exception("PyWPS job queue failed: {}".format(str(e)))

            # The job queue will repeat your tasks according to this variable
            # it's in second so 60 is 1 minute, 3600 is 1 hour, etc.
            time.sleep(self.max_time)


def launch_process():
    """Look at the queue of async process, if the queue is not empty launch
    the next pending request.
    """
    try:
        from pywps.processing.job import Job

        LOGGER.debug("Checking for stored requests")

        stored_request = dblog.pop_first_stored()
        if not stored_request:
            LOGGER.debug("No stored request found, sleeping")
            return

        value = {
            'process': json.loads(stored_request.process.decode("utf-8")),
            'wps_request': json.loads(stored_request.request.decode("utf-8"))
        }
        job = Job.from_json(value)

        processing_process = pywps.processing.Process(
            process=job.process,
            wps_request=job.wps_request,
            wps_response=job.wps_response)
        processing_process.start()

    except Exception as e:
        LOGGER.exception("Could not run stored process. {}".format(e))
        raise e
