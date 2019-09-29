#!/usr/bin/env python3

from daemon import DaemonContext
import sys
import time
import logging

from pywps import dblog
from pywps.app.WPSRequest import WPSRequest
from pywps.app.Service import Service
import pywps.processing
import pywps.configuration as config
import json
import lockfile
import os
import signal

# Configure logging
LOGGER = logging.getLogger("PYWPS")


def watchdog():

    global LOGGER
    config.load_configuration()

    LOGGER.setLevel(getattr(logging, config.get_config_value('logging', 'level')))

    max_time = int(config.get_config_value('daemon', 'pause'))
    maxparallel = int(config.get_config_value('server', 'parallelprocesses'))

    while True:
        # Logging errors and exceptions
        try:
            running, stored = dblog.get_process_counts()
            LOGGER.info('PyWPS daemon: {} running processes {} stored requests'.format(
                running, stored))

            while (running < maxparallel or maxparallel == -1) and stored > 0:
                launch_process()
                running, stored = dblog.get_process_counts()

        except Exception as e:
            LOGGER.exception("PyWPS daemon failed: {}".format(str(e)))

        # The daemon will repeat your tasks according to this variable
        # it's in second so 60 is 1 minute, 3600 is 1 hour, etc.
        time.sleep(max_time)


def launch_process():
    """Look at the queue of async process, if the queue is not empty launch
    the next pending request.
    """
    try:
        from pywps.processing.job import Job, JobLauncher

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


def start(pidfile):

    with DaemonContext(pidfile=pidfile) as context:
        context.signal_map = {
            # signal.SIGTERM: program_cleanup,
            signal.SIGHUP: 'terminate',
            # signal.SIGUSR1: reload_program_config,
        }

        watchdog()


if __name__ == "__main__":

    config.load_configuration()
    pidfile = config.get_config_value("daemon", "pidfile")
    lockfile = lockfile.FileLock(pidfile)
    print("PIDFile: ", pidfile)
    print("LOCKFile: ", lockfile)

    if len(sys.argv) == 2:

        if 'start' == sys.argv[1]:
            try:
                print("Starting pywps daemon...")
                start(lockfile)
            except Exception as e:
                print(e)
                pass

#        elif 'stop' == sys.argv[1]:
#            print ("Stopping pywps demon...")
#            stop(locfile)
#
#        elif 'restart' == sys.argv[1]:
#            print("Restaring pywps daemon...")
#            restart()
#
#        elif 'status' == sys.argv[1]:
#            try:
#                pf = file(pidfile,'r')
#                pid = int(pf.read().strip())
#                pf.close()
#            except IOError:
#                pid = None
#            except SystemExit:
#                pid = None
#
#            if pid:
#                print('PyWPS Daemon is running as pid {}'.format(pid))
#            else:
#                print('PyWPS Daemon is not running.')

        elif 'watchdog' == sys.argv[1]:
            watchdog()

        else:
            print("Unknown command")
            sys.exit(2)
            sys.exit(0)
    else:
        print("usage: %s start|watchdog" % sys.argv[0])
        sys.exit(2)
