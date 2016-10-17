##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Validatating functions for various inputs
"""


import logging
from pywps.validator.complexvalidator import validategml, validateshapefile, validategeojson, validategeotiff
from pywps.validator.base import emptyvalidator

LOGGER = logging.getLogger('PYWPS')

_VALIDATORS = {
    'application/vnd.geo+json': validategeojson,
    'application/json': validategeojson,
    'application/x-zipped-shp': validateshapefile,
    'application/gml+xml': validategml,
    'image/tiff; subtype=geotiff': validategeotiff,
    'application/xogc-wcs': emptyvalidator,
    'application/x-ogc-wcs; version=1.0.0': emptyvalidator,
    'application/x-ogc-wcs; version=1.1.0': emptyvalidator,
    'application/x-ogc-wcs; version=2.0': emptyvalidator,
    'application/x-ogc-wfs': emptyvalidator,
    'application/x-ogc-wfs; version=1.0.0': emptyvalidator,
    'application/x-ogc-wfs; version=1.1.0': emptyvalidator,
    'application/x-ogc-wfs; version=2.0': emptyvalidator,
    'application/x-ogc-wms': emptyvalidator,
    'application/x-ogc-wms; version=1.3.0': emptyvalidator,
    'application/x-ogc-wms; version=1.1.0': emptyvalidator,
    'application/x-ogc-wms; version=1.0.0': emptyvalidator
}


def get_validator(identifier):
    """Return validator function for given mime_type

    identifier can be either full mime_type or data type identifier
    """

    if identifier in _VALIDATORS:
        LOGGER.debug('validator: %s', _VALIDATORS[identifier])
        return _VALIDATORS[identifier]
    else:
        LOGGER.debug('empty validator')
        return emptyvalidator
