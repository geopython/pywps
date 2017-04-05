##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps.processing.basic import MultiProcessing
from pywps.processing.slurm import launch_slurm_job
from pywps.processing.slurm import Slurm


def Process(process, wps_request, wps_response):
    #return MultiProcessing(process, wps_request, wps_response)
    return Slurm(process, wps_request, wps_response)
