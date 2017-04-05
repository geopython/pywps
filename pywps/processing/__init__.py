##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import pywps.configuration as config
from pywps.processing.basic import MultiProcessing
from pywps.processing.slurm import Slurm

import logging
LOGGER = logging.getLogger("PYWPS")

MULTIPROCESSING = 'multiprocessing'
SLURM = 'slurm'


def Process(process, wps_request, wps_response):
    mode = config.get_config_value("extra", "mode")
    LOGGER.info("Configured processing mode: %s", mode)
    if mode == SLURM:
        return Slurm(process, wps_request, wps_response)
    else:
        return MultiProcessing(process, wps_request, wps_response)
