##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
"""
WPS Output classes
"""

import lxml.etree as etree
import os
from pywps.inout import basic
from pywps.inout.storage import FileStorage
from pywps.validator.mode import MODE
from pywps import configuration as config


class BoundingBoxOutput(basic.BBoxOutput):
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
        basic.BBoxOutput.__init__(self, identifier, title=title,
                                  abstract=abstract, keywords=keywords, crss=crss,
                                  dimensions=dimensions, mode=mode)

        self.metadata = metadata
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.as_reference = as_reference

    @property
    def json(self):
        """Get JSON representation of the output
        """
        return {
            'identifier': self.identifier,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'min_occurs': self.min_occurs,
            'max_occurs': self.max_occurs,
            'metadata': self.metadata,
            'type': 'bbox',
            'crs': self.crs,
            'crss': self.crss,
            'dimensions': self.dimensions,
            'bbox': (self.ll, self.ur),
            'workdir': self.workdir,
            'mode': self.valid_mode,
        }


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
        """Get JSON representation of the output
        """
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

        if self.data:

            if self.data_format.mime_type in ["application/xml", "application/gml+xml", "text/xml"]:
                # Note that in a client-server round trip, the original and returned file will not be identical.
                data_doc = etree.parse(self.file)
                data["data"] = etree.tostring(data_doc, pretty_print=True).decode('utf-8')

            else:
                if self.data_format.encoding == 'base64':
                    data["data"] = self.base64.decode('utf-8')

                else:
                    # Otherwise we assume all other formats are unsafe and need to be enclosed in a CDATA tag.
                    if isinstance(self.data, bytes):
                        out = self.data.encode(self.data_format.encoding or 'utf-8')
                    else:
                        out = self.data

                    data["data"] = u'<![CDATA[{}]]>'.format(out)

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
        """Get JSON representation of the output
        """
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


class MetaFile:
    """MetaFile object."""
    def __init__(self, identity=None, description=None, fmt=None):
        """Create a `MetaFile` object.

        :param str identity: human readable identity.
        :param str description: human readable file description.
        :param pywps.FORMAT fmt: file mime type.

        The content of each metafile is set like `ComplexOutputs`, ie
        using either the `data`, `file`, `stream` or `url` properties.

        The metalink document is created by a `MetaLink` instance, which
        holds a number of `MetaFile` instances.
        """
        self._output = ComplexOutput(
            identifier=identity or '',
            title=description or '',
            as_reference=True,
            supported_formats=[fmt, ],
        )

    def _set_workdir(self, workdir):
        self._output.workdir = workdir

    @property
    def hash(self):
        """Text construct that conveys a cryptographic hash for a file.

        All hashes are encoded in lowercase hexadecimal format.  Hashes
        are used to verify the integrity of a complete file or portion
        of a file to determine if the file has been transferred without
        any errors.
        """
        import hashlib
        m = hashlib.sha256()
        with open(self.file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                m.update(chunk)
        return m.hexdigest()

    @property
    def identity(self):
        """Human-readable identity."""
        return self._output.identifier

    @property
    def name(self):
        """Indicate a specific file in a document describing multiple files."""
        js = self._output.json
        (_, name) = os.path.split(js.get('href', 'http:///'))
        return name

    @property
    def size(self):
        """Length of the linked content in octets."""
        return os.stat(self.file).st_size

    @property
    def urls(self):
        js = self._output.json
        return [js.get('href', ''), ]

    @property
    def mediatype(self):
        """Multipurpose Internet Mail Extensions (MIME) media type
        [RFC4288] of the metadata file available at the IRI."""
        return self._output.data_format.mime_type

    @property
    def data(self):
        return self._output.data

    @data.setter
    def data(self, value):
        self._output.data = value

    @property
    def file(self):
        return self._output.file

    @file.setter
    def file(self, value):
        self._output.file = value

    @property
    def url(self):
        return self._output.url

    @url.setter
    def url(self, value):
        self._output.url = value

    @property
    def stream(self):
        return self._output.stream

    @stream.setter
    def stream(self, value):
        self._output.stream = value

    def __str__(self):
        out = "MetaFile {}:".format(self.name)
        for url in self.urls:
            out += "\n\t{}".format(url)
        return out

    def __repr__(self):
        return "<pywps.inout.outputs.MetaFile {}>".format(self.name)


class MetaLink:
    _xml_template = 'metalink/3.0/main.xml'
    # Specs: https://www.metalinker.org/Metalink_3.0_Spec.pdf

    def __init__(self, identity=None, description=None, publisher=None, files=(),
                 workdir=None, checksums=False):
        """Create a MetaLink v3.0 instance.

        :param str identity: human readable identity.
        :param str description: human readable file description.
        :param str publisher: The name of the file's publisher.
        :param tuple files: Sequence of files to include in Metalink. Can also be added using `append`.
        :param str workdir: Work directory to store temporary files.
        :param bool checksums: Whether to compute checksums on files.

        To use, first append `MetaFile` instances, then write the metalink using the `xml`
        property.

        Methods:
            - `append`: add a `MetaFile` instance
        """
        self.identity = identity
        self.description = description
        self.workdir = workdir
        self.publisher = publisher
        self.files = []
        self.checksums = checksums

        for file in files:
            self.append(file)
        self._load_template()

    def append(self, file):
        """Append a `MetaFile` instance."""
        if not isinstance(file, MetaFile):
            raise ValueError("file must be a MetaFile instance.")
        file._set_workdir(self.workdir)
        self.files.append(file)

    @property
    def xml(self):
        return self._template.render(meta=self)

    @property
    def origin(self):
        """IRI where the Metalink Document was originally published.
        If the dynamic attribute of metalink:origin is "true", then
        updated versions of the Metalink can be found at this IRI.
        """
        return ""

    @property
    def published(self):
        """Date construct indicating an instant in time associated
        with an event early in the life cycle of the entry."""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def generator(self):
        """Generating agent name and version used to generate a
        Metalink Document, for debugging and other purposes."""
        import pywps
        return "PyWPS/{}".format(pywps.__version__)

    @property
    def url(self):
        """Return the server URL."""
        return config.get_config_value('server', 'url')

    def _load_template(self):
        from pywps.response import RelEnvironment
        from jinja2 import PackageLoader

        template_env = RelEnvironment(
            loader=PackageLoader('pywps', 'templates'),
            trim_blocks=True, lstrip_blocks=True,
            autoescape=True, )

        self._template = template_env.get_template(self._xml_template)


class MetaLink4(MetaLink):
    _xml_template = 'metalink/4.0/main.xml'
    # Specs: https://tools.ietf.org/html/rfc5854
