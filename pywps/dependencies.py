##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import warnings

try:
    from osgeo import gdal, ogr
except ImportError:
    warnings.warn('Complex validation requires GDAL/OGR support.')

try:
    import netCDF4
except ImportError:
    warnings.warn('Complex validation requires netCDF4 support.')
