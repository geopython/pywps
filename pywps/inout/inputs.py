##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


from pywps import configuration, E, OWS, WPS, OGCTYPE, NAMESPACES
from pywps.inout import basic
from copy import deepcopy
from pywps.validator.mode import MODE
from pywps.inout.literaltypes import AnyValue


class BoundingBoxInput(basic.BBoxInput):

    """
    :param string identifier: The name of this input.
    :param string title: Human readable title
    :param string abstract: Longer text description
    :param crss: List of supported coordinate reference system (e.g. ['EPSG:4326'])
    :param int dimensions: 2 or 3
    :param int min_occurs: how many times this input occurs
    :param int max_occurs: how many times this input occurs
    :param metadata: List of metadata advertised by this process. They
                     should be :class:`pywps.app.Common.Metadata` objects.
    """

    def __init__(self, identifier, title, crss, abstract='',
                 dimensions=2, metadata=[], min_occurs=1,
                 max_occurs=1,
                 mode=MODE.NONE):
        basic.BBoxInput.__init__(self, identifier, title=title,
                                 abstract=abstract, crss=crss,
                                 dimensions=dimensions, mode=mode)

        self.metadata = metadata
        self.min_occurs = int(min_occurs)
        self.max_occurs = int(max_occurs)
        self.as_reference = False

    def describe_xml(self):
        """
        :return: describeprocess response xml element
        """
        doc = E.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        doc.attrib['minOccurs'] = str(self.min_occurs)
        doc.attrib['maxOccurs'] = str(self.max_occurs)

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata(dict(m)))

        bbox_data_doc = E.BoundingBoxData()
        doc.append(bbox_data_doc)

        default_doc = E.Default()
        default_doc.append(E.CRS(self.crss[0]))

        supported_doc = E.Supported()
        for c in self.crss:
            supported_doc.append(E.CRS(c))

        bbox_data_doc.append(default_doc)
        bbox_data_doc.append(supported_doc)

        return doc

    def execute_xml(self):
        """
        :return: execute response element
        """
        doc = WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        bbox_data_doc = OWS.BoundingBox()

        bbox_data_doc.attrib['crs'] = self.crs
        bbox_data_doc.attrib['dimensions'] = str(self.dimensions)

        bbox_data_doc.append(
            OWS.LowerCorner('{0[0]} {0[1]}'.format(self.data)))
        bbox_data_doc.append(
            OWS.UpperCorner('{0[2]} {0[3]}'.format(self.data)))

        doc.append(bbox_data_doc)

        return doc

    def clone(self):
        """Create copy of yourself
        """
        return deepcopy(self)


class ComplexInput(basic.ComplexInput):
    """
    Complex data input

    :param str identifier: The name of this input.
    :param str title: Title of the input
    :param  pywps.inout.formats.Format supported_formats: List of supported formats
    :param pywps.inout.formats.Format data_format: default data format
    :param str abstract: Input abstract
    :param list metada: TODO
    :param int min_occurs: minimum occurence
    :param int max_occurs: maximum occurence
    :param pywps.validator.mode.MODE mode: validation mode (none to strict)
    """

    def __init__(self, identifier, title, supported_formats=None,
                 data_format=None, abstract='', metadata=[], min_occurs=1,
                 max_occurs=1, mode=MODE.NONE):
        """constructor"""

        basic.ComplexInput.__init__(self, identifier=identifier, title=title,
                                    abstract=abstract,
                                    supported_formats=supported_formats,
                                    mode=mode)
        self.metadata = metadata
        self.min_occurs = int(min_occurs)
        self.max_occurs = int(max_occurs)
        self.as_reference = False
        self.url = ''
        self.method = ''
        self.max_size = int(0)

    def calculate_max_input_size(self):
        """Calculates maximal size for input file based on configuration
        and units

        :return: maximum file size bytes
        """
        max_size = configuration.get_config_value(
            'server', 'maxsingleinputsize')
        self.max_size = configuration.get_size_mb(max_size)

    def describe_xml(self):
        """Return Describe process element
        """
        default_format_el = self.supported_formats[0].describe_xml()
        supported_format_elements = [f.describe_xml()
                                     for f in self.supported_formats]

        doc = E.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        doc.attrib['minOccurs'] = str(self.min_occurs)
        doc.attrib['maxOccurs'] = str(self.max_occurs)

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata(dict(m)))

        doc.append(
            E.ComplexData(
                E.Default(default_format_el),
                E.Supported(*supported_format_elements)
            )
        )

        return doc

    def execute_xml(self):
        """Render Execute response XML node


        :return: node
        :rtype: ElementMaker
        """
        node = None
        if self.as_reference:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        doc = WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        doc.append(node)

        return doc

    def _execute_xml_reference(self):
        """Return Reference node
        """
        doc = WPS.Reference()
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.url
        if self.data_format:
            if self.data_format.mime_type:
                doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                doc.attrib['schema'] = self.data_format.schema
        if self.method.upper() == 'POST' or self.method.upper() == 'GET':
            doc.attrib['method'] = self.method.upper()
        return doc

    def _execute_xml_data(self):
        """Return Data node
        """
        doc = WPS.Data()
        complex_doc = WPS.ComplexData(self.data)

        if self.data_format:
            if self.data_format.mime_type:
                complex_doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                complex_doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                complex_doc.attrib['schema'] = self.data_format.schema
        doc.append(complex_doc)
        return doc

    def clone(self):
        """Create copy of yourself
        """
        return deepcopy(self)


class LiteralInput(basic.LiteralInput):
    """
    :param str identifier: The name of this input.
    :param str title: Title of the input
    :param pywps.inout.literaltypes.LITERAL_DATA_TYPES data_type: data type
    :param str abstract: Input abstract
    :param list metadata: TODO
    :param str uoms: units
    :param int min_occurs: minimum occurence
    :param int max_occurs: maximum occurence
    :param pywps.validator.mode.MODE mode: validation mode (none to strict)
    :param pywps.inout.literaltypes.AnyValue allowed_values: or :py:class:`pywps.inout.literaltypes.AllowedValue` object
    :param metadata: List of metadata advertised by this process. They
                     should be :class:`pywps.app.Common.Metadata` objects.
    """

    def __init__(self, identifier, title, data_type='integer', abstract='',
                 metadata=[], uoms=None, default=None,
                 min_occurs=1, max_occurs=1,
                 mode=MODE.SIMPLE, allowed_values=AnyValue):
        """Constructor
        """

        basic.LiteralInput.__init__(self, identifier=identifier, title=title,
                                    abstract=abstract, data_type=data_type,
                                    uoms=uoms, mode=mode,
                                    allowed_values=allowed_values)
        self.metadata = metadata
        self.default = default
        self.min_occurs = int(min_occurs)
        self.max_occurs = int(max_occurs)
        self.as_reference = False

    def describe_xml(self):
        """Return DescribeProcess Output element
        """
        doc = E.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        doc.attrib['minOccurs'] = str(self.min_occurs)
        doc.attrib['maxOccurs'] = str(self.max_occurs)

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata(dict(m)))

        literal_data_doc = E.LiteralData()

        if self.data_type:
            data_type = OWS.DataType(self.data_type)
            data_type.attrib['{%s}reference' %
                             NAMESPACES['ows']] = OGCTYPE[self.data_type]
            literal_data_doc.append(data_type)

        if self.uoms:
            default_uom_element = self.uoms[0].describe_xml()
            supported_uom_elements = [u.describe_xml() for u in self.uoms]

            literal_data_doc.append(
                E.UOMs(
                    E.Default(default_uom_element),
                    E.Supported(*supported_uom_elements)
                )
            )

        doc.append(literal_data_doc)

        # TODO: refer to table 29 and 30
        if self.any_value:
            literal_data_doc.append(OWS.AnyValue())
        else:
            literal_data_doc.append(self._describe_xml_allowedvalues())

        if self.default:
            literal_data_doc.append(E.DefaultValue(self.default))

        return doc

    def execute_xml(self):
        """Render Execute response XML node

        :return: node
        :rtype: ElementMaker
        """
        node = None
        if self.as_reference:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        doc = WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        doc.append(node)

        return doc

    def _describe_xml_allowedvalues(self):
        """Return AllowedValues node
        """
        doc = OWS.AllowedValues()
        for value in self.allowed_values:
            doc.append(value.describe_xml())
        return doc

    def _execute_xml_reference(self):
        """Return Reference node
        """
        doc = WPS.Reference()
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.stream
        if self.method.upper() == 'POST' or self.method.upper() == 'GET':
            doc.attrib['method'] = self.method.upper()
        return doc

    def _execute_xml_data(self):
        """Return Data node
        """
        doc = WPS.Data()
        literal_doc = WPS.LiteralData(str(self.data))

        if self.data_type:
            literal_doc.attrib['dataType'] = self.data_type
        if self.uom:
            literal_doc.attrib['uom'] = self.uom
        doc.append(literal_doc)
        return doc

    def clone(self):
        """Create copy of yourself
        """
        return deepcopy(self)
