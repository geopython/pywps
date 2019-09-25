###############################################################################
#
# Copyright (C) 2014-2016 PyWPS Development Team, represented by
# PyWPS Project Steering Committee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
###############################################################################

__author__ = 'Jachym Cepicky'

from pywps import Process, LiteralInput, ComplexOutput, ComplexInput, Format
from pywps.app.Common import Metadata
from pywps.validator.mode import MODE
from pywps.inout.formats import FORMATS
from pywps.response.status import WPS_STATUS

inpt_vector = ComplexInput(
    'vector',
    'Vector map',
    supported_formats=[Format('application/gml+xml')],
    mode=MODE.STRICT
)

inpt_size = LiteralInput('size', 'Buffer size', data_type='float')

out_output = ComplexOutput(
    'output',
    'HelloWorld Output',
    supported_formats=[Format('application/gml+xml')]
)

inputs = [inpt_vector, inpt_size]
outputs = [out_output]


class DemoBuffer(Process):
    def __init__(self):

        super(DemoBuffer, self).__init__(
            _handler,
            identifier='demobuffer',
            version='1.0.0',
            title='Buffer',
            abstract='This process demonstrates, how to create any process in PyWPS environment',
            metadata=[Metadata('process metadata 1', 'http://example.org/1'),
                      Metadata('process metadata 2', 'http://example.org/2')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )


@staticmethod
def _handler(request, response):
    """Handler method - this method obtains request object and response
    object and creates the buffer
    """

    from osgeo import ogr

    # obtaining input with identifier 'vector' as file name
    input_file = request.inputs['vector'][0].file

    # obtaining input with identifier 'size' as data directly
    size = request.inputs['size'][0].data

    # open file the "gdal way"
    input_source = ogr.Open(input_file)
    input_layer = input_source.GetLayer()
    layer_name = input_layer.GetName()

    # create output file
    driver = ogr.GetDriverByName('GML')
    output_source = driver.CreateDataSource(
        layer_name,
        ["XSISCHEMAURI=http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
    output_layer = output_source.CreateLayer(layer_name, None, ogr.wkbUnknown)

    # get feature count
    count = input_layer.GetFeatureCount()
    index = 0

    # make buffer for each feature
    while index < count:

        response._update_status(WPS_STATUS.STARTED, 'Buffering feature {}'.format(index), float(index) / count)

        # get the geometry
        input_feature = input_layer.GetNextFeature()
        input_geometry = input_feature.GetGeometryRef()

        # make the buffer
        buffer_geometry = input_geometry.Buffer(float(size))

        # create output feature to the file
        output_feature = ogr.Feature(feature_def=output_layer.GetLayerDefn())
        output_feature.SetGeometryDirectly(buffer_geometry)
        output_layer.CreateFeature(output_feature)
        output_feature.Destroy()
        index += 1

    # set output format
    response.outputs['output'].data_format = FORMATS.GML

    # set output data as file name
    response.outputs['output'].file = layer_name

    return response
