##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import lxml.etree as etree
import six
from pywps.exceptions import InvalidParameterValue
from pywps.inout.formats import Format
from pywps.inout import basic
from copy import deepcopy
from pywps.validator.mode import MODE
from pywps.inout.literaltypes import AnyValue, NoValue, ValuesReference, AllowedValue


class BoundingBoxInput(basic.BBoxInput):

    """
    :param string identifier: The name of this input.
    :param string title: Human readable title
    :param string abstract: Longer text description
    :param crss: List of supported coordinate reference
                 system (e.g. ['EPSG:4326'])
    :param list keywords: Keywords that characterize this input.
    :param int dimensions: 2 or 3
    :param str workdir: working directory, to save temporary file objects in.
    :param list metadata: TODO
    :param int min_occurs: how many times this input occurs
    :param int max_occurs: how many times this input occurs
    :param metadata: List of metadata advertised by this process. They
                     should be :class:`pywps.app.Common.Metadata` objects.
    """

    def __init__(self, identifier, title, crss=None, abstract='', keywords=[],
                 dimensions=2, workdir=None, metadata=[], min_occurs=1,
                 max_occurs=1,
                 mode=MODE.NONE,
                 default=None, default_type=basic.SOURCE_TYPE.DATA):

        basic.BBoxInput.__init__(self, identifier, title=title, crss=crss,
                                 abstract=abstract, keywords=keywords,
                                 dimensions=dimensions, workdir=workdir, metadata=metadata,
                                 min_occurs=min_occurs, max_occurs=max_occurs,
                                 mode=mode, default=default,
                                 default_type=default_type)

        self.as_reference = False

    @property
    def json(self):
        """Get JSON representation of the input
        """
        return {
            'identifier': self.identifier,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'type': 'bbox',
            'crs': self.crs,
            'crss': self.crss,
            'metadata': self.metadata,
            'bbox': (self.ll, self.ur),
            'dimensions': self.dimensions,
            'workdir': self.workdir,
            'mode': self.valid_mode,
            'min_occurs': self.min_occurs,
            'max_occurs': self.max_occurs
        }

    @classmethod
    def from_json(cls, json_input):
        instance = cls(
            identifier=json_input['identifier'],
            title=json_input['title'],
            abstract=json_input['abstract'],
            crss=json_input['crss'],
            keywords=json_input['keywords'],
            metadata=json_input['metadata'],
            dimensions=json_input['dimensions'],
            workdir=json_input['workdir'],
            mode=json_input['mode'],
            min_occurs=json_input['min_occurs'],
            max_occurs=json_input['max_occurs'],
        )
        instance.ll = json_input['bbox'][0]
        instance.ur = json_input['bbox'][1]

        return instance

    def clone(self):
        """Create copy of yourself
        """
        return deepcopy(self)


class ComplexInput(basic.ComplexInput):
    """
    Complex data input

    :param str identifier: The name of this input.
    :param str title: Title of the input
    :param pywps.inout.formats.Format supported_formats: List of supported
                                                          formats
    :param pywps.inout.formats.Format data_format: default data format
    :param str abstract: Input abstract
    :param list keywords: Keywords that characterize this input.
    :param str workdir: working directory, to save temporary file objects in.
    :param list metadata: TODO
    :param int min_occurs: minimum occurrence
    :param int max_occurs: maximum occurrence
    :param pywps.validator.mode.MODE mode: validation mode (none to strict)
    """

    def __init__(self, identifier, title, supported_formats,
                 data_format=None, abstract='', keywords=[], workdir=None, metadata=[], min_occurs=1,
                 max_occurs=1, mode=MODE.NONE,
                 default=None, default_type=basic.SOURCE_TYPE.DATA):
        """constructor"""

        basic.ComplexInput.__init__(self, identifier, title=title,
                                    supported_formats=supported_formats,
                                    data_format=data_format, abstract=abstract,
                                    keywords=keywords, workdir=workdir, metadata=metadata,
                                    min_occurs=min_occurs,
                                    max_occurs=max_occurs, mode=mode,
                                    default=default, default_type=default_type)

        self.as_reference = False
        self.method = ''

    @property
    def json(self):
        """Get JSON representation of the input
        """
        data = {
            'identifier': self.identifier,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'metadata': self.metadata,
            'type': 'complex',
            'data_format': self.data_format.json,
            'asreference': self.as_reference,
            'supported_formats': [frmt.json for frmt in self.supported_formats],
            'workdir': self.workdir,
            'mode': self.valid_mode,
            'min_occurs': self.min_occurs,
            'max_occurs': self.max_occurs
        }

        if self.prop == 'file':
            data['file'] = self.file
        elif self.prop == 'url':
            data["href"] = self.url
        elif self.prop == 'data':
            data = self._json_data(data)
        elif self.prop == 'stream':
            # we store the stream in the data property
            data = self._json_data(data)

        if self.data_format:
            if self.data_format.mime_type:
                data['mimetype'] = self.data_format.mime_type
            if self.data_format.encoding:
                data['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                data['schema'] = self.data_format.schema

        return data

    @classmethod
    def from_json(cls, json_input):
        instance = cls(
            identifier=json_input['identifier'],
            title=json_input.get('title'),
            abstract=json_input.get('abstract'),
            keywords=json_input.get('keywords', []),
            workdir=json_input.get('workdir'),
            metadata=json_input.get('metadata', []),
            data_format=Format(
                schema=json_input['data_format'].get('schema'),
                extension=json_input['data_format'].get('extension'),
                mime_type=json_input['data_format']['mime_type'],
                encoding=json_input['data_format'].get('encoding')
            ),
            supported_formats=[
                Format(
                    schema=infrmt.get('schema'),
                    extension=infrmt.get('extension'),
                    mime_type=infrmt['mime_type'],
                    encoding=infrmt.get('encoding')
                ) for infrmt in json_input['supported_formats']
            ],
            mode=json_input.get('mode', MODE.NONE)
        )
        instance.as_reference = json_input.get('asreference', False)
        if json_input.get('file'):
            instance.file = json_input['file']
        elif json_input.get('href'):
            instance.url = json_input['href']
        elif json_input.get('data'):
            instance.data = json_input['data']

        return instance

    def _json_data(self, data):
        """Return Data node
        """

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

    def clone(self):
        """Create copy of yourself
        """
        return deepcopy(self)


class LiteralInput(basic.LiteralInput):
    """
    :param str identifier: The name of this input.
    :param str title: Title of the input
    :param pywps.inout.literaltypes.LITERAL_DATA_TYPES data_type: data type
    :param str workdir: working directory, to save temporary file objects in.
    :param str abstract: Input abstract
    :param list keywords: Keywords that characterize this input.
    :param list metadata: TODO
    :param str uoms: units
    :param int min_occurs: minimum occurence
    :param int max_occurs: maximum occurence
    :param pywps.validator.mode.MODE mode: validation mode (none to strict)
    :param pywps.inout.literaltypes.AnyValue allowed_values: or :py:class:`pywps.inout.literaltypes.AllowedValue` object
    :param metadata: List of metadata advertised by this process. They
                     should be :class:`pywps.app.Common.Metadata` objects.
    """

    def __init__(self, identifier, title=None, data_type='integer', workdir=None, abstract='', keywords=[],
                 metadata=[], uoms=None,
                 min_occurs=1, max_occurs=1,
                 mode=MODE.SIMPLE, allowed_values=AnyValue,
                 default=None, default_type=basic.SOURCE_TYPE.DATA):

        """Constructor
        """

        basic.LiteralInput.__init__(self, identifier, title=title,
                                    data_type=data_type, workdir=workdir, abstract=abstract,
                                    keywords=keywords, metadata=metadata,
                                    uoms=uoms, min_occurs=min_occurs,
                                    max_occurs=max_occurs, mode=mode,
                                    allowed_values=allowed_values,
                                    default=default, default_type=default_type)

        self.as_reference = False

    @property
    def json(self):
        """Get JSON representation of the input
        """
        data = {
            'identifier': self.identifier,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'metadata': self.metadata,
            'type': 'literal',
            'data_type': self.data_type,
            'workdir': self.workdir,
            'allowed_values': [value.json for value in self.allowed_values],
            'mode': self.valid_mode,
            'min_occurs': self.min_occurs,
            'max_occurs': self.max_occurs,

            # other values not set in the constructor
            'data': self.data,
        }
        if self.uoms:
            data["uoms"] = [uom.json for uom in self.uoms]
        if self.uom:
            data["uom"] = self.uom.json
        return data

    @classmethod
    def from_json(cls, json_input):

        allowed_values = []
        for allowed_value in json_input['allowed_values']:
            if allowed_value['type'] == 'anyvalue':
                allowed_values.append(AnyValue())
            elif allowed_value['type'] == 'novalue':
                allowed_values.append(NoValue())
            elif allowed_value['type'] == 'valuesreference':
                allowed_values.append(ValuesReference())
            elif allowed_value['type'] == 'allowedvalue':
                allowed_values.append(AllowedValue(
                    allowed_type=allowed_value['allowed_type'],
                    value=allowed_value['value'],
                    minval=allowed_value['minval'],
                    maxval=allowed_value['maxval'],
                    spacing=allowed_value['spacing'],
                    range_closure=allowed_value['range_closure']
                ))

        json_input['allowed_values'] = allowed_values
        json_input['uoms'] = [basic.UOM(uom.get('uom')) for uom in json_input.get('uoms', [])]

        data = json_input.pop('data', None)
        uom = json_input.pop('uom', None)
        json_input.pop('type')

        instance = cls(**json_input)

        instance.data = data
        if uom:
            instance.uom = basic.UOM(uom['uom'])

        return instance

    def clone(self):
        """Create copy of yourself
        """
        return deepcopy(self)


def input_from_json(json_data):
    if json_data['type'] == 'complex':
        inpt = ComplexInput.from_json(json_data)
    elif json_data['type'] == 'literal':
        inpt = LiteralInput.from_json(json_data)
    elif json_data['type'] == 'bbox':
        inpt = BoundingBoxInput.from_json(json_data)
    else:
        raise InvalidParameterValue("Input type not recognized: {}".format(json_data['type']))

    return inpt
