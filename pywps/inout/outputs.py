from pywps import configuration
from pywps._compat import text_type
from pywps import E, WPS, OWS, OGCTYPE, NAMESPACES
from pywps.inout import basic
from pywps.inout.storage import FileStorage
from pywps.inout.formats import Format


class LiteralOutput(basic.LiteralOutput):
    """
    :param identifier: The name of this output.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    :param value: Resulting value
            Should be :class:`~String` object.
    """

    def __init__(self, identifier, title, data_type='string', abstract='',
            metadata=[], uoms=[]):
        basic.LiteralOutput.__init__(self, identifier, title=title, data_type=data_type, uoms=uoms)
        self.abstract = abstract
        self.metadata = metadata

    def describe_xml(self):
        doc = E.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata(m))

        literal_data_doc = E.LiteralOutput()

        if self.data_type:
            data_type = OWS.DataType(self.data_type)
            data_type.attrib['{%s}reference' % NAMESPACES['ows']] = OGCTYPE[self.data_type]
            literal_data_doc.append(data_type)

        if self.uoms:
            default_uom_element = self.uom.describe_xml()
            supported_uom_elements = [u.describe_xml() for u in self.uoms]

            literal_data_doc.append(
                E.UOMs(
                    E.Default(default_uom_element),
                    E.Supported(*supported_uom_elements)
                )
            )

        doc.append(literal_data_doc)

        return doc

    def execute_xml(self):
        doc = WPS.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        data_doc = WPS.Data()

        literal_data_doc = WPS.LiteralData(text_type(self.data))
        literal_data_doc.attrib['dataType'] = OGCTYPE[self.data_type]
        if self.uom:
            literal_data_doc.attrib['uom'] = self.uom.execute_attribute()
        data_doc.append(literal_data_doc)

        doc.append(data_doc)

        return doc


class ComplexOutput(basic.ComplexOutput):
    """
    :param identifier: The name of this output.
    :param formats: Possible output formats for this output.
            Should be list of :class:`~Format` object.
    :param output_format: Required format for this output.
            Should be :class:`~Format` object.
    :param encoding: The encoding of this input or requested for this output
            (e.g., UTF-8).
    """

    def __init__(self, identifier, title,  output_format,
                 abstract='', supported_formats=None, metadata=[]):

        basic.ComplexOutput.__init__(self, identifier, title=title, abstract=abstract)
        self.metadata = metadata

        self._output_format = None

        self.as_reference = False
        if type(output_format) == type([]):
            self.output_format = output_format[0]
            supported_formats = output_format
        else:
            self.output_format = output_format
        self.storage = None
        if not supported_formats:
            supported_formats = []
        self.supported_formats = [self.output_format]
        self.supported_formats.extend(supported_formats)

    @property
    def output_format(self):
        """Get output format
        :rtype: String
        """

        if self._output_format:
            return self._output_format
        else:
            return ''

    @output_format.setter
    def output_format(self, output_format):
        """Set output format
        """
        self._output_format = output_format


    def describe_xml(self):
        """Generate DescribeProcess element
        """
        default_format_el = self.output_format.describe_xml()
        supported_format_elements = [f.describe_xml() for f in self.supported_formats]

        doc = E.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        for m in self.metadata:
            doc.append(OWS.Metadata(*self.metadata))

        doc.append(
            E.ComplexOutput(
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

        doc = WPS.Output(
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

        # get_url will create the file and return the url for it
        self.storage = FileStorage(configuration)
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.get_url()

        if self.data_format:
            if self.data_format.mime_type:
                doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                doc.attrib['schema'] = self.data_format.schema
        return doc

    def _execute_xml_data(self):
        """Return Data node
        """
        doc = WPS.Data()

        if self.data is None:
            complex_doc = WPS.ComplexData()
        else:
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


class BoundingBoxOutput(basic.BBoxInput):
    """
    :param identifier: The name of this input.
    """

    def __init__(self, identifier, title, crss, abstract='',
                 dimensions=2, metadata=[], min_occurs='1',
                 max_occurs='1', as_reference=False):
        basic.BBoxInput.__init__(self, identifier, title=title,
                                 abstract=abstract, crss=crss,
                                 dimensions=dimensions)

        self.metadata = metadata
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.as_reference = as_reference

    def describe_xml(self):
        doc = E.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        if self.metadata:
            doc.append(OWS.Metadata(*self.metadata))

        bbox_data_doc = E.BoundingBoxOutput()
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
        doc = E.Output(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        bbox_data_doc = OWS.BoundingBox()

        bbox_data_doc.attrib['crs'] = self.crs
        bbox_data_doc.attrib['dimensions'] = str(self.dimensions)

        bbox_data_doc.append(OWS.LowerCorner('{0[0]} {0[1]}'.format(self.data)))
        bbox_data_doc.append(OWS.UpperCorner('{0[2]} {0[3]}'.format(self.data)))

        doc.append(bbox_data_doc)

        return doc
