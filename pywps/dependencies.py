##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


try:
    from osgeo import gdal, ogr
except ImportError as err:
    from pywps.exceptions import NoApplicableCode
    raise NoApplicableCode('Complex validation requires GDAL/OGR support')
