##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################
from pywps.Process import WPSProcess

myFirstProcess = WPSProcess(identifier="firstInstance",
                            title="First instance process")

mySecondProcess = WPSProcess(identifier="secondInstance",
                            title="Second instance process")

#WPSProcess(identifier="firstInstance", title="First instance process")
