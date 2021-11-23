##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import warnings

try:
    import netCDF4  # noqa
except ImportError:
    warnings.warn('Complex validation requires netCDF4 support.')
