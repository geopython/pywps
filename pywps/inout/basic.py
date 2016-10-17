##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


from pywps._compat import text_type, StringIO
import os
import tempfile
from pywps.inout.literaltypes import (LITERAL_DATA_TYPES, convert,
                                      make_allowedvalues, is_anyvalue)
from pywps import OWS, OGCUNIT, NAMESPACES
from pywps.validator.mode import MODE
from pywps.validator.base import emptyvalidator
from pywps.validator import get_validator
from pywps.validator.literalvalidator import (validate_anyvalue,
                                              validate_allowed_values)
from pywps.exceptions import InvalidParameterValue
import base64
from collections import namedtuple

_SOURCE_TYPE = namedtuple('SOURCE_TYPE', 'MEMORY, FILE, STREAM, DATA')
SOURCE_TYPE = _SOURCE_TYPE(0, 1, 2, 3)


class IOHandler(object):
    """Basic IO class. Provides functions, to accept input data in file,
    memory object and stream object and give them out in all three types

    >>> # setting up
    >>> import os
    >>> from io import RawIOBase
    >>> from io import FileIO
    >>> import types
    >>>
    >>> ioh_file = IOHandler(workdir=tmp)
    >>> assert isinstance(ioh_file, IOHandler)
    >>>
    >>> # Create test file input
    >>> fileobj = open(os.path.join(tmp, 'myfile.txt'), 'w')
    >>> fileobj.write('ASDF ASFADSF ASF ASF ASDF ASFASF')
    >>> fileobj.close()
    >>>
    >>> # testing file object on input
    >>> ioh_file.file = fileobj.name
    >>> assert ioh_file.source_type == SOURCE_TYPE.FILE
    >>> file = ioh_file.file
    >>> stream = ioh_file.stream
    >>>
    >>> assert file == fileobj.name
    >>> assert isinstance(stream, RawIOBase)
    >>> # skipped assert isinstance(ioh_file.memory_object, POSH)
    >>>
    >>> # testing stream object on input
    >>> ioh_stream = IOHandler(workdir=tmp)
    >>> assert ioh_stream.workdir == tmp
    >>> ioh_stream.stream = FileIO(fileobj.name,'r')
    >>> assert ioh_stream.source_type == SOURCE_TYPE.STREAM
    >>> file = ioh_stream.file
    >>> stream = ioh_stream.stream
    >>>
    >>> assert open(file).read() == ioh_file.stream.read()
    >>> assert isinstance(stream, RawIOBase)
    >>> # skipped assert isinstance(ioh_stream.memory_object, POSH)
    >>>
    >>> # testing in memory object object on input
    >>> # skipped ioh_mo = IOHandler(workdir=tmp)
    >>> # skipped ioh_mo.memory_object = POSH
    >>> # skipped assert ioh_mo.source_type == SOURCE_TYPE.MEMORY
    >>> # skipped file = ioh_mo.file
    >>> # skipped stream = ioh_mo.stream
    >>> # skipped posh = ioh_mo.memory_object
    >>> #
    >>> # skipped assert open(file).read() == ioh_file.stream.read()
    >>> # skipped assert isinstance(ioh_mo.stream, RawIOBase)
    >>> # skipped assert isinstance(ioh_mo.memory_object, POSH)
    """

    def __init__(self, workdir=None, mode=MODE.NONE):
        self.source_type = None
        self.source = None
        self._tempfile = None
        self.workdir = workdir
        self._stream = None

        self.valid_mode = mode

    def _check_valid(self):
        """Validate this input usig given validator
        """

        validate = self.validator
        _valid = validate(self, self.valid_mode)
        if not _valid:
            raise InvalidParameterValue('Input data not valid using '
                                        'mode %s' % (self.valid_mode))

    def set_file(self, filename):
        """Set source as file name"""
        self.source_type = SOURCE_TYPE.FILE
        self.source = os.path.abspath(filename)
        self._check_valid()

    def set_workdir(self, workdirpath):
        """Set working temporary directory for files to be stored in"""

        if workdirpath is not None and not os.path.exists(workdirpath):
            os.makedirs(workdirpath)

        self._workdir = workdirpath

    def set_memory_object(self, memory_object):
        """Set source as in memory object"""
        self.source_type = SOURCE_TYPE.MEMORY
        self._check_valid()

    def set_stream(self, stream):
        """Set source as stream object"""
        self.source_type = SOURCE_TYPE.STREAM
        self.source = stream
        self._check_valid()

    def set_data(self, data):
        """Set source as simple datatype e.g. string, number"""
        self.source_type = SOURCE_TYPE.DATA
        self.source = data
        self._check_valid()

    def set_base64(self, data):
        """Set data encoded in base64"""

        self.data = base64.b64decode(data)
        self._check_valid()

    def get_file(self):
        """Get source as file name"""
        if self.source_type == SOURCE_TYPE.FILE:
            return self.source

        elif self.source_type == SOURCE_TYPE.STREAM or self.source_type == SOURCE_TYPE.DATA:
            if self._tempfile:
                return self._tempfile
            else:
                (opening, stream_file_name) = tempfile.mkstemp(dir=self.workdir)
                stream_file = open(stream_file_name, 'w')

                if self.source_type == SOURCE_TYPE.STREAM:
                    stream_file.write(self.source.read())
                else:
                    stream_file.write(self.source)

                stream_file.close()
                self._tempfile = str(stream_file_name)
                return self._tempfile

    def get_workdir(self):
        """Return working directory name
        """
        return self._workdir

    def get_memory_object(self):
        """Get source as memory object"""
        # TODO: Soeren promissed to implement at WPS Workshop on 23rd of January 2014
        raise NotImplementedError("setmemory_object not implemented")

    def get_stream(self):
        """Get source as stream object"""
        if self.source_type == SOURCE_TYPE.FILE:
            if self._stream and not self._stream.closed:
                self._stream.close()
            from io import FileIO
            self._stream = FileIO(self.source, mode='r', closefd=True)
            return self._stream
        elif self.source_type == SOURCE_TYPE.STREAM:
            return self.source
        elif self.source_type == SOURCE_TYPE.DATA:
            return StringIO(text_type(self.source))

    def get_data(self):
        """Get source as simple data object"""
        if self.source_type == SOURCE_TYPE.FILE:
            file_handler = open(self.source, mode='r')
            content = file_handler.read()
            file_handler.close()
            return content
        elif self.source_type == SOURCE_TYPE.STREAM:
            return self.source.read()
        elif self.source_type == SOURCE_TYPE.DATA:
            return self.source

    @property
    def validator(self):
        """Return the function suitable for validation
        This method should be overridden by class children

        :return: validating function
        """

        return emptyvalidator

    def get_base64(self):
        return base64.b64encode(self.data)

    # Properties
    file = property(fget=get_file, fset=set_file)
    memory_object = property(fget=get_memory_object, fset=set_memory_object)
    stream = property(fget=get_stream, fset=set_stream)
    data = property(fget=get_data, fset=set_data)
    base64 = property(fget=get_base64, fset=set_base64)
    workdir = property(fget=get_workdir, fset=set_workdir)


class SimpleHandler(IOHandler):
    """Data handler for Literal In- and Outputs

    >>> class Int_type(object):
    ...     @staticmethod
    ...     def convert(value): return int(value)
    >>>
    >>> class MyValidator(object):
    ...     @staticmethod
    ...     def validate(inpt): return 0 < inpt.data < 3
    >>>
    >>> inpt = SimpleHandler(data_type = Int_type)
    >>> inpt.validator = MyValidator
    >>>
    >>> inpt.data = 1
    >>> inpt.validator.validate(inpt)
    True
    >>> inpt.data = 5
    >>> inpt.validator.validate(inpt)
    False
    """

    def __init__(self, workdir=None, data_type=None, mode=MODE.NONE):
        IOHandler.__init__(self, workdir=workdir, mode=mode)
        self.data_type = data_type

    def get_data(self):
        return IOHandler.get_data(self)

    def set_data(self, data):
        """Set data value. input data are converted into target format
        """

        if self.data_type:
            data = convert(self.data_type, data)

        IOHandler.set_data(self, data)

    data = property(fget=get_data, fset=set_data)


class BasicIO:
    """Basic Input or Ouput class
    """
    def __init__(self, identifier, title=None, abstract=None):
        self.identifier = identifier
        self.title = title
        self.abstract = abstract


class BasicLiteral:
    """Basic literal input/output class
    """

    def __init__(self, data_type="integer", uoms=None):
        assert data_type in LITERAL_DATA_TYPES
        self.data_type = data_type
        # list of uoms
        self.uoms = []
        # current uom
        self._uom = None

        # add all uoms (upcasting to UOM)
        if uoms is not None:
            for uom in uoms:
                if not isinstance(uom, UOM):
                    uom = UOM(uom)
                self.uoms.append(uom)

        if self.uoms:
            # default/current uom
            self.uom = self.uoms[0]

    @property
    def uom(self):
        return self._uom

    @uom.setter
    def uom(self, uom):
        self._uom = uom


class BasicComplex(object):
    """Basic complex input/output class

    """

    def __init__(self, data_format=None, supported_formats=None):
        self._data_format = None
        self._supported_formats = None
        if supported_formats:
            self.supported_formats = supported_formats
        if self.supported_formats:
            # not an empty list, set the default/current format to the first
            self.data_format = supported_formats[0]

    def get_format(self, mime_type):
        """
        :param mime_type: given mimetype
        :return: Format
        """

        for frmt in self.supported_formats:
            if frmt.mime_type == mime_type:
                return frmt
        else:
            return None

    @property
    def validator(self):
        """Return the proper validator for given data_format
        """

        return self.data_format.validate

    @property
    def supported_formats(self):
        return self._supported_formats

    @supported_formats.setter
    def supported_formats(self, supported_formats):
        """Setter of supported formats
        """

        def set_format_validator(supported_format):
            if not supported_format.validate or \
               supported_format.validate == emptyvalidator:
                supported_format.validate =\
                    get_validator(supported_format.mime_type)
            return supported_format

        self._supported_formats = list(map(set_format_validator, supported_formats))

    @property
    def data_format(self):
        return self._data_format

    @data_format.setter
    def data_format(self, data_format):
        """self data_format setter
        """
        if self._is_supported(data_format):
            self._data_format = data_format
            if not data_format.validate or data_format.validate == emptyvalidator:
                data_format.validate = get_validator(data_format.mime_type)
        else:
            raise InvalidParameterValue("Requested format "
                                        "%s, %s, %s not supported" %
                                        (data_format.mime_type,
                                         data_format.encoding,
                                         data_format.schema),
                                        'mimeType')

    def _is_supported(self, data_format):

        if self.supported_formats:
            for frmt in self.supported_formats:
                if frmt.same_as(data_format):
                    return True

        return False


class BasicBoundingBox(object):
    """Basic BoundingBox input/output class
    """

    def __init__(self, crss=None, dimensions=2):
        self.crss = crss or ['epsg:4326']
        self.crs = self.crss[0]
        self.dimensions = dimensions
        self.ll = []
        self.ur = []


class LiteralInput(BasicIO, BasicLiteral, SimpleHandler):
    """LiteralInput input abstract class
    """

    def __init__(self, identifier, title=None, abstract=None,
                 data_type="integer", workdir=None, allowed_values=None,
                 uoms=None, mode=MODE.NONE):
        BasicIO.__init__(self, identifier, title, abstract)
        BasicLiteral.__init__(self, data_type, uoms)
        SimpleHandler.__init__(self, workdir, data_type, mode=mode)

        self.any_value = is_anyvalue(allowed_values)
        self.allowed_values = []
        if not self.any_value:
            self.allowed_values = make_allowedvalues(allowed_values)

    @property
    def validator(self):
        """Get validator for any value as well as allowed_values
        :rtype: function
        """

        if self.any_value:
            return validate_anyvalue
        else:
            return validate_allowed_values

    @property
    def json(self):
        """Get JSON representation of the input
        """
        return {
            'identifier': self.identifier,
            'title': self.title,
            'abstract': self.abstract,
            'type': 'literal',
            'data_type': self.data_type,
            'workdir': self.workdir,
            'allowed_values': [value.json for value in self.allowed_values],
            'uoms': self.uoms,
            'uom': self.uom,
            'mode': self.valid_mode,
            'data': self.data
        }


class LiteralOutput(BasicIO, BasicLiteral, SimpleHandler):
    """Basic LiteralOutput class
    """

    def __init__(self, identifier, title=None, abstract=None,
                 data_type=None, workdir=None, uoms=None, validate=None,
                 mode=MODE.NONE):
        BasicIO.__init__(self, identifier, title, abstract)
        BasicLiteral.__init__(self, data_type, uoms)
        SimpleHandler.__init__(self, workdir=None, data_type=data_type,
                               mode=mode)

        self._storage = None

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, storage):
        self._storage = storage

    @property
    def validator(self):
        """Get validator for any value as well as allowed_values
        """

        return validate_anyvalue


class BBoxInput(BasicIO, BasicBoundingBox, IOHandler):
    """Basic Bounding box input abstract class
    """

    def __init__(self, identifier, title=None, abstract=None, crss=None,
                 dimensions=None, workdir=None, mode=MODE.NONE):
        BasicIO.__init__(self, identifier, title, abstract)
        BasicBoundingBox.__init__(self, crss, dimensions)
        IOHandler.__init__(self, workdir=None, mode=mode)

    @property
    def json(self):
        """Get JSON representation of the input. It returns following keys in
        the JSON object:

            * identifier
            * title
            * abstract
            * type
            * crs
            * bbox
            * dimensions
            * workdir
            * mode
        """
        return {
            'identifier': self.identifier,
            'title': self.title,
            'abstract': self.abstract,
            'type': 'bbox',
            'crs': self.crss,
            'bbox': (self.ll, self.ur),
            'dimensions': self.dimensions,
            'workdir': self.workdir,
            'mode': self.valid_mode
        }


class BBoxOutput(BasicIO, BasicBoundingBox, SimpleHandler):
    """Basic BoundingBox output class
    """

    def __init__(self, identifier, title=None, abstract=None, crss=None,
                 dimensions=None, workdir=None, mode=MODE.NONE):
        BasicIO.__init__(self, identifier, title, abstract)
        BasicBoundingBox.__init__(self, crss, dimensions)
        SimpleHandler.__init__(self, workdir=None, mode=mode)
        self._storage = None

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, storage):
        self._storage = storage


class ComplexInput(BasicIO, BasicComplex, IOHandler):
    """Complex input abstract class

    >>> ci = ComplexInput()
    >>> ci.validator = 1
    >>> ci.validator
    1
    """

    def __init__(self, identifier, title=None, abstract=None,
                 workdir=None, data_format=None, supported_formats=None,
                 mode=MODE.NONE):
        BasicIO.__init__(self, identifier, title, abstract)
        IOHandler.__init__(self, workdir=workdir, mode=mode)
        BasicComplex.__init__(self, data_format, supported_formats)

    @property
    def json(self):
        """Get JSON representation of the input
        """
        return {
            'identifier': self.identifier,
            'title': self.title,
            'abstract': self.abstract,
            'type': 'complex',
            'data_format': self.data_format.json,
            'supported_formats': [frmt.json for frmt in self.supported_formats],
            'file': self.file,
            'workdir': self.workdir,
            'mode': self.valid_mode
        }


class ComplexOutput(BasicIO, BasicComplex, IOHandler):
    """Complex output abstract class

    >>> # temporary configuration
    >>> import ConfigParser
    >>> from pywps.storage import *
    >>> config = ConfigParser.RawConfigParser()
    >>> config.add_section('FileStorage')
    >>> config.set('FileStorage', 'target', './')
    >>> config.add_section('server')
    >>> config.set('server', 'outputurl', 'http://foo/bar/filestorage')
    >>>
    >>> # create temporary file
    >>> tiff_file = open('file.tiff', 'w')
    >>> tiff_file.write("AA")
    >>> tiff_file.close()
    >>>
    >>> co = ComplexOutput()
    >>> co.set_file('file.tiff')
    >>> fs = FileStorage(config)
    >>> co.storage = fs
    >>>
    >>> url = co.get_url() # get url, data are stored
    >>>
    >>> co.get_stream().read() # get data - nothing is stored
    'AA'
    """

    def __init__(self, identifier, title=None, abstract=None,
                 workdir=None, data_format=None, supported_formats=None,
                 mode=MODE.NONE):
        BasicIO.__init__(self, identifier, title, abstract)
        IOHandler.__init__(self, workdir=workdir, mode=mode)
        BasicComplex.__init__(self, data_format, supported_formats)

        self._storage = None

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, storage):
        self._storage = storage

    def get_url(self):
        """Return URL pointing to data
        """
        (outtype, storage, url) = self.storage.store(self)
        return url


class UOM(object):
    """
    :param uom: unit of measure
    """

    def __init__(self, uom=''):
        self.uom = uom

    def describe_xml(self):
        elem = OWS.UOM(
            self.uom
        )

        elem.attrib['{%s}reference' % NAMESPACES['ows']] = OGCUNIT[self.uom]

        return elem

    def execute_attribute(self):
        return OGCUNIT[self.uom]


if __name__ == "__main__":
    import doctest
    from pywps.wpsserver import temp_dir

    with temp_dir() as tmp:
        os.chdir(tmp)
        doctest.testmod()
