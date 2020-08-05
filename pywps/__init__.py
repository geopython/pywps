##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging

import os

from lxml.builder import ElementMaker

__version__ = '4.2.7'

LOGGER = logging.getLogger('PYWPS')
LOGGER.debug('setting core variables')

PYWPS_INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))

NAMESPACES = {
    'xlink': "http://www.w3.org/1999/xlink",
    'wps': "http://www.opengis.net/wps/{wps_version}",
    'ows': "http://www.opengis.net/ows/{ows_version}",
    'gml': "http://www.opengis.net/gml",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

E = ElementMaker()
namespaces100 = {k: NAMESPACES[k].format(wps_version="1.0.0", ows_version="1.1") for k in NAMESPACES}
namespaces200 = {k: NAMESPACES[k].format(wps_version="2.0", ows_version="2.0") for k in NAMESPACES}


def get_ElementMakerForVersion(version):
    WPS = OWS = None
    if version == "1.0.0":
        WPS = ElementMaker(namespace=namespaces100['wps'], nsmap=namespaces100)
        OWS = ElementMaker(namespace=namespaces100['ows'], nsmap=namespaces100)
    elif version == "2.0.0":
        WPS = ElementMaker(namespace=namespaces200['wps'], nsmap=namespaces200)
        OWS = ElementMaker(namespace=namespaces200['ows'], nsmap=namespaces200)

    return WPS, OWS


def get_version_from_ns(ns):
    if ns == "http://www.opengis.net/wps/1.0.0":
        return "1.0.0"
    elif ns == "http://www.opengis.net/wps/2.0":
        return "2.0.0"
    else:
        return None


OGCTYPE = {
    'measure': 'urn:ogc:def:dataType:OGC:1.1:measure',
    'length': 'urn:ogc:def:dataType:OGC:1.1:length',
    'scale': 'urn:ogc:def:dataType:OGC:1.1:scale',
    'time': 'urn:ogc:def:dataType:OGC:1.1:time',
    'date': 'urn:ogc:def:dataType:OGC:1.1:date',
    'dateTime': 'urn:ogc:def:dataType:OGC:1.1:dateTime',
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
