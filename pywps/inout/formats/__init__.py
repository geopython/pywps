##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


"""List of know mimetypes"""

# List of known complex data formats
# you can use any other, but thise are widly known and supported by popular
# software packages
# based on Web Processing Service Best Practices Discussion Paper, OGC 12-029
# http://opengeospatial.org/standards/wps

from lxml.builder import ElementMaker
from collections import namedtuple
import mimetypes
from pywps.validator.mode import MODE
from pywps.validator.base import emptyvalidator

_FORMAT = namedtuple('FormatDefintion', 'mime_type,'
                     'extension, schema')
_FORMATS = namedtuple('FORMATS', 'GEOJSON, JSON, SHP, GML, GEOTIFF, WCS,'
                                 'WCS100, WCS110, WCS20, WFS, WFS100,'
                                 'WFS110, WFS20, WMS, WMS130, WMS110,'
                                 'WMS100,'
                                 'TEXT, NETCDF')
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
    _FORMAT('application/x-ogc-wms; version=1.0.0', '.xml', None),
    _FORMAT('text/plain', '.txt', None),
    _FORMAT('application/x-netcdf', '.nc', None),
)


def _get_mimetypes():
    """Add FORMATS to system wide mimetypes
    """
    mimetypes.init()
    for pywps_format in FORMATS:
        mimetypes.add_type(pywps_format.mime_type, pywps_format.extension, True)


_get_mimetypes()


class Format(object):
    """Input/output format specification

    Predefined Formats are stored in :class:`pywps.inout.formats.FORMATS`

    :param str mime_type: mimetype definition
    :param str schema: xml schema definition
    :param str encoding: base64 or not
    :param function validate: function, which will perform validation. e.g.
    :param number mode: validation mode
    :param str extension: file extension
    """

    def __init__(self, mime_type,
                 schema=None, encoding=None,
                 validate=emptyvalidator, mode=MODE.SIMPLE,
                 extension=None):
        """Constructor
        """

        self._mime_type = None
        self._encoding = None
        self._schema = None

        self.mime_type = mime_type
        self.encoding = encoding
        self.schema = schema
        self.validate = validate
        self.extension = extension

    @property
    def mime_type(self):
        """Get format mime type
        :rtype: String
        """

        return self._mime_type

    @mime_type.setter
    def mime_type(self, mime_type):
        """Set format mime type
        """
        try:
            # support Format('GML')
            formatdef = getattr(FORMATS, mime_type)
            self._mime_type = formatdef.mime_type
        except AttributeError:
            # if we don't have this as a shortcut, assume it's a real mime type
            self._mime_type = mime_type

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

    def same_as(self, frmt):
        """Check input frmt, if it seems to be the same as self
        """
        return all([frmt.mime_type == self.mime_type,
                    frmt.encoding == self.encoding,
                    frmt.schema == self.schema])

    def describe_xml(self):
        """Return describe process response element
        """

        elmar = ElementMaker()
        doc = elmar.Format(
            elmar.MimeType(self.mime_type)
        )

        if self.encoding:
            doc.append(elmar.Encoding(self.encoding))

        if self.schema:
            doc.append(elmar.Schema(self.schema))

        return doc

    @property
    def json(self):
        """Get format as json
        :rtype: dict
        """
        return {
            'mime_type': self.mime_type,
            'encoding': self.encoding,
            'schema': self.schema,
            'extension': self.extension
        }

    @json.setter
    def json(self, jsonin):
        """Set format from json
        :param jsonin:
        """

        self.mime_type = jsonin['mime_type']
        self.encoding = jsonin['encoding']
        self.schema = jsonin['schema']
        self.extension = jsonin['extension']


def get_format(frmt, validator=None):
    """Return Format instance based on given pywps.inout.FORMATS keyword
    """
    # TODO this should be probably removed, it's used only in tests

    outfrmt = None

    if frmt in FORMATS._asdict():
        formatdef = FORMATS._asdict()[frmt]
        outfrmt = Format(**formatdef._asdict())
        outfrmt.validate = validator
        return outfrmt
    else:
        return Format('None', validate=validator)
