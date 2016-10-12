##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################

__author__ = "Jachym Cepicky"
__email__ = "jachym.cepicky@gmail.com"

from pywps.Process import WPSProcess

myFirstProcess = WPSProcess(identifier="firstInstance",
                            title="First instance process")

mySecondProcess = WPSProcess(identifier="secondInstance",
                            title="Second instance process")
