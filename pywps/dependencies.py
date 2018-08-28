##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
from pywps.exceptions import NoApplicableCode
import warnings

# It seems these should raise warnings, not errors.
try:
    from osgeo import gdal, ogr
except ImportError as err:
    warnings.warn('Complex validation requires GDAL/OGR support.')
    # raise NoApplicableCode('Complex validation requires GDAL/OGR support.')

try:
    import netCDF4
except ImportError as err:
    warnings.warn('Complex validation requires netCDF4 support.')
    # raise NoApplicableCode('Complex validation requires netCDF4 support.')
