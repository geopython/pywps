# -*- coding: utf-8 -*-

"""Unit tests for IOs
"""
##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from __future__ import absolute_import
import requests
import os
import tempfile
import datetime
import unittest
import json
from pywps import inout
import base64

from pywps import Format, FORMATS
from pywps.app.Common import Metadata
from pywps.validator import get_validator
from pywps.inout.basic import IOHandler, SOURCE_TYPE, SimpleHandler, BBoxInput, BBoxOutput, \
    ComplexInput, ComplexOutput, LiteralOutput, LiteralInput, _is_textfile
from pywps.inout.literaltypes import convert, AllowedValue, AnyValue
from pywps.inout.outputs import MetaFile, MetaLink, MetaLink4
from pywps._compat import StringIO, text_type, urlparse
from pywps.validator.base import emptyvalidator
from pywps.exceptions import InvalidParameterValue
from pywps.validator.mode import MODE
from pywps.inout.basic import UOM
from pywps._compat import PY2
from pywps.inout.storage.file import FileStorageBuilder
from pywps.tests import service_ok
from pywps.translations import get_translation

from lxml import etree

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def get_data_format(mime_type):
    return Format(mime_type=mime_type, validate=get_validator(mime_type))


class IOHandlerTest(unittest.TestCase):
    """IOHandler test cases"""

    def setUp(self):
        tmp_dir = tempfile.mkdtemp()
        self.iohandler = IOHandler(workdir=tmp_dir)
        self._value = 'lalala'

    def tearDown(self):
        pass

    def test_basic_IOHandler(self):
        """Test basic IOHandler"""
        self.assertTrue(os.path.isdir(self.iohandler.workdir))

    def test_validator(self):
        """Test available validation function
        """
        self.assertEqual(self.iohandler.validator, emptyvalidator)

    def _test_outout(self, source_type, suffix=''):
        """Test all outputs"""

        self.assertEqual(source_type, self.iohandler.source_type,
                         'Source type properly set')

        self.assertEqual(self._value, self.iohandler.data, 'Data obtained')

        if self.iohandler.source_type == SOURCE_TYPE.URL:
            self.assertEqual('http', urlparse(self.iohandler.url).scheme)
        else:
            self.assertEqual('file', urlparse(self.iohandler.url).scheme)

        if self.iohandler.source_type == SOURCE_TYPE.STREAM:
            source = StringIO(text_type(self._value))
            self.iohandler.stream = source

        file_path = self.iohandler.file
        self.assertTrue(file_path.endswith(suffix))
        file_handler = open(file_path)
        self.assertEqual(self._value, file_handler.read(), 'File obtained')
        file_handler.close()

        if self.iohandler.source_type == SOURCE_TYPE.STREAM:
            source = StringIO(text_type(self._value))
            self.iohandler.stream = source

        stream_val = self.iohandler.stream.read()
        self.iohandler.stream.close()

        if PY2 and isinstance(stream_val, str):
            self.assertEqual(self._value, stream_val.decode('utf-8'),
                             'Stream obtained')
        elif not PY2 and isinstance(stream_val, bytes):
            self.assertEqual(self._value, stream_val.decode('utf-8'),
                             'Stream obtained')
        else:
            self.assertEqual(self._value, stream_val,
                             'Stream obtained')

        if self.iohandler.source_type == SOURCE_TYPE.STREAM:
            source = StringIO(text_type(self._value))
            self.iohandler.stream = source

        # self.assertEqual(stream_val, self.iohandler.memory_object,
        #                 'Memory object obtained')

    def test_data(self):
        """Test data input IOHandler"""
        if PY2:
            self.skipTest('fails on python 2.7')
        self.iohandler.data = self._value
        self.iohandler.data_format = Format('foo', extension='.foo')
        self._test_outout(SOURCE_TYPE.DATA, '.foo')

    def test_stream(self):
        """Test stream input IOHandler"""
        source = StringIO(text_type(self._value))
        self.iohandler.stream = source
        self._test_outout(SOURCE_TYPE.STREAM)

    def test_file(self):
        """Test file input IOHandler"""
        (fd, tmp_file) = tempfile.mkstemp()
        source = tmp_file
        file_handler = open(tmp_file, 'w')
        file_handler.write(self._value)
        file_handler.close()
        self.iohandler.file = source
        self._test_outout(SOURCE_TYPE.FILE)
        with self.assertRaises(TypeError):
            self.iohandler[0].data = '5'

    def test_url(self):
        if not service_ok('https://demo.mapserver.org'):
            self.skipTest("mapserver is unreachable")
        wfsResource = 'http://demo.mapserver.org/cgi-bin/wfs?' \
                      'service=WFS&version=1.1.0&' \
                      'request=GetFeature&' \
                      'typename=continents&maxfeatures=2'
        self._value = requests.get(wfsResource).text
        self.iohandler.url = wfsResource
        self._test_outout(SOURCE_TYPE.URL)

    def test_workdir(self):
        """Test workdir"""
        workdir = tempfile.mkdtemp()
        self.iohandler.workdir = workdir
        self.assertTrue(os.path.isdir(self.iohandler.workdir))

        # make another
        workdir = tempfile.mkdtemp()
        self.iohandler.workdir = workdir
        self.assertTrue(os.path.isdir(self.iohandler.workdir))

    def test_memory(self):
        """Test data input IOHandler"""
        self.skipTest('Memory object not implemented')

    def test_data_bytes(self):
        if PY2:
            self.skipTest('fails on python 2.7')
        self._value = b'aa'

        self.iohandler.data = self._value
        self.assertEqual(self.iohandler.source_type, SOURCE_TYPE.DATA,
                         'Source type properly set')

        # test the data handle
        self.assertEqual(self._value, self.iohandler.data, 'Data obtained')

        # test the file handle
        file_handler = open(self.iohandler.file, 'rb')
        self.assertEqual(self._value, file_handler.read(), 'File obtained')
        file_handler.close()

        # test the stream handle
        stream_data = self.iohandler.stream.read()
        self.iohandler.stream.close()
        self.assertEqual(self._value, stream_data, 'Stream obtained')

    def test_is_textfile(self):
        geotiff = os.path.join(DATA_DIR, 'geotiff', 'dem.tiff')
        self.assertFalse(_is_textfile(geotiff))
        gml = os.path.join(DATA_DIR, 'gml', 'point.gml')
        self.assertTrue(_is_textfile(gml))
        geojson = os.path.join(DATA_DIR, 'json', 'point.geojson')
        self.assertTrue(_is_textfile(geojson))


class ComplexInputTest(unittest.TestCase):
    """ComplexInput test cases"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        data_format = get_data_format('application/json')
        self.complex_in = inout.inputs.ComplexInput(identifier="complexinput",
                                                    title='MyComplex',
                                                    abstract='My complex input',
                                                    keywords=['kw1', 'kw2'],
                                                    workdir=self.tmp_dir,
                                                    supported_formats=[data_format])

        self.complex_in.data = "Hallo world!"

    def test_validator(self):
        self.assertEqual(self.complex_in.data_format.validate,
                         get_validator('application/json'))
        self.assertEqual(self.complex_in.validator,
                         get_validator('application/json'))
        frmt = get_data_format('application/json')

        def my_validate():
            return True

        frmt.validate = my_validate
        self.assertNotEqual(self.complex_in.validator, frmt.validate)

    def test_contruct(self):
        self.assertIsInstance(self.complex_in, ComplexInput)

    def test_data_format(self):
        self.assertIsInstance(self.complex_in.supported_formats[0], Format)


class SerializationComplexInputTest(unittest.TestCase):
    """ComplexInput test cases"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def make_complex_input(self):
        complex = inout.inputs.ComplexInput(
            identifier="complexinput",
            title='MyComplex',
            abstract='My complex input',
            keywords=['kw1', 'kw2'],
            workdir=self.tmp_dir,
            supported_formats=[get_data_format('application/json')],
            metadata=[Metadata("special data")],
            default="/some/file/path",
            default_type=SOURCE_TYPE.FILE,
            translations={"fr-CA": {"title": "Mon input", "abstract": "Une description"}},
        )
        complex.as_reference = False
        complex.method = "GET"
        complex.max_size = 1000
        return complex

    def assert_complex_equals(self, complex_1, complex_2):
        self.assertEqual(complex_1.identifier, complex_2.identifier)
        self.assertEqual(complex_1.title, complex_2.title)
        self.assertEqual(complex_1.supported_formats, complex_2.supported_formats)
        self.assertEqual(complex_1.data_format, complex_2.data_format)
        self.assertEqual(complex_1.abstract, complex_2.abstract)
        self.assertEqual(complex_1.keywords, complex_2.keywords)
        self.assertEqual(complex_1.workdir, complex_2.workdir)
        self.assertEqual(complex_1.metadata, complex_2.metadata)
        self.assertEqual(complex_1.max_occurs, complex_2.max_occurs)
        self.assertEqual(complex_1.valid_mode, complex_2.valid_mode)
        self.assertEqual(complex_1.as_reference, complex_2.as_reference)
        self.assertEqual(complex_1.translations, complex_2.translations)

        self.assertEqual(complex_1.prop, complex_2.prop)

        if complex_1.prop != 'url':
            # don't download the file when running tests
            self.assertEqual(complex_1.file, complex_2.file)
            self.assertEqual(complex_1.data, complex_2.data)

        self.assertEqual(complex_1.url, complex_2.url)

    def test_complex_input_file(self):
        complex = self.make_complex_input()
        some_file = os.path.join(self.tmp_dir, "some_file.txt")
        with open(some_file, "w") as f:
            f.write("some data")
        complex.file = some_file
        complex2 = inout.inputs.ComplexInput.from_json(complex.json)
        self.assert_complex_equals(complex, complex2)
        self.assertEqual(complex.prop, 'file')

    def test_complex_input_data(self):
        complex = self.make_complex_input()
        complex.data = "some data"
        complex2 = inout.inputs.ComplexInput.from_json(complex.json)
        # the data is enclosed by a CDATA tag
        complex._data = u'<![CDATA[{}]]>'.format(complex.data)
        # it's expected that the file path changed
        complex._file = complex2.file

        self.assert_complex_equals(complex, complex2)
        self.assertEqual(complex.prop, 'data')

    def test_complex_input_stream(self):
        complex = self.make_complex_input()
        complex.stream = StringIO("some data")
        complex2 = inout.inputs.ComplexInput.from_json(complex.json)

        # the serialized stream becomes a data type
        # we hard-code it for the testing comparison
        complex.prop = 'data'
        # the data is enclosed by a CDATA tag
        complex._data = u'<![CDATA[{}]]>'.format(complex.data)
        # it's expected that the file path changed
        complex._file = complex2.file

        self.assert_complex_equals(complex, complex2)

    def test_complex_input_url(self):
        complex = self.make_complex_input()
        complex.url = "http://test.opendap.org:80/opendap/netcdf/examples/sresa1b_ncar_ccsm3_0_run1_200001.nc"
        complex2 = inout.inputs.ComplexInput.from_json(complex.json)
        self.assert_complex_equals(complex, complex2)
        self.assertEqual(complex.prop, 'url')


class SerializationLiteralInputTest(unittest.TestCase):
    """LiteralInput test cases"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def make_literal_input(self):
        literal = inout.inputs.LiteralInput(
            identifier="complexinput",
            title='MyComplex',
            data_type='string',
            workdir=self.tmp_dir,
            abstract="some description",
            keywords=['kw1', 'kw2'],
            metadata=[Metadata("special data")],
            uoms=['metre', 'unity'],
            min_occurs=2,
            max_occurs=5,
            mode=MODE.STRICT,
            allowed_values=[AllowedValue(value='something'), AllowedValue(value='something else'), AnyValue()],
            default="something else",
            default_type=SOURCE_TYPE.DATA,
        )
        literal.data = 'something'
        literal.uom = UOM('unity')
        literal.as_reference = False
        return literal

    def assert_literal_equals(self, literal_1, literal_2):
        self.assertEqual(literal_1.identifier, literal_2.identifier)
        self.assertEqual(literal_1.title, literal_2.title)
        self.assertEqual(literal_1.data_type, literal_2.data_type)
        self.assertEqual(literal_1.workdir, literal_2.workdir)
        self.assertEqual(literal_1.abstract, literal_2.abstract)
        self.assertEqual(literal_1.keywords, literal_2.keywords)
        self.assertEqual(literal_1.metadata, literal_2.metadata)
        self.assertEqual(literal_1.uoms, literal_2.uoms)
        self.assertEqual(literal_1.min_occurs, literal_2.min_occurs)
        self.assertEqual(literal_1.max_occurs, literal_2.max_occurs)
        self.assertEqual(literal_1.valid_mode, literal_2.valid_mode)
        self.assertEqual(literal_1.allowed_values, literal_2.allowed_values)
        self.assertEqual(literal_1.any_value, literal_2.any_value)
        self.assertTrue(literal_1.any_value)
        self.assertEqual(literal_1.as_reference, literal_2.as_reference)

        self.assertEqual(literal_1.data, literal_2.data)

    def test_literal_input(self):
        literal = self.make_literal_input()
        literal2 = inout.inputs.LiteralInput.from_json(literal.json)
        self.assert_literal_equals(literal, literal2)


class SerializationBoundingBoxInputTest(unittest.TestCase):
    """LiteralInput test cases"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def make_bbox_input(self):
        bbox = inout.inputs.BoundingBoxInput(
            identifier="complexinput",
            title='MyComplex',
            crss=['epsg:3857', 'epsg:4326'],
            abstract="some description",
            keywords=['kw1', 'kw2'],
            dimensions=2,
            workdir=self.tmp_dir,
            metadata=[Metadata("special data")],
            min_occurs=2,
            max_occurs=5,
            mode=MODE.NONE,
            default="something else",
            default_type=SOURCE_TYPE.DATA,
        )
        bbox.as_reference = False
        return bbox

    def assert_bbox_equals(self, bbox_1, bbox_2):
        self.assertEqual(bbox_1.identifier, bbox_2.identifier)
        self.assertEqual(bbox_1.title, bbox_2.title)
        self.assertEqual(bbox_1.crss, bbox_2.crss)
        self.assertEqual(bbox_1.abstract, bbox_2.abstract)
        self.assertEqual(bbox_1.keywords, bbox_2.keywords)
        self.assertEqual(bbox_1.dimensions, bbox_2.dimensions)
        self.assertEqual(bbox_1.workdir, bbox_2.workdir)
        self.assertEqual(bbox_1.metadata, bbox_2.metadata)
        self.assertEqual(bbox_1.min_occurs, bbox_2.min_occurs)
        self.assertEqual(bbox_1.max_occurs, bbox_2.max_occurs)
        self.assertEqual(bbox_1.valid_mode, bbox_2.valid_mode)
        self.assertEqual(bbox_1.as_reference, bbox_2.as_reference)

        self.assertEqual(bbox_1.ll, bbox_2.ll)
        self.assertEqual(bbox_1.ur, bbox_2.ur)

    def test_bbox_input(self):
        bbox = self.make_bbox_input()
        bbox2 = inout.inputs.BoundingBoxInput.from_json(bbox.json)
        self.assert_bbox_equals(bbox, bbox2)


class DodsComplexInputTest(unittest.TestCase):
    """ComplexInput test cases"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        data_format = get_data_format('application/x-ogc-dods')
        self.complex_in = ComplexInput(identifier="complexinput",
                                       title='MyComplex',
                                       abstract='My complex input',
                                       keywords=['kw1', 'kw2'],
                                       workdir=self.tmp_dir,
                                       data_format=data_format,
                                       supported_formats=[data_format, get_data_format('application/x-netcdf')])

        self.complex_in.href = "http://test.opendap.org:80/opendap/netcdf/examples/sresa1b_ncar_ccsm3_0_run1_200001.nc"

    def test_validator(self):
        self.assertEqual(self.complex_in.data_format.validate,
                         get_validator('application/x-ogc-dods'))
        self.assertEqual(self.complex_in.validator,
                         get_validator('application/x-ogc-dods'))
        frmt = get_data_format('application/x-ogc-dods')

        def my_validate():
            return True

        frmt.validate = my_validate
        self.assertNotEqual(self.complex_in.validator, frmt.validate)

    def test_contruct(self):
        self.assertIsInstance(self.complex_in, ComplexInput)


class ComplexOutputTest(unittest.TestCase):
    """ComplexOutput test cases"""

    def setUp(self):
        tmp_dir = tempfile.mkdtemp()
        data_format = get_data_format('application/json')
        self.complex_out = inout.outputs.ComplexOutput(
            identifier="complexoutput",
            title='Complex Output',
            workdir=tmp_dir,
            data_format=data_format,
            supported_formats=[data_format],
            mode=MODE.NONE,
            translations={"fr-CA": {"title": "Mon output", "abstract": "Une description"}},
            )

        self.complex_out_nc = inout.outputs.ComplexOutput(
            identifier="netcdf",
            title="NetCDF output",
            workdir=tmp_dir,
            data_format=get_data_format('application/x-netcdf'),
            supported_formats=[get_data_format('application/x-netcdf')],
            mode=MODE.NONE)

        self.data = json.dumps({'a': 1, 'unicodé': u'éîïç', })
        self.ncfile = os.path.join(DATA_DIR, 'netcdf', 'time.nc')

        self.test_fn = os.path.join(self.complex_out.workdir, 'test.json')
        with open(self.test_fn, 'w') as f:
            f.write(self.data)

    def test_contruct(self):
        self.assertIsInstance(self.complex_out, ComplexOutput)

    def test_data_format(self):
        self.assertIsInstance(self.complex_out.data_format, Format)

    def test_storage(self):
        class Storage(object):
            pass
        storage = Storage()
        self.complex_out.store = storage
        self.assertEqual(self.complex_out.store, storage)

    def test_validator(self):
        self.assertEqual(self.complex_out.validator,
                         get_validator('application/json'))

        self.assertEqual(self.complex_out_nc.validator,
                         get_validator('application/x-netcdf'))

    def test_file_handler(self):
        self.complex_out.file = self.test_fn
        self.assertEqual(self.complex_out.data, self.data)
        if PY2:
            self.assertEqual(self.complex_out.stream.read(), self.data)
        else:
            with self.complex_out.stream as s:
                self.assertEqual(s.read(), bytes(self.data, encoding='utf8'))

        with open(urlparse(self.complex_out.url).path) as f:
            self.assertEqual(f.read(), self.data)

    def test_file_handler_netcdf(self):
        if PY2:
            self.skipTest('fails on python 2.7')
        self.complex_out_nc.file = self.ncfile
        self.complex_out_nc.base64

    def test_data_handler(self):
        if PY2:
            self.skipTest('fails on python 2.7')
        self.complex_out.data = self.data
        with open(self.complex_out.file) as f:
            self.assertEqual(f.read(), self.data)

    def test_base64(self):
        self.complex_out.data = self.data
        b = self.complex_out.base64
        if PY2:
            self.assertEqual(base64.b64decode(b), self.data)
        else:
            self.assertEqual(base64.b64decode(b).decode(), self.data)

    def test_url_handler(self):
        wfsResource = 'http://demo.mapserver.org/cgi-bin/wfs?' \
                      'service=WFS&version=1.1.0&' \
                      'request=GetFeature&' \
                      'typename=continents&maxfeatures=2'
        self.complex_out.url = wfsResource
        self.complex_out.storage = FileStorageBuilder().build()
        url = self.complex_out.get_url()
        self.assertEqual('file', urlparse(url).scheme)

    def test_json(self):
        new_output = inout.outputs.ComplexOutput.from_json(self.complex_out.json)
        self.assertEqual(new_output.identifier, 'complexoutput')
        self.assertEqual(
            new_output.translations,
            {"fr-ca": {"title": "Mon output", "abstract": "Une description"}},
            'translations does not exist'
        )


class SimpleHandlerTest(unittest.TestCase):
    """SimpleHandler test cases"""

    def setUp(self):

        data_type = 'integer'

        self.simple_handler = SimpleHandler(data_type=data_type)

    def test_contruct(self):
        self.assertIsInstance(self.simple_handler, SimpleHandler)

    def test_data_type(self):
        self.assertEqual(convert(self.simple_handler.data_type, '1'), 1)


class LiteralInputTest(unittest.TestCase):
    """LiteralInput test cases"""

    def setUp(self):

        self.literal_input = inout.inputs.LiteralInput(
            identifier="literalinput",
            title="Literal Input",
            data_type='integer',
            mode=2,
            allowed_values=(1, 2, (3, 3, 12)),
            default=6,
            uoms=(UOM("metre"),),
            translations={"fr-CA": {"title": "Mon input", "abstract": "Une description"}},
        )

    def test_contruct(self):
        self.assertIsInstance(self.literal_input, LiteralInput)
        self.assertEqual(len(self.literal_input.allowed_values), 3)
        self.assertIsInstance(self.literal_input.allowed_values[0], AllowedValue)
        self.assertIsInstance(self.literal_input.allowed_values[2], AllowedValue)
        self.assertEqual(self.literal_input.allowed_values[2].spacing, 3)
        self.assertEqual(self.literal_input.allowed_values[2].minval, 3)
        self.assertEqual(self.literal_input.data, 6, "Default value set to 6")

    def test_valid(self):
        self.assertEqual(self.literal_input.data, 6)
        self.literal_input.data = 1
        self.assertEqual(self.literal_input.data, 1)

        with self.assertRaises(InvalidParameterValue):
            self.literal_input.data = 5

        with self.assertRaises(InvalidParameterValue):
            self.literal_input.data = "a"

        with self.assertRaises(InvalidParameterValue):
            self.literal_input.data = 15

        self.literal_input.data = 6
        self.assertEqual(self.literal_input.data, 6)

    def test_json_out(self):
        self.literal_input.data = 9
        out = self.literal_input.json

        self.assertTrue('uoms' in out, 'UOMs does not exist')
        self.assertTrue('uom' in out, 'uom does not exist')
        self.assertFalse(out['workdir'], 'Workdir exist')
        self.assertEqual(out['data_type'], 'integer', 'Data type is integer')
        self.assertFalse(out['abstract'], 'abstract exist')
        self.assertFalse(out['keywords'], 'keywords exist')
        self.assertTrue(out['title'], 'title does not exist')
        self.assertEqual(out['data'], '9', 'data set')
        self.assertEqual(out['mode'], MODE.STRICT, 'Mode set')
        self.assertEqual(out['identifier'], 'literalinput', 'identifier set')
        self.assertEqual(out['type'], 'literal', 'it\'s literal input')
        self.assertEqual(len(out['allowed_values']), 3, '3 allowed values')
        self.assertEqual(out['allowed_values'][0]['value'], 1, 'allowed value 1')
        self.assertEqual(
            out['translations'],
            {"fr-ca": {"title": "Mon input", "abstract": "Une description"}},
            'translations does not exist'
        )

    def test_json_out_datetime(self):
        inpt = inout.inputs.LiteralInput(
            identifier="datetime",
            title="Literal Input",
            mode=2,
            data_type='dateTime')
        inpt.data = "2017-04-20T12:30:00"
        out = inpt.json
        self.assertEqual(out['data'], '2017-04-20 12:30:00', 'datetime set')

    def test_json_out_time(self):
        inpt = inout.inputs.LiteralInput(
            identifier="time",
            title="Literal Input",
            mode=2,
            data_type='time')
        inpt.data = "12:30:00"
        out = inpt.json
        self.assertEqual(out['data'], '12:30:00', 'time set')

    def test_json_out_date(self):
        inpt = inout.inputs.LiteralInput(
            identifier="date",
            title="Literal Input",
            mode=2,
            data_type='date')
        inpt.data = "2017-04-20"
        out = inpt.json
        self.assertEqual(out['data'], '2017-04-20', 'date set')

    def test_translations(self):
        title_fr = get_translation(self.literal_input, "title", "fr-CA")
        assert title_fr == "Mon input"
        abstract_fr = get_translation(self.literal_input, "abstract", "fr-CA")
        assert abstract_fr == "Une description"
        identifier = get_translation(self.literal_input, "identifier", "fr-CA")
        assert identifier == self.literal_input.identifier

class LiteralOutputTest(unittest.TestCase):
    """LiteralOutput test cases"""

    def setUp(self):

        self.literal_output = inout.outputs.LiteralOutput(
            "literaloutput", 
            data_type="integer", 
            title="Literal Output",
            translations={"fr-CA": {"title": "Mon output", "abstract": "Une description"}},
        )

    def test_contruct(self):
        self.assertIsInstance(self.literal_output, LiteralOutput)

    def test_storage(self):
        class Storage(object):
            pass
        storage = Storage()
        self.literal_output.store = storage
        self.assertEqual(self.literal_output.store, storage)

    def test_json(self):
        new_output = inout.outputs.LiteralOutput.from_json(self.literal_output.json)
        self.assertEqual(new_output.identifier, 'literaloutput')
        self.assertEqual(
            new_output.translations,
            {"fr-ca": {"title": "Mon output", "abstract": "Une description"}},
            'translations does not exist'
        )


class BBoxInputTest(unittest.TestCase):
    """BountingBoxInput test cases"""

    def setUp(self):

        self.bbox_input = inout.inputs.BoundingBoxInput(
            "bboxinput", 
            title="BBox input", 
            dimensions=2,
            translations={"fr-CA": {"title": "Mon input", "abstract": "Une description"}},
        )
        self.bbox_input.data = [0, 1, 2, 4]

    def test_contruct(self):
        self.assertIsInstance(self.bbox_input, BBoxInput)

    def test_json_out(self):
        out = self.bbox_input.json

        self.assertTrue(out['identifier'], 'identifier exists')
        self.assertTrue(out['title'], 'title does not exist')
        self.assertFalse(out['abstract'], 'abstract set')
        self.assertEqual(out['type'], 'bbox', 'type set')
        # self.assertTupleEqual(out['bbox'], ([0, 1], [2, 4]), 'data are there')
        self.assertEqual(out['bbox'], [0, 1, 2, 4], 'data are there')
        self.assertEqual(out['dimensions'], 2, 'Dimensions set')
        self.assertEqual(
            out['translations'],
            {"fr-ca": {"title": "Mon input", "abstract": "Une description"}},
            'translations does not exist'
        )


class BBoxOutputTest(unittest.TestCase):
    """BoundingBoxOutput test cases"""

    def setUp(self):
        self.bbox_out = inout.outputs.BoundingBoxOutput(
            "bboxoutput",
            title="BBox output",
            dimensions=2,
            crss=['epsg:3857', 'epsg:4326'],
            translations={"fr-CA": {"title": "Mon output", "abstract": "Une description"}},
        )

    def test_contruct(self):
        self.assertIsInstance(self.bbox_out, BBoxOutput)

    def test_storage(self):
        class Storage(object):
            pass
        storage = Storage()
        self.bbox_out.store = storage
        self.assertEqual(self.bbox_out.store, storage)

    def test_json(self):
        new_bbox = inout.outputs.BoundingBoxOutput.from_json(self.bbox_out.json)
        self.assertEqual(new_bbox.identifier, 'bboxoutput')
        self.assertEqual(
            new_bbox.translations,
            {"fr-ca": {"title": "Mon output", "abstract": "Une description"}},
            'translations does not exist'
        )


class TestMetaLink(unittest.TestCase):
    tmp_dir = tempfile.mkdtemp()

    def metafile(self):
        mf = MetaFile('identifier', 'title', fmt=FORMATS.JSON)
        mf.data = json.dumps({'a': 1})
        mf._set_workdir(self.tmp_dir)
        return mf

    def test_metafile(self):
        mf = self.metafile()
        self.assertEqual('identifier', mf.identity)

    def metalink(self):
        ml = MetaLink(identity='unittest', description='desc', files=(self.metafile(), ), workdir=self.tmp_dir)
        return ml

    def metalink4(self):
        ml = MetaLink4(identity='unittest', description='desc', files=(self.metafile(), ), workdir=self.tmp_dir)
        return ml

    def test_metalink(self):
        from pywps.validator.complexvalidator import validatexml

        out = inout.outputs.ComplexOutput('metatest', 'MetaLink Test title', abstract='MetaLink test abstract',
                                          supported_formats=[FORMATS.METALINK, ],
                                          as_reference=True)
        out.workdir = self.tmp_dir
        ml = self.metalink()

        out.data = ml.xml
        self.assertTrue(validatexml(out, MODE.STRICT))

    def test_metalink4(self):
        from pywps.validator.complexvalidator import validatexml

        out = inout.outputs.ComplexOutput('metatest', 'MetaLink4 Test title', abstract='MetaLink4 test abstract',
                                          supported_formats=[FORMATS.META4, ],
                                          as_reference=True)
        out.workdir = self.tmp_dir
        ml = self.metalink4()

        out.data = ml.xml
        self.assertTrue(validatexml(out, MODE.STRICT))

    def test_hash(self):
        ml = self.metalink()
        assert 'hash' not in ml.xml

        ml.checksums = True
        assert 'hash' in ml.xml

        ml4 = self.metalink4()
        assert 'hash' not in ml4.xml

        ml4.checksums = True
        assert 'hash' in ml4.xml


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(IOHandlerTest),
        loader.loadTestsFromTestCase(ComplexInputTest),
        loader.loadTestsFromTestCase(DodsComplexInputTest),
        loader.loadTestsFromTestCase(ComplexOutputTest),
        loader.loadTestsFromTestCase(SerializationBoundingBoxInputTest),
        loader.loadTestsFromTestCase(SerializationComplexInputTest),
        loader.loadTestsFromTestCase(SerializationLiteralInputTest),
        loader.loadTestsFromTestCase(SimpleHandlerTest),
        loader.loadTestsFromTestCase(LiteralInputTest),
        loader.loadTestsFromTestCase(LiteralOutputTest),
        loader.loadTestsFromTestCase(BBoxInputTest),
        loader.loadTestsFromTestCase(BBoxOutputTest)
    ]
    return unittest.TestSuite(suite_list)
