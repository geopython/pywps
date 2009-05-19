#!c:/Python26/python.exe
#
# Author: Jachym Cepicky
# Purpose: CGI script for wrapping PyWPS script, in python, tested on MS
# Windows
# Licence: GNU/GPL
# Usage: Put this script to your web server cgi-bin directory, e.g.
# c:\Osgeo4W\bin\ 

# NOTE: tested on windows/apache (Osgeo4W)

import os
import sys
sys.path.append("c:\pywps/trunk")

from wps import *

os.environ["PYWPS_PROCESSES"] = "c:\pywps\processes"
os.environ["PYWPS_CFG"] = "c:\pywps\pywps.cfg"

mywps = WPS()
