##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import pywps.configuration as config
from pywps.processing.basic import MultiProcessing
from pywps.processing.scheduler import Scheduler
# api only
from pywps.processing.basic import Processing  # noqa: F401
from pywps.processing.job import Job  # noqa: F401

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
    LOGGER.info("Processing mode: {}".format(mode))
    if mode == SCHEDULER:
        process = Scheduler(process, wps_request, wps_response)
    else:
        process = MultiProcessing(process, wps_request, wps_response)
    return process
