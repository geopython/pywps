"""Unit tests for IOs
"""
##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import tempfile
import datetime
import unittest
from pywps import Format
from pywps.validator import get_validator
from pywps import NAMESPACES
from pywps.inout.basic import IOHandler, SOURCE_TYPE, SimpleHandler, BBoxInput, BBoxOutput, \
    ComplexInput, ComplexOutput, LiteralOutput, LiteralInput
from pywps.inout import BoundingBoxInput as BoundingBoxInputXML
from pywps.inout.literaltypes import convert, AllowedValue
from pywps._compat import StringIO, text_type
from pywps.validator.base import emptyvalidator
from pywps.exceptions import InvalidParameterValue
from pywps.validator.mode import MODE

from lxml import etree


def get_data_format(mime_type):
    return Format(mime_type=mime_type,
    validate=get_validator(mime_type))

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

        if type(stream_val) == type(b''):
            self.assertEqual(str.encode(self._value), stream_val,
                             'Stream obtained')
        else:
            self.assertEqual(self._value, stream_val,
                             'Stream obtained')

        if self.iohandler.source_type == SOURCE_TYPE.STREAM:
            source = StringIO(text_type(self._value))
            self.iohandler.stream = source

        self.skipTest('Memory object not implemented')
        self.assertEqual(stream_val, self.iohandler.memory_object,
                         'Memory object obtained')

    def test_data(self):
        """Test data input IOHandler"""
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


class ComplexInputTest(unittest.TestCase):
    """ComplexInput test cases"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        data_format = get_data_format('application/json')
        self.complex_in = ComplexInput(identifier="complexinput",
                                       title='MyComplex',
                                       abstract='My complex input',
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

    def test_json_out(self):
        out = self.complex_in.json

        self.assertEqual(out['workdir'], self.tmp_dir, 'Workdir defined')
        self.assertTrue(out['file'], 'There is no file')
        self.assertTrue(out['supported_formats'], 'There are some formats')
        self.assertEqual(len(out['supported_formats']), 1, 'There is one formats')
        self.assertEqual(out['title'], 'MyComplex', 'Title not set but existing')
        self.assertEqual(out['abstract'], 'My complex input', 'Abstract not set but existing')
        self.assertEqual(out['identifier'], 'complexinput', 'identifier set')
        self.assertEqual(out['type'], 'complex', 'it is complex input')
        self.assertTrue(out['data_format'], 'data_format set')
        self.assertEqual(out['data_format']['mime_type'], 'application/json', 'data_format set')

class ComplexOutputTest(unittest.TestCase):
    """ComplexOutput test cases"""

    def setUp(self):
        tmp_dir = tempfile.mkdtemp()
        data_format = get_data_format('application/json')
        self.complex_out = ComplexOutput(identifier="complexinput", workdir=tmp_dir,
                                         data_format=data_format,
                                         supported_formats=[data_format])

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

        self.literal_input = LiteralInput(
                identifier="literalinput",
                mode=2,
                allowed_values=(1, 2, (3, 3, 12)),
                default=6)


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

        self.assertFalse(out['uoms'], 'UOMs exist')
        self.assertFalse(out['workdir'], 'Workdir exist')
        self.assertEqual(out['data_type'], 'integer', 'Data type is integer')
        self.assertFalse(out['abstract'], 'abstract exist')
        self.assertFalse(out['title'], 'title exist')
        self.assertEqual(out['data'], 9, 'data set')
        self.assertEqual(out['mode'], MODE.STRICT, 'Mode set')
        self.assertEqual(out['identifier'], 'literalinput', 'identifier set')
        self.assertEqual(out['type'], 'literal', 'it\'s literal input')
        self.assertFalse(out['uom'], 'uom exists')
        self.assertEqual(len(out['allowed_values']), 3, '3 allowed values')
        self.assertEqual(out['allowed_values'][0]['value'], 1, 'allowed value 1')

    def test_json_out_datetime(self):
        inpt = LiteralInput(
            identifier="datetime",
            mode=2,
            data_type='dateTime')
        inpt.data = "2017-04-20T12:30:00"
        out = inpt.json
        self.assertEqual(out['data'], datetime.datetime(2017, 4, 20, 12, 30, 0), 'datetime set')

    def test_json_out_time(self):
        inpt = LiteralInput(
            identifier="time",
            mode=2,
            data_type='time')
        inpt.data = "12:30:00"
        out = inpt.json
        self.assertEqual(out['data'], datetime.time(12, 30, 0), 'time set')

    def test_json_out_date(self):
        inpt = LiteralInput(
            identifier="date",
            mode=2,
            data_type='date')
        inpt.data = "2017-04-20"
        out = inpt.json
        self.assertEqual(out['data'], datetime.date(2017, 4, 20), 'date set')



class LiteralOutputTest(unittest.TestCase):
    """LiteralOutput test cases"""

    def setUp(self):

        self.literal_output = LiteralOutput("literaloutput", data_type="integer")

    def test_contruct(self):
        self.assertIsInstance(self.literal_output, LiteralOutput)

    def test_storage(self):
        class Storage(object):
            pass
        storage = Storage()
        self.literal_output.store = storage
        self.assertEqual(self.literal_output.store, storage)

class BoxInputTest(unittest.TestCase):
    """BBoxInput test cases"""

    def setUp(self):

        self.bbox_input = BBoxInput("bboxinput", dimensions=2)
        self.bbox_input.ll = [0, 1]
        self.bbox_input.ur = [2, 4]

    def test_contruct(self):
        self.assertIsInstance(self.bbox_input, BBoxInput)

    def test_json_out(self):
        out = self.bbox_input.json

        self.assertTrue(out['identifier'], 'identifier exists')
        self.assertFalse(out['title'], 'title exists')
        self.assertFalse(out['abstract'], 'abstract set')
        self.assertEqual(out['type'], 'bbox', 'type set')
        self.assertTupleEqual(out['bbox'], ([0, 1], [2, 4]), 'data are tehre')
        self.assertEqual(out['dimensions'], 2, 'Dimensions set')


class BoxOutputTest(unittest.TestCase):
    """BoundingBoxOutput test cases"""

    def setUp(self):

        self.bbox_out = BBoxOutput("bboxoutput")

    def test_contruct(self):
        self.assertIsInstance(self.bbox_out, BBoxOutput)

    def test_storage(self):
        class Storage(object):
            pass
        storage = Storage()
        self.bbox_out.store = storage
        self.assertEqual(self.bbox_out.store, storage)

def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(IOHandlerTest),
        loader.loadTestsFromTestCase(ComplexInputTest),
        loader.loadTestsFromTestCase(ComplexOutputTest),
        loader.loadTestsFromTestCase(SimpleHandlerTest),
        loader.loadTestsFromTestCase(LiteralInputTest),
        loader.loadTestsFromTestCase(LiteralOutputTest),
        loader.loadTestsFromTestCase(BoxInputTest),
        loader.loadTestsFromTestCase(BoxOutputTest)
    ]
    return unittest.TestSuite(suite_list)
