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


    def tearDown(self):
        pass

    def test_basic_IOHandler(self):
        """Test basic IOHandler"""
        self.assertTrue(os.path.isdir(self.iohandler.tempdir))
        self.assertTrue(self.iohandler.data_format)

    def test_data(self):
        """Test data input IOHandler"""
        source = 'lalala'
        self.iohandler.data = source
        self.assertEqual(SOURCE_TYPE.DATA, self.iohandler.source_type,
                          'Source type properly set')
        self.assertEqual(source, self.iohandler.data, 'Data obtained')
        file_handler = open(self.iohandler.file)
        self.assertEqual(source, file_handler.read(), 'File obtained')
        file_handler.close()
        self.assertEqual(source, self.iohandler.stream.read(),
                          'Stream obtained')
        self.skipTest('Memory object not implemented')
        self.assertEqual(source, self.iohandler.memory_object,
                          'Memory object obtained')

    def test_stream(self):
        """Test stream input IOHandler"""
        value = 'lalala'
        source = StringIO(text_type(value))
        self.iohandler.stream = source
        self.assertEqual(SOURCE_TYPE.STREAM, self.iohandler.source_type,
                          'Source type properly set')
        self.assertEqual(value, self.iohandler.data, 'Data obtained')

        source = StringIO(text_type(value))
        self.iohandler.stream = source

        file_handler = open(self.iohandler.file)
        self.assertEqual(value, file_handler.read(), 'File obtained')
        file_handler.close()

        source = StringIO(text_type(value))
        self.iohandler.stream = source

        self.assertEqual(value, self.iohandler.stream.read(),
                          'Stream obtained')

        source = StringIO(text_type(value))
        self.iohandler.stream = source

        self.skipTest('Memory object not implemented')
        self.assertEqual(data, self.iohandler.memory_object,
                          'Memory object obtained')

    def test_file(self):
        """Test file input IOHandler"""
        pass
        # TODO
        #value = 'lalala'
        #source = StringIO(text_type(value))
        #self.iohandler.stream = source
        #self.assertEqual(SOURCE_TYPE.STREAM, self.iohandler.source_type,
        #                  'Source type properly set')
        #self.assertEqual(value, self.iohandler.data, 'Data obtained')

        #source = StringIO(text_type(value))
        #self.iohandler.stream = source

        #self.assertEqual(value, open(self.iohandler.file).read(),
        #                  'File obtained')

        #source = StringIO(text_type(value))
        #self.iohandler.stream = source

        #self.assertEqual(value, self.iohandler.stream.read(),
        #                  'Stream obtained')

        #source = StringIO(text_type(value))
        #self.iohandler.stream = source

        #self.skipTest('Memory object not implemented')
        #self.assertEqual(data, self.iohandler.memory_object,
        #                  'Memory object obtained')



def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(IOHandlerTest)
    ]
    return unittest.TestSuite(suite_list)
