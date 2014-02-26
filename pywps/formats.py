# List of known complex data formats
# you can use any other, but thise are widly known and supported by polular
# software packages
# based on Web Processing Service Best Practices Discussion Paper, OGC 12-029
# http://opengeospatial.org/standards/wps

"""List of known mimetypes
"""

FORMATS = {
    'GEOJSON': ['application/geojson', '.geojson'],
    'JSON': ['application/json', '.json'],
    'SHP': ['application/x-zipped-shp', '.zip'],
    'GML': ['application/gml+xml', '.gml'],
    'GEOTIFF': ['image/tiff; subtype=geotiff', '.tiff'],
    'WCS': ['application/xogc-wcs', '.xml'],
    'WCS100': ['application/x-ogc-wcs; version=1.0.0', '.xml'],
    'WCS110': ['application/x-ogc-wcs; version=1.1.0', '.xml'],
    'WCS20': ['application/x-ogc-wcs; version=2.0', '.xml'],
    'WFS': ['application/x-ogc-wfs', '.xml'],
    'WFS100': ['application/x-ogc-wfs; version=1.0.0', '.xml'],
    'WFS110': ['application/x-ogc-wfs; version=1.1.0', '.xml'],
    'WFS20': ['application/x-ogc-wfs; version=2.0', '.xml'],
    'WMS': ['application/x-ogc-wms', '.xml'],
    'WMS130': ['application/x-ogc-wms; version=1.3.0', '.xml'],
    'WMS110': ['application/x-ogc-wms; version=1.1.0', '.xml'],
    'WMS100': ['application/x-ogc-wms; version=1.0.0','.xml']
}
