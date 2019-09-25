##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

__author__ = "Luis de Sousa"
__date__ = "10-03-2015"

import os
import tempfile
import unittest
import lxml.etree
import sys
from pywps import Service, Process, ComplexInput, ComplexOutput, Format, FORMATS, get_format
from pywps.dependencies import ogr
from pywps.exceptions import NoApplicableCode
from pywps import get_ElementMakerForVersion
from pywps.wpsserver import temp_dir
import pywps.configuration as config
from pywps.tests import client_for, assert_response_success, service_ok

wfsResource = 'https://demo.mapserver.org/cgi-bin/wfs?service=WFS&version=1.1.0&request=GetFeature&typename=continents&maxfeatures=10'  # noqa
wcsResource = 'https://demo.mapserver.org/cgi-bin/wcs?service=WCS&version=1.0.0&request=GetCoverage&coverage=ndvi&crs=EPSG:4326&bbox=-92,42,-85,45&format=image/tiff&width=400&height=300'  # noqa

WPS, OWS = get_ElementMakerForVersion("1.0.0")


def create_feature():

    def feature(request, response):
        input = request.inputs['input'][0].file
        # What do we need to assert a Complex input?
        # assert type(input) is text_type

        # open the input file
        try:
            inSource = ogr.Open(input)
        except Exception as e:
            return "Could not open given vector file: {}".format(e)
        inLayer = inSource.GetLayer()

        # create output file
        out = 'point'
        outPath = os.path.join(tempfile.gettempdir(), out)

        driver = ogr.GetDriverByName('GML')
        outSource = driver.CreateDataSource(
            outPath,
            ["XSISCHEMAURI=http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        outLayer = outSource.CreateLayer(out, None, ogr.wkbUnknown)

        # get the first feature
        inFeature = inLayer.GetNextFeature()
        inGeometry = inFeature.GetGeometryRef()

        # make the buffer
        buff = inGeometry.Buffer(float(100000))

        # create output feature to the file
        outFeature = ogr.Feature(feature_def=outLayer.GetLayerDefn())
        outFeature.SetGeometryDirectly(buff)
        outLayer.CreateFeature(outFeature)
        outFeature.Destroy()

        response.outputs['output'].data_format = FORMATS.GML
        response.outputs['output'].file = outPath
        return response

    return Process(handler=feature,
                   identifier='feature',
                   title='Process Feature',
                   inputs=[ComplexInput(
                       'input',
                       title='Input',
                       supported_formats=[get_format('GML')])],
                   outputs=[ComplexOutput(
                       'output',
                       title='Output',
                       supported_formats=[get_format('GML')])])


def create_sum_one():

    def sum_one(request, response):
        input = request.inputs['input'][0].file
        # What do we need to assert a Complex input?
        # assert type(input) is text_type

        import grass.script as grass

        # Import the raster and set the region
        if grass.run_command("r.in.gdal", flags="o", out="input",
                             input=input, quiet=True) != 0:
            raise NoApplicableCode("Could not import cost map. "
                                   "Please check the WCS service.")

        if grass.run_command("g.region", flags="a", rast="input") != 0:
            raise NoApplicableCode("Could not set GRASS region.")

        # Add 1
        if grass.mapcalc("$output = $input + $value", output="output",
                         input="input", value=1.0, quiet=True):
            raise NoApplicableCode("Could not use GRASS map calculator.")

        # Export the result
        _, out = tempfile.mkstemp()
        os.environ['GRASS_VERBOSE'] = '-1'
        if grass.run_command("r.out.gdal", flags="f", input="output",
                             type="UInt16", output=out, overwrite=True) != 0:
            raise NoApplicableCode("Could not export result from GRASS.")
        del os.environ['GRASS_VERBOSE']

        response.outputs['output'].file = out
        return response

    return Process(handler=sum_one,
                   identifier='sum_one',
                   title='Process Sum One',
                   inputs=[ComplexInput(
                       'input',
                       title='Input',
                       supported_formats=[Format('image/img')])],
                   outputs=[ComplexOutput(
                       'output',
                       title='Output',
                       supported_formats=[get_format('GEOTIFF')])],
                   grass_location='epsg:4326')


class ExecuteTests(unittest.TestCase):

    def test_wfs(self):
        if not service_ok('https://demo.mapserver.org'):
            self.skipTest("mapserver is unreachable")
        client = client_for(Service(processes=[create_feature()]))
        request_doc = WPS.Execute(
            OWS.Identifier('feature'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('input'),
                    WPS.Reference(
                        {'{http://www.w3.org/1999/xlink}href': wfsResource},
                        mimeType=FORMATS.GML.mime_type,
                        encoding='',
                        schema=''))),
            WPS.ProcessOutputs(
                WPS.Output(
                    OWS.Identifier('output'))),
            version='1.0.0'
        )
        resp = client.post_xml(doc=request_doc)

        assert_response_success(resp)
        # Other things to assert:
        # . the inclusion of output
        # . the type of output

    def test_wcs(self):
        if not config.CONFIG.get('grass', 'gisbase'):
            self.skipTest('GRASS lib not found')
        if not service_ok('https://demo.mapserver.org'):
            self.skipTest("mapserver is unreachable")

        client = client_for(Service(processes=[create_sum_one()]))
        request_doc = WPS.Execute(
            OWS.Identifier('sum_one'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('input'),
                    WPS.Reference(
                        {'{http://www.w3.org/1999/xlink}href': wcsResource}))),
            WPS.ProcessOutputs(
                WPS.Output(
                    OWS.Identifier('output'))),
            version='1.0.0')
        resp = client.post_xml(doc=request_doc)
        assert_response_success(resp)
        # Other things to assert:
        # . the inclusion of output
        # . the type of output


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(ExecuteTests),
    ]
    return unittest.TestSuite(suite_list)
