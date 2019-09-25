##################################################################
# Copyright 2019 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
import pywps.configuration as config
from pywps import Service, Process, ComplexInput, get_format, \
    get_ElementMakerForVersion
from pywps.tests import client_for, assert_response_success

WPS, OWS = get_ElementMakerForVersion("1.0.0")


def grass_epsg_based_location():
    """Return a Process creating a GRASS location based on an EPSG code."""
    def epsg_location(request, response):
        """Check whether the EPSG of a mapset corresponds the specified one."""
        from grass.script import parse_command

        g_proj = parse_command('g.proj', flags='g')

        assert g_proj['epsg'] == '5514', \
            'Error in creating a GRASS location based on an EPSG code'

        return response

    return Process(handler=epsg_location,
                   identifier='my_epsg_based_location',
                   title='EPSG location',
                   grass_location="EPSG:5514")


def grass_file_based_location():
    """Return a Process creating a GRASS location from a georeferenced file."""
    def file_location(request, response):
        """Check whether the datum of a mapset corresponds the file one."""
        from grass.script import parse_command

        g_proj = parse_command('g.proj', flags='g')

        assert g_proj['datum'] == 'wgs84', \
            'Error in creating a GRASS location based on a file'

        return response

    inputs = [ComplexInput(identifier='input1',
                           supported_formats=[get_format('GEOTIFF')],
                           title="Name of input vector map")]

    return Process(handler=file_location,
                   identifier='my_file_based_location',
                   title='File location',
                   inputs=inputs,
                   grass_location="complexinput:input1")


class GRASSTests(unittest.TestCase):
    """Test creating GRASS locations and mapsets in different ways."""

    def setUp(self):
        """Skip test if GRASS is not installed on the machine."""
        if not config.CONFIG.get('grass', 'gisbase'):
            self.skipTest('GRASS lib not found')

    def test_epsg_based_location(self):
        """Test whether the EPSG of a mapset corresponds the specified one."""
        my_process = grass_epsg_based_location()
        client = client_for(Service(processes=[my_process]))

        request_doc = WPS.Execute(
            OWS.Identifier('my_epsg_based_location'),
            version='1.0.0'
        )

        resp = client.post_xml(doc=request_doc)
        assert_response_success(resp)

    def test_file_based_location(self):
        """Test whether the datum of a mapset corresponds the file one."""
        my_process = grass_file_based_location()
        client = client_for(Service(processes=[my_process]))

        href = 'http://demo.mapserver.org/cgi-bin/wfs?service=WFS&' \
               'version=1.1.0&request=GetFeature&typename=continents&' \
               'maxfeatures=1'

        request_doc = WPS.Execute(
            OWS.Identifier('my_file_based_location'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('input1'),
                    WPS.Reference(
                        {'{http://www.w3.org/1999/xlink}href': href}))),
            version='1.0.0')

        resp = client.post_xml(doc=request_doc)
        assert_response_success(resp)


def load_tests(loader=None, tests=None, pattern=None):
    """Load tests."""
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(GRASSTests),
    ]
    return unittest.TestSuite(suite_list)
