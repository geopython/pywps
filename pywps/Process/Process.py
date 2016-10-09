##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################

from pywps.Process import WPSProcess
import sys
print >>sys.stderr, """PyWPS Warning: Usage of"""
print >>sys.stderr, """PyWPS Warning:       from pywps.Process.Process import WPSProcess"""
print >>sys.stderr, """PyWPS Warning: is deprecated. Use """
print >>sys.stderr, """PyWPS Warning:       from pywps.Process import WPSProcess"""
print >>sys.stderr, """PyWPS Warning: instead!"""
