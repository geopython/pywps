##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Unit tests for complex validator
"""

import unittest
import sys
from pywps.validator.complexvalidator import *
from pywps.inout.formats import FORMATS
import tempfile
import os

try:
    import osgeo
except ImportError:
    WITH_GDAL = False
else:
    WITH_GDAL = True

def get_input(name, schema, mime_type):

    class FakeFormat(object):
        mimetype = 'text/plain'
        schema = None
        units = None
        def validate(self, data):
            return True

    class FakeInput(object):
        tempdir = tempfile.mkdtemp()
        file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'data', name)
        format = FakeFormat()

    class data_format(object):
        file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'data', str(schema))

    fake_input = FakeInput()
    fake_input.stream = open(fake_input.file)
    fake_input.data_format = data_format()
    if schema:
        fake_input.data_format.schema = 'file://' + fake_input.data_format.file
    fake_input.data_format.mime_type = mime_type

    return fake_input


class ValidateTest(unittest.TestCase):
    """Complex validator test cases"""

    def setUp(self):
        pass


    def tearDown(self):
        pass

    @unittest.skip('long')
    def test_gml_validator(self):
        """Test GML validator
        """
        gml_input = get_input('gml/point.gml', 'point.xsd', FORMATS.GML.mime_type)
        self.assertTrue(validategml(gml_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validategml(gml_input, MODE.SIMPLE), 'SIMPLE validation')
        if WITH_GDAL:
            self.assertTrue(validategml(gml_input, MODE.STRICT), 'STRICT validation')
            self.assertTrue(validategml(gml_input, MODE.VERYSTRICT), 'VERYSTRICT validation')
        gml_input.stream.close()

    def test_geojson_validator(self):
        """Test GeoJSON validator
        """
        geojson_input = get_input('json/point.geojson', 'json/schema/geojson.json',
                                  FORMATS.GEOJSON.mime_type)
        self.assertTrue(validategeojson(geojson_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validategeojson(geojson_input, MODE.SIMPLE), 'SIMPLE validation')
        if WITH_GDAL:
            self.assertTrue(validategeojson(geojson_input, MODE.STRICT), 'STRICT validation')
            self.assertTrue(validategeojson(geojson_input, MODE.VERYSTRICT), 'VERYSTRICT validation')
        geojson_input.stream.close()

    def test_shapefile_validator(self):
        """Test ESRI Shapefile validator
        """
        shapefile_input = get_input('shp/point.shp.zip', None,
                FORMATS.SHP.mime_type)
        self.assertTrue(validateshapefile(shapefile_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validateshapefile(shapefile_input, MODE.SIMPLE), 'SIMPLE validation')
        if WITH_GDAL:
            self.assertTrue(validateshapefile(shapefile_input, MODE.STRICT), 'STRICT validation')
        shapefile_input.stream.close()

    def test_geotiff_validator(self):
        """Test GeoTIFF validator
        """
        geotiff_input = get_input('geotiff/dem.tiff', None,
                                  FORMATS.GEOTIFF.mime_type)
        self.assertTrue(validategeotiff(geotiff_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validategeotiff(geotiff_input, MODE.SIMPLE), 'SIMPLE validation')
        if not WITH_GDAL:
            self.testSkipp('GDAL Not Installed')
        self.assertTrue(validategeotiff(geotiff_input, MODE.STRICT), 'STRICT validation')
        geotiff_input.stream.close()

    def test_fail_validator(self):
        fake_input = get_input('point.xsd', 'point.xsd', FORMATS.SHP.mime_type)
        self.assertFalse(validategml(fake_input, MODE.SIMPLE), 'SIMPLE validation invalid')
        fake_input.stream.close()

def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ValidateTest)
    ]
    return unittest.TestSuite(suite_list)
