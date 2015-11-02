"""List of supported formats
"""
from collections import namedtuple

_FORMAT = namedtuple('FormatDefintion', 'mime_type,'
                     'extension, schema')
_FORMATS = namedtuple('FORMATS', 'GEOJSON, JSON, SHP, GML, GEOTIFF, WCS,'
                                 'WCS100, WCS110, WCS20, WFS, WFS100,'
                                 'WFS110, WFS20, WMS, WMS130, WMS110,'
                                 'WMS100')
FORMATS = _FORMATS(
    _FORMAT('application/vnd.geo+json', '.geojson', None),
    _FORMAT('application/json', '.json', None),
    _FORMAT('application/x-zipped-shp', '.zip', None),
    _FORMAT('application/gml+xml', '.gml', None),
    _FORMAT('image/tiff; subtype=geotiff', '.tiff', None),
    _FORMAT('application/xogc-wcs', '.xml', None),
    _FORMAT('application/x-ogc-wcs; version=1.0.0', '.xml', None),
    _FORMAT('application/x-ogc-wcs; version=1.1.0', '.xml', None),
    _FORMAT('application/x-ogc-wcs; version=2.0', '.xml', None),
    _FORMAT('application/x-ogc-wfs', '.xml', None),
    _FORMAT('application/x-ogc-wfs; version=1.0.0', '.xml', None),
    _FORMAT('application/x-ogc-wfs; version=1.1.0', '.xml', None),
    _FORMAT('application/x-ogc-wfs; version=2.0', '.xml', None),
    _FORMAT('application/x-ogc-wms', '.xml', None),
    _FORMAT('application/x-ogc-wms; version=1.3.0', '.xml', None),
    _FORMAT('application/x-ogc-wms; version=1.1.0', '.xml', None),
    _FORMAT('application/x-ogc-wms; version=1.0.0', '.xml', None)
)

