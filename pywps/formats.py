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
