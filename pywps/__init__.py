##############################################################################
#
# Author:    Alex Morega & Calin Ciociu
#
# License:
#
# Web Processing Service implementation
# Copyright (C) 2015 PyWPS Development Team, represented by Jachym Cepicky
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
##############################################################################

import logging

import os

from lxml.builder import ElementMaker

__version__ = '4.0.0-beta1'

LOGGER = logging.getLogger('PYWPS')
LOGGER.debug('setting core variables')

PYWPS_INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))

NAMESPACES = {
    'xlink': "http://www.w3.org/1999/xlink",
    'wps': "http://www.opengis.net/wps/1.0.0",
    'ows': "http://www.opengis.net/ows/1.1",
    'gml': "http://www.opengis.net/gml",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

E = ElementMaker()
WPS = ElementMaker(namespace=NAMESPACES['wps'], nsmap=NAMESPACES)
OWS = ElementMaker(namespace=NAMESPACES['ows'], nsmap=NAMESPACES)

OGCTYPE = {
    'measure': 'urn:ogc:def:dataType:OGC:1.1:measure',
    'length': 'urn:ogc:def:dataType:OGC:1.1:length',
    'scale': 'urn:ogc:def:dataType:OGC:1.1:scale',
    'time': 'urn:ogc:def:dataType:OGC:1.1:time',
    'gridLength': 'urn:ogc:def:dataType:OGC:1.1:gridLength',
    'angle': 'urn:ogc:def:dataType:OGC:1.1:angle',
    'lengthOrAngle': 'urn:ogc:def:dataType:OGC:1.1:lengthOrAngle',
    'string': 'urn:ogc:def:dataType:OGC:1.1:string',
    'positiveInteger': 'urn:ogc:def:dataType:OGC:1.1:positiveInteger',
    'nonNegativeInteger': 'urn:ogc:def:dataType:OGC:1.1:nonNegativeInteger',
    'boolean': 'urn:ogc:def:dataType:OGC:1.1:boolean',
    'measureList': 'urn:ogc:def:dataType:OGC:1.1:measureList',
    'lengthList': 'urn:ogc:def:dataType:OGC:1.1:lengthList',
    'scaleList': 'urn:ogc:def:dataType:OGC:1.1:scaleList',
    'angleList': 'urn:ogc:def:dataType:OGC:1.1:angleList',
    'timeList': 'urn:ogc:def:dataType:OGC:1.1:timeList',
    'gridLengthList': 'urn:ogc:def:dataType:OGC:1.1:gridLengthList',
    'integerList': 'urn:ogc:def:dataType:OGC:1.1:integerList',
    'positiveIntegerList': 'urn:ogc:def:dataType:OGC:1.1:positiveIntegerList',
    'anyURI': 'urn:ogc:def:dataType:OGC:1.1:anyURI',
    'integer': 'urn:ogc:def:dataType:OGC:1.1:integer',
    'float': 'urn:ogc:def:dataType:OGC:1.1:float'
}

OGCUNIT = {
    'degree': 'urn:ogc:def:uom:OGC:1.0:degree',
    'metre': 'urn:ogc:def:uom:OGC:1.0:metre',
    'unity': 'urn:ogc:def:uom:OGC:1.0:unity'
}

from pywps.app import Process, Service, WPSRequest
from pywps.app.WPSRequest import get_inputs_from_xml, get_output_from_xml
from pywps.inout.inputs import LiteralInput, ComplexInput, BoundingBoxInput
from pywps.inout.outputs import LiteralOutput, ComplexOutput, BoundingBoxOutput
from pywps.inout.formats import Format, FORMATS, get_format
from pywps.inout import UOM

if __name__ == "__main__":
    pass
