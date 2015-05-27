# List of known complex data formats
# you can use any other, but thise are widly known and supported by polular
# software packages
# based on Web Processing Service Best Practices Discussion Paper, OGC 12-029
# http://opengeospatial.org/standards/wps

"""List of known mimetypes
"""

from lxml.builder import ElementMaker

FORMATS = {
    'GEOJSON': ['application/vnd.geo+json', '.geojson'],
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

class Format(object):
    """Input/output format specification
    """
    def __init__(self, mime_type, schema=None, encoding=None, validator=None):

        self._mime_type = None
        self._encoding = None
        self._schema = None
        self._validator = None

        self.mime_type = mime_type
        self.encoding = encoding
        self.schema = schema
        self.validator = validator


    @property
    def mime_type(self):
        """Get format mime type
        :rtype: String
        """

        if self._mime_type in FORMATS:
            return FORMATS[self._mime_type][0]
        else:
            return self._mime_type

    @mime_type.setter
    def mime_type(self, mime_type):
        """Set format mime type
        """

        self._mime_type = mime_type

    def get_extension(self):
        return self._mime_type[1]

    @property
    def encoding(self):
        """Get format encoding
        :rtype: String
        """

        if self._encoding:
            return self._encoding
        else:
            return ''

    @encoding.setter
    def encoding(self, encoding):
        """Set format encoding
        """

        self._encoding = encoding

    @property
    def schema(self):
        """Get format schema
        :rtype: String
        """
        if self._schema:
            return self._schema
        else:
            return ''

    @schema.setter
    def schema(self, schema):
        """Set format schema
        """
        self._schema = schema

    @property
    def validator(self):
        """Get format validator
        :rtype: String
        """
        if self._validator:
            return self._validator
        else:
            return ''


    @validator.setter
    def validator(self, validator):
        """Set format validator
        """
        self._validator = validator
        
        
    def describe_xml(self):
        
        E = ElementMaker()
        doc = E.Format(
            E.MimeType(self.mime_type)
        )

        if self.encoding:
            doc.append(E.Encoding(self.encoding))

        if self.schema:
            doc.append(E.Schema(self.schema))
    
        return doc

