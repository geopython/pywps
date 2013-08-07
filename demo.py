#!/usr/bin/env python

import os
from contextlib import contextmanager
import tempfile
import subprocess
import json
from collections import deque
from uuid import uuid4
from StringIO import StringIO
from path import path
from werkzeug.serving import run_simple
from werkzeug.wsgi import get_path_info, wrap_file
from pywps.app import (Process, Service, WPSResponse, LiteralInput,
                       ComplexInput, Format, FileReference)


recent_data_files = deque(maxlen=20)


@contextmanager
def temp_dir():
    tmp = path(tempfile.mkdtemp())
    try:
        yield tmp
    finally:
        tmp.rmtree()


def say_hello(request):
    return WPSResponse({'message': "Hello %s!" % request.inputs['name']})


def feature_count(request):
    import lxml.etree
    from pywps.app import xpath_ns
    doc = lxml.etree.parse(request.inputs['layer'])
    feature_elements = xpath_ns(doc, '//gml:featureMember')
    return WPSResponse({'count': str(len(feature_elements))})


def centroids(request):
    from shapely.geometry import shape, mapping
    with temp_dir() as tmp:
        input_gml = tmp / 'input.gml'
        input_gml.write_bytes(request.inputs['layer'].read().encode('utf-8'))
        input_geojson = tmp / 'input.geojson'
        subprocess.check_call(['ogr2ogr', '-f', 'geojson',
                               input_geojson, input_gml])
        data = json.loads(input_geojson.text(encoding='utf-8'))
        for feature in data['features']:
            geom = shape(feature['geometry'])
            feature['geometry'] = mapping(geom.centroid)
        out_bytes = json.dumps(data, indent=2)
        data_file = {
            'uuid': str(uuid4()),
            'bytes': out_bytes,
            'mime-type': 'application/json',
        }
        recent_data_files.append(data_file)
        url = (request.http_request.base_url.rstrip('/') +
               '/datafile/' + data_file['uuid'])
        reference = FileReference(url, data_file['mime-type'])
        return WPSResponse({'centroids_layer': reference})


def create_app():
    service = Service(processes=[
        Process(say_hello, inputs=[LiteralInput('name', 'string')]),
        Process(feature_count,
                inputs=[ComplexInput('layer', [Format('text/xml')])]),
        Process(centroids,
                inputs=[ComplexInput('layer', [Format('text/xml')])]),
    ])

    def serve_data_files(environ, start_response):
        cleaned_path = get_path_info(environ).strip('/')
        print(cleaned_path)
        if cleaned_path.startswith('datafile/'):
            requested_uuid = cleaned_path.split('/', 1)[1]
            for data_file in recent_data_files:
                if data_file['uuid'] == requested_uuid:
                    start_response('200 OK', [])
                    return wrap_file(environ, StringIO(data_file['bytes']))
        return service(environ, start_response)

    return serve_data_files


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('DEBUG') == 'on'
    run_simple('0.0.0.0', port, app, use_reloader=debug)
