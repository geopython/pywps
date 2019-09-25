"""Test embedding different file formats and different encodings within the <Data> tag."""

import unittest
import os
from pywps import get_ElementMakerForVersion, E
from pywps.app.basic import get_xpath_ns
from pywps import Service, Process, ComplexInput, ComplexOutput, FORMATS
from pywps.tests import client_for, assert_response_success
from owslib.wps import WPSExecution, ComplexDataInput
from lxml import etree

VERSION = "1.0.0"
WPS, OWS = get_ElementMakerForVersion(VERSION)
xpath_ns = get_xpath_ns(VERSION)


def get_resource(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', path)


test_fmts = {'json': (get_resource('json/point.geojson'), FORMATS.JSON),
             'geojson': (get_resource('json/point.geojson'), FORMATS.GEOJSON),
             'netcdf': (get_resource('netcdf/time.nc'), FORMATS.NETCDF),
             'geotiff': (get_resource('geotiff/dem.tiff'), FORMATS.GEOTIFF),
             'gml': (get_resource('gml/point.gml'), FORMATS.GML),
             'shp': (get_resource('shp/point.shp.zip'), FORMATS.SHP),
             'txt': (get_resource('text/unsafe.txt'), FORMATS.TEXT),
             }


def create_fmt_process(name, fn, fmt):
    """Create a dummy process comparing the input file on disk and the data that was passed in the request."""
    def handler(request, response):
        # Load output from file and convert to data
        response.outputs['complex'].file = fn
        o = response.outputs['complex'].data

        # Get input data from the request
        i = request.inputs['complex'][0].data

        assert i == o
        return response

    return Process(handler=handler,
                   identifier='test-fmt',
                   title='Complex fmt test process',
                   inputs=[ComplexInput('complex', 'Complex input',
                                        supported_formats=(fmt, ))],
                   outputs=[ComplexOutput('complex', 'Complex output',
                                          supported_formats=(fmt, ))])


def get_data(fn, encoding=None):
    """Read the data from file and encode."""
    import base64
    mode = 'rb' if encoding == 'base64' else 'r'
    with open(fn, mode) as fp:
        data = fp.read()

    if encoding == 'base64':
        data = base64.b64encode(data)

    if isinstance(data, bytes):
        return data.decode('utf-8')
    else:
        return data


class RawInput(unittest.TestCase):

    def make_request(self, name, fn, fmt):
        """Create XML request embedding encoded data."""
        data = get_data(fn, fmt.encoding)

        doc = WPS.Execute(
            OWS.Identifier('test-fmt'),
            WPS.DataInputs(
                WPS.Input(
                    OWS.Identifier('complex'),
                    WPS.Data(
                        WPS.ComplexData(data, mimeType=fmt.mime_type, encoding=fmt.encoding)))),
            version='1.0.0')

        return doc

    def compare_io(self, name, fn, fmt):
        """Start the dummy process, post the request and check the response matches the input data."""

        # Note that `WPSRequest` calls `get_inputs_from_xml` which converts base64 input to bytes
        # See `_get_rawvalue_value`
        client = client_for(Service(processes=[create_fmt_process(name, fn, fmt)]))
        data = get_data(fn, fmt.encoding)

        wps = WPSExecution()
        doc = wps.buildRequest('test-fmt',
                               inputs=[('complex', ComplexDataInput(data, mimeType=fmt.mime_type,
                                                                    encoding=fmt.encoding))],
                               mode='sync')
        resp = client.post_xml(doc=doc)
        assert_response_success(resp)
        wps.parseResponse(resp.xml)
        out = wps.processOutputs[0].data[0]

        if 'gml' in fmt.mime_type:
            xml_orig = etree.tostring(etree.fromstring(data.encode('utf-8'))).decode('utf-8')
            xml_out = etree.tostring(etree.fromstring(out.decode('utf-8'))).decode('utf-8')
            # Not equal because the output includes additional namespaces compared to the origin.
            # self.assertEqual(xml_out, xml_orig)

        else:
            self.assertEqual(out.strip(), data.strip())

    def test_json(self):
        key = 'json'
        self.compare_io(key, *test_fmts[key])

    def test_geojson(self):
        key = 'geojson'
        self.compare_io(key, *test_fmts[key])

    def test_geotiff(self):
        key = 'geotiff'
        self.compare_io(key, *test_fmts[key])

    def test_netcdf(self):
        key = 'netcdf'
        self.compare_io(key, *test_fmts[key])

    def test_gml(self):
        key = 'gml'
        self.compare_io(key, *test_fmts[key])

    def test_shp(self):
        key = 'shp'
        self.compare_io(key, *test_fmts[key])

    def test_txt(self):
        key = 'txt'
        self.compare_io(key, *test_fmts[key])
