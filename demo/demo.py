#!/usr/bin/env python

import os,sys
from contextlib import contextmanager
import tempfile
import subprocess
import json
from collections import deque
from uuid import uuid4
from pywps._compat import StringIO
from path import path
import flask
from werkzeug.serving import run_simple
from werkzeug.wsgi import get_path_info, wrap_file

sys.path.append(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.path.pardir))
import pywps
from pywps.formats import FORMATS
from pywps import (Process, Service, WPSResponse, LiteralInput, LiteralOutput,
                   ComplexInput, ComplexOutput, Format, FileReference)
                   ComplexInput, ComplexOutput, Format)


recent_data_files = deque(maxlen=20)


@contextmanager
def temp_dir():
    tmp = path(tempfile.mkdtemp())
    try:
        yield tmp
    finally:
        tmp.rmtree()


def say_hello(request, response):
    response.outputs['response'].value = request.inputs['name'].value
    return response


def feature_count(request, response):
    import lxml.etree
    from pywps.app import xpath_ns
    doc = lxml.etree.parse(request.inputs['layer'])
    feature_elements = xpath_ns(doc, '//gml:featureMember')
    response.outputs['count'] =  str(len(feature_elements))
    return response


def centroids(request, response):
    from shapely.geometry import shape, mapping
    with temp_dir() as tmp:
        input_gml = tmp / 'input.gml'
        input_gml.write_bytes(request.inputs['layer'].stream.read())
        input_geojson = tmp / 'input.geojson'
        subprocess.check_call(['ogr2ogr', '-f', 'geojson',
                               input_geojson, input_gml])
        data = json.loads(input_geojson.text(encoding='utf-8'))
        for feature in data['features']:
            geom = shape(feature['geometry'])
            feature['geometry'] = mapping(geom.centroid)
        out_bytes = json.dumps(data, indent=2)
        response.outputs['out'].output_format = Format(FORMATS['JSON'])
        response.outputs['out'].out_bytes = out_bytes
        return response


def create_app():
    service = Service(processes=[
        Process(say_hello, version='1.3.3.7', inputs=[LiteralInput('name', 'blatitle', data_type='string')],
                outputs=[LiteralOutput('response', 'Response', data_type='string')]),
        Process(feature_count,
                inputs=[ComplexInput('layer', 'Layer', [Format('SHP')])],
                outputs=[ComplexOutput('layer', 'Layer', [Format('GML')])]),
        Process(centroids,
                inputs=[ComplexInput('layer', 'Layer', [Format('GML')])],
                outputs=[ComplexOutput('out', 'Referenced Output', [Format('JSON')])])
    ])
    

    app = flask.Flask(__name__)

    @app.route('/')
    def home():
        url = flask.url_for('wps', _external=True)
        return flask.render_template('home.html', url=url)

    @app.route('/wps', methods=['GET', 'POST'])
    def wps():
        return service

    @app.route(pywps.config.get_config_value('server', 'outputUrl')+'<uuid>')
    def datafile(uuid):
        service.processes
        import pywps.config
        file_path = pywps.config.get_config_value('server', 'outputPath')
        for data_file in os.listdir(file_path):
            if data_file == uuid:
                file_ext = os.path.splitext(data_file)[1]
                file_obj = open(os.path.join(file_path, data_file))
                file_bytes = file_obj.read()
                file_obj.close()
                return flask.Response(file_bytes, mimetype=None)
        else:
            flask.abort(404)

    return app


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('listen', nargs='?', default='localhost:5000')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-w', '--waitress', action='store_true')
    args = parser.parse_args()

    app = create_app()
    app.debug = True #args.debug
    host, port = args.listen.split(':')
    port = int(port)

    if args.waitress:
        import waitress
        waitress.serve(app, host=host, port=port)
    else:
        run_simple(host, port, app, use_reloader=app.debug)


if __name__ == '__main__':
    main()
