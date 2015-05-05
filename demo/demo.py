#!/usr/bin/env python

import os,sys
from contextlib import contextmanager
import tempfile
import subprocess
import json
from path import path
import flask
from werkzeug.serving import run_simple

sys.path.append(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.path.pardir))
import pywps
from pywps.formats import FORMATS
from pywps import (Process, Service, LiteralInput, LiteralOutput,
                   ComplexInput, ComplexOutput, Format)

@contextmanager
def temp_dir():
    tmp = path(tempfile.mkdtemp())
    try:
        yield tmp
    finally:
        tmp.rmtree()


def sleep(request, response):
    import time

    sleep_delay = request.inputs['delay'].data
    if sleep_delay:
        sleep_delay = float(sleep_delay)
    else:
        sleep_delay = 10

    time.sleep(sleep_delay)
    response.update_status('PyWPS Process started. Waiting...', 20)
    time.sleep(sleep_delay)
    response.update_status('PyWPS Process started. Waiting...', 40)
    time.sleep(sleep_delay)
    response.update_status('PyWPS Process started. Waiting...', 60)
    time.sleep(sleep_delay)
    response.update_status('PyWPS Process started. Waiting...', 80)
    time.sleep(sleep_delay)
    response.outputs['sleep_output'].data = 'done sleeping'

    return response


def ultimate_question(request, response):
    response.outputs['outvalue'].data = '42'
    return response


def say_hello(request, response):
    response.outputs['response'].data = 'Hello ' + request.inputs['name'].data
    return response


def feature_count(request, response):
    import lxml.etree
    from pywps.app import xpath_ns
    doc = lxml.etree.parse(request.inputs['layer'])
    feature_elements = xpath_ns(doc, '//gml:featureMember')
    response.outputs['count'] = str(len(feature_elements))
    return response


def centroids(request, response):
    from shapely.geometry import shape, mapping
    with temp_dir() as tmp:
        input_gml = request.inputs['layer'].file
        input_geojson = tmp / 'input.geojson'
        subprocess.check_call(['ogr2ogr', '-f', 'geojson',
                               input_geojson, input_gml])
        data = json.loads(input_geojson.text(encoding='utf-8'))
        for feature in data['features']:
            geom = shape(feature['geometry'])
            feature['geometry'] = mapping(geom.centroid)
        out_bytes = json.dumps(data, indent=2)
        response.outputs['out'].output_format = Format(FORMATS['JSON'])
        response.outputs['out'].data = out_bytes
        return response


def create_app():
    from pywps.config import PyWPSConfig
    pywps.app.config = PyWPSConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pywps.cfg"))
    output_url = pywps.app.config.get_config_value('server', 'outputUrl')
    output_path = pywps.app.config.get_config_value('server', 'outputPath')
    temp_path = pywps.app.config.get_config_value('server', 'tempPath')
    # check if in the configuration file specified directories can be created/written to
    try:
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        if not os.path.exists(output_path):
            os.makedirs(output_path)
    except OSError as e:
        from pywps.exceptions import NoApplicableCode

        print e
        exit(1)

    service = Service(processes=[
        Process(say_hello, version='1.3.3.7', inputs=[LiteralInput('name', data_type='string')],
                outputs=[LiteralOutput('response', data_type='string')],
                store_supported=True,
                status_supported=True),
        Process(feature_count,
                inputs=[ComplexInput('layer', 'Layer', [Format('SHP')])],
                outputs=[ComplexOutput('layer', 'Layer', [Format('GML')])]),
        Process(centroids,
                inputs=[ComplexInput('layer', 'Layer', [Format('GML')])],
                outputs=[ComplexOutput('out', 'Referenced Output', [Format('JSON')])],
                store_supported=True,
                status_supported=True),
        Process(ultimate_question,
                outputs=[LiteralOutput('outvalue', 'Output Value', data_type='string')]),
        Process(sleep,
                inputs=[LiteralInput('delay', 'Delay between every update', data_type='float')],
                outputs=[LiteralOutput('sleep_output', 'Sleep Output', data_type='string')],
                store_supported=True,
                status_supported=True
                )
    ])

    app = flask.Flask(__name__)

    @app.route('/')
    def home():
        url = flask.url_for('wps', _external=True)
        return flask.render_template('home.html', url=url)

    @app.route('/wps', methods=['GET', 'POST'])
    def wps():
        return service

    @app.route(output_url+'<uuid>')
    def datafile(uuid):
        for data_file in os.listdir(output_path):
            if data_file == uuid:
                file_ext = os.path.splitext(data_file)[1]
                file_obj = open(os.path.join(output_path, data_file))
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
