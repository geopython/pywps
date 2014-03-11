"""Unit tests for IOs
"""
import unittest
from pywps.inout import *
import os
import tempfile
from path import path
from pywps._compat import text_type, StringIO

def get_data_format():
    class DataFormat(FormatBase):
        pass
    return DataFormat(mimetype= 'text/plain')

class IOHandlerTest(unittest.TestCase):
    """IOHandler test cases"""

    def setUp(self):
        tmp_dir = path(tempfile.mkdtemp())
        self.iohandler = IOHandler(tempdir=tmp_dir)
        self._value = 'lalala'

    def tearDown(self):
        pass

    def test_basic_IOHandler(self):
        """Test basic IOHandler"""
        self.assertTrue(os.path.isdir(self.iohandler.tempdir))

    def _test_outout(self, source_type):
        """Test all outputs"""

        self.assertEqual(source_type, self.iohandler.source_type,
                          'Source type properly set')

        self.assertEqual(self._value, self.iohandler.data, 'Data obtained')

        if self.iohandler.source_type == SOURCE_TYPE.STREAM:
            source = StringIO(text_type(self._value))
            self.iohandler.stream = source

        file_handler = open(self.iohandler.file)
        self.assertEqual(self._value, file_handler.read(), 'File obtained')
        file_handler.close()

        if self.iohandler.source_type == SOURCE_TYPE.STREAM:
            source = StringIO(text_type(self._value))
            self.iohandler.stream = source

        stream_val = self.iohandler.stream.read()
        if type(stream_val) == type(b''):
            self.assertEqual(str.encode(self._value), stream_val,
                            'Stream obtained')
        else:
            self.assertEqual(self._value, stream_val,
                            'Stream obtained')
        self.iohandler.stream.close()

        if self.iohandler.source_type == SOURCE_TYPE.STREAM:
            source = StringIO(text_type(self._value))
            self.iohandler.stream = source

        self.skipTest('Memory object not implemented')
        self.assertEqual(data, self.iohandler.memory_object,
                          'Memory object obtained')


    def test_data(self):
        """Test data input IOHandler"""
        self.iohandler.data = self._value
        self._test_outout(SOURCE_TYPE.DATA)

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

    def test_memory(self):
        """Test data input IOHandler"""
        self.skipTest('Memory object not implemented')


class ComplexInputTest(unittest.TestCase):
    """ComplexInput test cases"""

    def setUp(self):
        tmp_dir = path(tempfile.mkdtemp())
        data_format = get_data_format()
        self.complex_in = ComplexInput(tempdir=tmp_dir,
                                       data_format=data_format)

    def test_contruct(self):
        self.assertIsInstance(self.complex_in, ComplexInput)

    def test_data_format(self):
        self.assertIsInstance(self.complex_in.data_format, FormatBase)


class ComplexOutputTest(unittest.TestCase):
    """ComplexOutput test cases"""

    def setUp(self):
        tmp_dir = path(tempfile.mkdtemp())
        data_format = get_data_format()
        self.complex_out = ComplexOutput(tempdir=tmp_dir,
                                         data_format=data_format)

    def test_contruct(self):
        self.assertIsInstance(self.complex_out, ComplexOutput)

    def test_data_format(self):
        self.assertIsInstance(self.complex_out.data_format, FormatBase)

    def test_storage(self):
        class Storage(object):
            pass
        storage = Storage()
        self.complex_out.store = storage
        self.assertEqual(self.complex_out.store, storage)


class SimpleHandlerTest(unittest.TestCase):
    """SimpleHandler test cases"""

    def setUp(self):

        class IntegerDataType(DataTypeAbstract):
            def convert(self, value):
                return int(value)
        data_type = IntegerDataType()

        self.simple_handler = SimpleHandler(data_type=data_type)

    def test_contruct(self):
        self.assertIsInstance(self.simple_handler, SimpleHandler)

    def test_data_type(self):
        self.assertEqual(self.simple_handler.data_type.convert('1'), 1)

class BasicLiteralInputTest(unittest.TestCase):
    """BasicLiteralInput test cases"""

    def setUp(self):

        self.literal_input = BasicLiteralInput()

    def test_contruct(self):
        self.assertIsInstance(self.literal_input, BasicLiteralInput)


class BasicLiteralOutputTest(unittest.TestCase):
    """BasicLiteralOutput test cases"""

    def setUp(self):

        self.literal_output = BasicLiteralOutput()

    def test_contruct(self):
        self.assertIsInstance(self.literal_output, BasicLiteralOutput)

    def test_storage(self):
        class Storage(object):
            pass
        storage = Storage()
        self.literal_output.store = storage
        self.assertEqual(self.literal_output.store, storage)

class BasicBBoxInputTest(unittest.TestCase):
    """BasicLiteralInput test cases"""

    def setUp(self):

        self.bbox_input = BasicBBoxInput()

    def test_contruct(self):
        self.assertIsInstance(self.bbox_input, BasicBBoxInput)


class BasicBBoxOutputTest(unittest.TestCase):
    """BasicLiteralOutput test cases"""

    def setUp(self):

        self.bbox_out = BasicBBoxOutput()

    def test_contruct(self):
        self.assertIsInstance(self.bbox_out, BasicBBoxOutput)

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
        loader.loadTestsFromTestCase(SimpleHandlerTest),
        loader.loadTestsFromTestCase(BasicLiteralInputTest),
        loader.loadTestsFromTestCase(BasicLiteralOutputTest)
    ]
    return unittest.TestSuite(suite_list)
