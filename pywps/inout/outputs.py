##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
"""
WPS Output classes
"""

import lxml.etree as etree
import six
from pywps.inout import basic
from pywps.inout.storage import FileStorage
from pywps.validator.mode import MODE


class BoundingBoxOutput(basic.BBoxInput):
    """
    :param identifier: The name of this input.
    :param str title: Title of the input
    :param str abstract: Input abstract
    :param crss: List of supported coordinate reference system (e.g. ['EPSG:4326'])
    :param int dimensions: number of dimensions (2 or 3)
    :param int min_occurs: minimum occurence
    :param int max_occurs: maximum occurence
    :param pywps.validator.mode.MODE mode: validation mode (none to strict)
    :param metadata: List of metadata advertised by this process. They
                     should be :class:`pywps.app.Common.Metadata` objects.
    """

    def __init__(self, identifier, title, crss, abstract='', keywords=[],
                 dimensions=2, metadata=[], min_occurs='1',
                 max_occurs='1', as_reference=False,
                 mode=MODE.NONE):
        basic.BBoxInput.__init__(self, identifier, title=title,
                                 abstract=abstract, keywords=keywords, crss=crss,
                                 dimensions=dimensions, mode=mode)

        self.metadata = metadata
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.as_reference = as_reference


class ComplexOutput(basic.ComplexOutput):
    """
    :param identifier: The name of this output.
    :param title: Readable form of the output name.
    :param supported_formats: List of supported
        formats. The first format in the list will be used as the default.
    :type supported_formats: (pywps.inout.formats.Format, )
    :param str abstract: Description of the output
    :param pywps.validator.mode.MODE mode: validation mode (none to strict)
    :param metadata: List of metadata advertised by this process. They
                     should be :class:`pywps.app.Common.Metadata` objects.
    """

    def __init__(self, identifier, title, supported_formats=None,
                 abstract='', keywords=[], metadata=None,
                 as_reference=False, mode=MODE.NONE):
        if metadata is None:
            metadata = []

        basic.ComplexOutput.__init__(self, identifier, title=title,
                                     abstract=abstract, keywords=keywords,
                                     supported_formats=supported_formats,
                                     mode=mode)
        self.metadata = metadata
        self.as_reference = as_reference

        self.storage = None

    @property
    def json(self):

        data = {
            "identifier": self.identifier,
            "title": self.title,
            "abstract": self.abstract,
            'keywords': self.keywords,
            'type': 'complex',
            'supported_formats': [frmt.json for frmt in self.supported_formats],
            'asreference': self.as_reference,
            'data_format': self.data_format.json if self.data_format else None,
            'file': self.file if self.prop == 'file' else None,
            'workdir': self.workdir,
            'mode': self.valid_mode,
            'min_occurs': self.min_occurs,
            'max_occurs': self.max_occurs
        }

        if self.as_reference:
            data = self._json_reference(data)
        else:
            data = self._json_data(data)

        if self.data_format:
            if self.data_format.mime_type:
                data['mimetype'] = self.data_format.mime_type
            if self.data_format.encoding:
                data['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                data['schema'] = self.data_format.schema

        return data

    def _json_reference(self, data):
        """Return Reference node
        """
        data["type"] = "reference"

        # get_url will create the file and return the url for it
        if self.prop == 'url':
            data["href"] = self.url
        elif self.prop is not None:
            self.storage = FileStorage()
            data["href"] = self.get_url()

        return data

    def _json_data(self, data):
        """Return Data node
        """

        data["type"] = "complex"

        try:
            data_doc = etree.parse(self.file)
            data["data"] = etree.tostring(data_doc, pretty_print=True).decode("utf-8")
        except Exception:

            if self.data:
                # XML compatible formats don't have to be wrapped in a CDATA tag.
                if self.data_format.mime_type in ["application/xml", "application/gml+xml", "text/xml"]:
                    fmt = "{}"
                else:
                    fmt = "<![CDATA[{}]]>"

                if self.data_format.encoding == 'base64':
                    data["data"] = fmt.format(etree.CDATA(self.base64))

                elif isinstance(self.data, six.string_types):
                    if isinstance(self.data, bytes):
                        data["data"] = fmt.format(self.data.decode("utf-8"))
                    else:
                        data["data"] = fmt.format(self.data)

                else:
                    raise NotImplementedError

        return data


class LiteralOutput(basic.LiteralOutput):
    """
    :param identifier: The name of this output.
    :param str title: Title of the input
    :param pywps.inout.literaltypes.LITERAL_DATA_TYPES data_type: data type
    :param str abstract: Input abstract
    :param str uoms: units
    :param pywps.validator.mode.MODE mode: validation mode (none to strict)
    :param metadata: List of metadata advertised by this process. They
                     should be :class:`pywps.app.Common.Metadata` objects.
    """

    def __init__(self, identifier, title, data_type='string', abstract='', keywords=[],
                 metadata=[], uoms=None, mode=MODE.SIMPLE):
        if uoms is None:
            uoms = []
        basic.LiteralOutput.__init__(self, identifier, title=title, abstract=abstract, keywords=keywords,
                                     data_type=data_type, uoms=uoms, mode=mode)
        self.metadata = metadata

    @property
    def json(self):
        data = {
            "identifier": self.identifier,
            "title": self.title,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "data": self.data,
            "data_type": self.data_type,
            "type": "literal",
            "uoms": [u.json for u in self.uoms]
        }

        if self.uom:
            data["uom"] = self.uom.json

        return data
