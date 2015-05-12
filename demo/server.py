import json
import os
import flask
import subprocess
from processes.ultimate_question import UltimateQuestion
from processes.sleep import Sleep
from pywps import Service, Process, ComplexInput, Format, ComplexOutput, FORMATS, LiteralOutput, LiteralInput
from pywps.wpsserver import PyWPSServerAbstract, temp_dir
from pywps import config


def centroids(request, response):
    # ogr2ogr requires gdal-bin
    from shapely.geometry import shape, mapping
    with temp_dir() as tmp:
        input_gml = request.inputs['layer'].file
        input_geojson = os.path.join(tmp, 'input.geojson')
        subprocess.check_call(['ogr2ogr', '-f', 'geojson',
                               input_geojson, input_gml])
        data = json.loads(input_geojson.read_file('r'))
        for feature in data['features']:
            geom = shape(feature['geometry'])
            feature['geometry'] = mapping(geom.centroid)
        out_bytes = json.dumps(data, indent=2)
        response.outputs['out'].output_format = Format(FORMATS['JSON'])
        response.outputs['out'].data = out_bytes
        return response


def feature_count(request, response):
    import lxml.etree
    from pywps.app import xpath_ns
    doc = lxml.etree.parse(request.inputs['layer'])
    feature_elements = xpath_ns(doc, '//gml:featureMember')
    response.outputs['count'] = str(len(feature_elements))
    return response


def say_hello(request, response):
    response.outputs['response'].data = 'Hello ' + request.inputs['name'].data
    return response


class Server(PyWPSServerAbstract):
    def __init__(self, host='localhost', port='5000', debug=False, processes=[], config_file=None):
        self.app = flask.Flask(__name__)
        self.host = host
        self.port = port
        self.debug = debug

        # Load config files and override settings if any file specified
        if config_file:
            config.load_configuration(config_file)

        self.output_url = config.get_config_value('server', 'outputUrl')
        self.output_path = config.get_config_value('server', 'outputPath')
        self.temp_path = config.get_config_value('server', 'tempPath')
        self.host = config.get_config_value('wps', 'serveraddress').split('://')[1]
        self.port = int(config.get_config_value('wps', 'serverport'))

        self.processes = [
            Process(say_hello,
                    version='1.3.3.7',
                    inputs=[LiteralInput('name', data_type='string')],
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
            UltimateQuestion(),
            Sleep()
        ]

        # if any processes have been passed then prioritize these
        if processes:
            self.processes = processes

        self.service = Service(processes=self.processes)

    def run(self):
        @self.app.route('/')
        def index():
            url = flask.url_for('Server:wps', _external=True)
            return flask.render_template('home.html', url=url)

        @self.app.route('/wps', methods=['GET', 'POST'])
        def wps():
            return self.service

        @self.app.route(self.output_url+'<uuid>')
        def datafile(uuid):
            for data_file in os.listdir(self.output_path):
                if data_file == uuid:
                    file_ext = os.path.splitext(data_file)[1]
                    file_obj = open(os.path.join(self.output_path, data_file))
                    file_bytes = file_obj.read()
                    file_obj.close()
                    mime_type = None
                    if 'xml' in file_ext:
                        mime_type = 'text/xml'
                    return flask.Response(file_bytes, content_type=mime_type)
            else:
                flask.abort(404)

        self.app.run(host=self.host, port=self.port, debug=self.debug)