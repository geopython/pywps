##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

try:
    from osgeo import gdal, ogr
except ImportError as err:
    from pywps.exceptions import NoApplicableCode
    raise NoApplicableCode('Complex validation requires GDAL/OGR support')
