'''
Created on 10 Mar 2015

@author: desousa
'''
import unittest
import lxml.etree
from pywps import Service, Process, ComplexInput, ComplexOutput
from pywps.app import WPS, OWS
from tests.common import client_for
from osgeo import ogr

# A layer from the MUSIC project - must be replace by something simpler
wfsResource = "http://maps.iguess.list.lu/cgi-bin/mapserv?map=/srv/mapserv/MapFiles/LB_localOWS_test.map&SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature&TYPENAME=LB_building_footprints&MAXFEATURES=10"

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
    
        return response

    return Process(handler=feature,
                   inputs=[ComplexInput('input', mimeType='text/xml')],
                   outputs=[ComplexOutput('output', mimeType='text/xml')])
    
    
class ExecuteTest(unittest.TestCase):

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
        