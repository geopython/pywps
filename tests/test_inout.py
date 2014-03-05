"""Unit tests for IOs
"""
import unittest
from pywps.inout import *
import os
import tempfile
from path import path
from pywps._compat import text_type, StringIO

def get_data_format():
    class DataFormat(FormatAbstract):
        pass
    return DataFormat(mimetype= 'text/plain')

class IOHandlerTest(unittest.TestCase):
    """IOHandler test cases"""

    def setUp(self):
        tmp_dir = path(tempfile.mkdtemp())
        data_format = get_data_format()
        self.iohandler = IOHandler(tempdir=tmp_dir, data_format = data_format)
        self._value = 'lalala'


    def tearDown(self):
        pass

    def test_basic_IOHandler(self):
        """Test basic IOHandler"""
        self.assertTrue(os.path.isdir(self.iohandler.tempdir))
        self.assertTrue(self.iohandler.data_format)

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


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(IOHandlerTest)
    ]
    return unittest.TestSuite(suite_list)
