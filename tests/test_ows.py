'''
Created on 10 Mar 2015

@author: desousa
'''
import unittest
import lxml.etree
import sys
from pywps import Service, Process, ComplexInput, ComplexOutput, Format 
from pywps.exceptions import NoApplicableCode
from pywps.app import WPS, OWS
from tests.common import client_for
from osgeo import ogr

# Layers from the MUSIC project - must be replaced by something simpler
wfsResource = "http://maps.iguess.list.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/LB_localOWS_test.map&SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature&TYPENAME=LB_building_footprints&MAXFEATURES=10"
wcsResource = "http://mapservices-gent.tudor.lu/gent_ows?&SERVICE=WCS&FORMAT=image/img&BBOX=103757,192665,104721,193770&RESX=1.0&RESY=1.0&RESPONSE_CRS=EPSG:31370&CRS=EPSG:31370&VERSION=1.0.0&REQUEST=GetCoverage&COVERAGE=GE_dsm"

# This method already exists in test_execute - think of refactoring
def assert_response_success(resp):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/xml'
    success = resp.xpath_text('/wps:ExecuteResponse'
                              '/wps:Status'
                              '/wps:ProcessSucceeded')
    assert success == "great success"


def create_feature():
    
    def feature(request, response):
        input = request.inputs['input']
        # What do we need to assert a Complex input?
        #assert type(input) is text_type
        
        # open the input file
        try:
            inSource = ogr.Open(input)
        except Exception,e:
            return "Could not open given vector file: %s" % e
        inLayer = inSource.GetLayer()

        # create output file
        out = "output.gml"
        driver = ogr.GetDriverByName('GML')
        outSource = driver.CreateDataSource(out, ["XSISCHEMAURI=http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        outLayer = outSource.CreateLayer(out,None,ogr.wkbUnknown)
        
        # get the first feature
        inFeature = inLayer.GetNextFeature()
        inGeometry = inFeature.GetGeometryRef()

        # create output feature to the file
        outFeature = ogr.Feature(feature_def=outLayer.GetLayerDefn())
        outFeature.SetGeometryDirectly(inGeometry)
        outLayer.CreateFeature(outFeature)
        outFeature.Destroy()

        response.outputs['output'] = out
        return response

    return Process(handler=feature,
                   inputs=[ComplexInput('input', [Format('text/xml')])],
                   outputs=[ComplexOutput('output', [Format('text/xml')])])
    
    
def create_sum_one():
    
    def sum_one(request, response):
        input = request.inputs['input']
        # What do we need to assert a Complex input?
        #assert type(input) is text_type
        
        sys.path.append("/usr/lib/grass64/etc/python/")
        import grass.script as grass

        # Import the raster and set the region
        if grass.run_command("r.in.gdal", flags="o", out="input", input=input) != 0:
            raise NoApplicableCode("Could not import cost map. Please check the WCS service.")
        
        if grass.run_command("g.region", flags="ap", rast="input") != 0:
            raise NoApplicableCode("Could not set GRASS region.")
        
        # Add 1
        if grass.mapcalc("$output = $input + $value", output="output", input="input", value=1.0) != 0:
            raise NoApplicableCode("Could not set GRASS region.")
        
        # Export the result
        out = "./output.tif"
        if grass.run_command("r.out.gdal", input="output", type="Float32", output=out) != 0:
            raise NoApplicableCode("Could not export result from GRASS.")

        response.outputs['output'] = out
        return response

    return Process(handler=sum_one,
                   inputs=[ComplexInput('input', [Format('image/tiff')])],
                   outputs=[ComplexOutput('output', [Format('image/tiff')])])
    
    
class ExecuteTests(unittest.TestCase):

    def test_wfs(self):
        client = client_for(Service(processes=[create_feature()]))
        request_doc = WPS.Execute(
            OWS.Identifier('feature'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('input'),
                    WPS.Data(WPS.ComplexData(wfsResource)))))
        resp = client.post_xml(doc=request_doc)
        assert_response_success(resp)
        # Other things to assert:
        # . the inclusion of output
        # . the type of output
        
    def test_wcs(self):
        client = client_for(Service(processes=[create_sum_one()]))
        request_doc = WPS.Execute(
            OWS.Identifier('sum_one'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('input'),
                    WPS.Data(WPS.ComplexData(wcsResource)))))
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