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
import flask
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
        url = flask.url_for('datafile', uuid=data_file['uuid'], _external=True)
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

    app = flask.Flask(__name__)

    @app.route('/')
    def home():
        url = flask.url_for('wps', _external=True)
        return DESCRIPTION_HTML.format(url=url)

    @app.route('/wps', methods=['GET', 'POST'])
    def wps():
        return service

    @app.route('/datafile/<uuid>')
    def datafile(uuid):
        for data_file in recent_data_files:
            if data_file['uuid'] == uuid:
                return flask.Response(data_file['bytes'])
        else:
            flask.abort(404)

    return app


DESCRIPTION_HTML = """\
<!doctype html>
<h1>PyWPS-4 demo app</h1>
<p>This is a demo WPS server. It exposes a few processes: say_hello,
feature_count, and centroids. Connect to <tt>{url}</tt>.</p>
<p>Source code and issue tracking
at <a href="https://github.com/jachym/pywps-4/"
>github.com/jachym/pywps-4</a>.</p>
"""


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('DEBUG') == 'on'
    run_simple('0.0.0.0', port, app, use_reloader=debug)
