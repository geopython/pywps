# List of known complex data formats
# you can use any other, but thise are widly known and supported by polular
# software packages
# based on Web Processing Service Best Practices Discussion Paper, OGC 12-029
# http://opengeospatial.org/standards/wps

from enum import Enum


class Formats(Enum):
    """List of known mimetypes
    """
    GEOJSON = 'application/geojson'
    JSON = 'application/json'
    SHP = 'application/x-zipped-shp'
    GML = 'application/gml+xml'
    GEOTIFF = 'image/tiff; subtype=geotiff'
    WCS = 'application/xogc-wcs'
    WCS100 = 'application/x-ogc-wcs; version=1.0.0'
    WCS110 = 'application/x-ogc-wcs; version=1.1.0'
    WCS20 = 'application/x-ogc-wcs; version=2.0'
    WFS = 'application/x-ogc-wfs'
    WFS100 = 'application/x-ogc-wfs; version=1.0.0'
    WFS110 = 'application/x-ogc-wfs; version=1.1.0'
    WFS20 = 'application/x-ogc-wfs; version=2.0'
    WMS = 'application/x-ogc-wms'
    WMS130 = 'application/x-ogc-wms; version=1.3.0'
    WMS110 = 'application/x-ogc-wms; version=1.1.0'
    WMS100 = 'application/x-ogc-wms; version=1.0.0'
