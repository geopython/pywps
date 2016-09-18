"""Validatating functions for various inputs
"""
###############################################################################
#
# Copyright (C) 2014-2016 PyWPS Development Team, represented by
# PyWPS Project Steering Committee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
###############################################################################

import logging
from collections import namedtuple
from pywps.validator.complexvalidator import validategml, validateshapefile, validategeojson, validategeotiff
from pywps.validator.literalvalidator import validate_anyvalue, validate_allowed_values
import logging
from pywps.validator.mode import MODE
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
