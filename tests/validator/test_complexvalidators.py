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
from pywps import ComplexInput
from pywps.inout.basic import SOURCE_TYPE
import tempfile
import os

try:
    import osgeo
except ImportError:
    WITH_GDAL = False
else:
    WITH_GDAL = True

try:
    import netCDF4
except ImportError:
    WITH_NC4 = False
else:
    WITH_NC4 = True

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

    def test_json_validator(self):
        """Test GeoJSON validator
        """
        json_input = get_input('json/point.geojson', None, FORMATS.JSON.mime_type)
        self.assertTrue(validatejson(json_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validatejson(json_input, MODE.SIMPLE), 'SIMPLE validation')
        self.assertTrue(validatejson(json_input, MODE.STRICT), 'STRICT validation')
        json_input.stream.close()

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
            self.skipTest('GDAL not Installed')
        self.assertTrue(validategeotiff(geotiff_input, MODE.STRICT), 'STRICT validation')
        geotiff_input.stream.close()

    def test_netcdf_validator(self):
        """Test netCDF validator
        """
        netcdf_input = get_input('netcdf/time.nc', None, FORMATS.NETCDF.mime_type)
        self.assertTrue(validatenetcdf(netcdf_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validatenetcdf(netcdf_input, MODE.SIMPLE), 'SIMPLE validation')
        netcdf_input.stream.close()
        if WITH_NC4:
            self.assertTrue(validatenetcdf(netcdf_input, MODE.STRICT), 'STRICT validation')
            netcdf_input.file = 'grub.nc'
            self.assertFalse(validatenetcdf(netcdf_input, MODE.STRICT))
        else:
            self.assertFalse(validatenetcdf(netcdf_input, MODE.STRICT), 'STRICT validation')

    def test_dods_validator(self):
        opendap_input = ComplexInput('dods', 'opendap test', [FORMATS.DODS,])
        opendap_input.url = "http://test.opendap.org:80/opendap/netcdf/examples/sresa1b_ncar_ccsm3_0_run1_200001.nc"
        self.assertTrue(validatedods(opendap_input, MODE.NONE), 'NONE validation')
        self.assertTrue(validatedods(opendap_input, MODE.SIMPLE), 'SIMPLE validation')

        if WITH_NC4:
            self.assertTrue(validatedods(opendap_input, MODE.STRICT), 'STRICT validation')
            opendap_input.url = 'Faulty url'
            self.assertFalse(validatedods(opendap_input, MODE.STRICT))
        else:
            self.assertFalse(validatedods(opendap_input, MODE.STRICT), 'STRICT validation')

    def test_dods_default(self):
        opendap_input = ComplexInput('dods', 'opendap test', [FORMATS.DODS,],
                                     default='http://test.opendap.org',
                                     default_type=SOURCE_TYPE.URL,
                                     mode=MODE.SIMPLE)


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
