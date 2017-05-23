##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import pywps.configuration as config
from pywps.processing.basic import MultiProcessing
from pywps.processing.slurm import Slurm
from pywps.processing.scheduler import Scheduler

import logging
LOGGER = logging.getLogger("PYWPS")

MULTIPROCESSING = 'multiprocessing'
SCHEDULER = 'scheduler'
DEFAULT = MULTIPROCESSING


def Process(process, wps_request, wps_response):
    """
    Factory method (looking like a class) to return the
    configured processing class.

    :return: instance of :class:`pywps.processing.Processing`
    """
    mode = config.get_config_value("processing", "mode")
    LOGGER.info("Processing mode: %s", mode)
    if mode == SCHEDULER:
        process = Scheduler(process, wps_request, wps_response)
    else:
        process = MultiProcessing(process, wps_request, wps_response)
    return process
