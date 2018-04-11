##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps import configuration
from pywps.inout import basic
from copy import deepcopy
from pywps.validator.mode import MODE
from pywps.inout.literaltypes import AnyValue


class BoundingBoxInput(basic.BBoxInput):

    """
    :param string identifier: The name of this input.
    :param string title: Human readable title
    :param string abstract: Longer text description
    :param crss: List of supported coordinate reference
                 system (e.g. ['EPSG:4326'])
    :param list keywords: Keywords that characterize this input.
    :param int dimensions: 2 or 3
    :param list metadata: TODO
    :param int min_occurs: how many times this input occurs
    :param int max_occurs: how many times this input occurs
    :param metadata: List of metadata advertised by this process. They
                     should be :class:`pywps.app.Common.Metadata` objects.
    """

    def __init__(self, identifier, title, crss, abstract='', keywords=[],
                 dimensions=2, metadata=[], min_occurs=1,
                 max_occurs=1,
                 mode=MODE.NONE,
                 default=None, default_type=basic.SOURCE_TYPE.DATA):

        basic.BBoxInput.__init__(self, identifier, title=title, crss=crss,
                                 abstract=abstract, keywords=keywords,
                                 dimensions=dimensions, metadata=metadata,
                                 min_occurs=min_occurs, max_occurs=max_occurs,
                                 mode=mode, default=default,
                                 default_type=default_type)

        self.as_reference = False

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
    :param list metadata: TODO
    :param int min_occurs: minimum occurrence
    :param int max_occurs: maximum occurrence
    :param pywps.validator.mode.MODE mode: validation mode (none to strict)
    """

    def __init__(self, identifier, title, supported_formats,
                 data_format=None, abstract='', keywords=[], metadata=[], min_occurs=1,
                 max_occurs=1, mode=MODE.NONE,
                 default=None, default_type=basic.SOURCE_TYPE.DATA):
        """constructor"""

        basic.ComplexInput.__init__(self, identifier, title=title,
                                    supported_formats=supported_formats,
                                    data_format=data_format, abstract=abstract,
                                    keywords=keywords, metadata=metadata,
                                    min_occurs=min_occurs,
                                    max_occurs=max_occurs, mode=mode,
                                    default=default, default_type=default_type)

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

    def __init__(self, identifier, title, data_type='integer', abstract='', keywords=[],
                 metadata=[], uoms=None,
                 min_occurs=1, max_occurs=1,
                 mode=MODE.SIMPLE, allowed_values=AnyValue,
                 default=None, default_type=basic.SOURCE_TYPE.DATA):

        """Constructor
        """

        basic.LiteralInput.__init__(self, identifier, title=title,
                                    data_type=data_type, abstract=abstract,
                                    keywords=keywords, metadata=metadata,
                                    uoms=uoms, min_occurs=min_occurs,
                                    max_occurs=max_occurs, mode=mode,
                                    allowed_values=allowed_values,
                                    default=default, default_type=default_type)

        self.as_reference = False

    def clone(self):
        """Create copy of yourself
        """
        return deepcopy(self)
