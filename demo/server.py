import json
import os
import flask
import subprocess
#from ultimate_question import UltimateQuestion
from processes.ultimate_question import UltimateQuestion
from processes.sleep import Sleep
from pywps import Service, Process, ComplexInput, Format, ComplexOutput, FORMATS
from pywps.wpsserver import PyWPSServerAbstract, temp_dir
from pywps import config


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


class Server(PyWPSServerAbstract):

    def __init__(self, config_file):
        config.load_configuration(config_file)
        self.output_url = config.get_config_value('server', 'outputUrl')
        self.output_path = config.get_config_value('server', 'outputPath')
        self.temp_path = config.get_config_value('server', 'tempPath')
        self.host = config.get_config_value('wps', 'serveraddress').split('://')[1]
        self.port = int(config.get_config_value('wps', 'serverport'))
        self.processes = [
            Process(centroids,
                    inputs=[ComplexInput('layer', 'Layer', [Format('GML')])],
                    outputs=[ComplexOutput('out', 'Referenced Output', [Format('JSON')])],
                    store_supported=True,
                    status_supported=True),
            UltimateQuestion(),
            Sleep()
        ]
        self.service = Service(processes=self.processes)

    def run(self):
        app = flask.Flask(__name__)

        @app.route('/')
        def index():
            url = flask.url_for('Server:wps', _external=True)
            return flask.render_template('home.html', url=url)

        @app.route('/wps', methods=['GET', 'POST'])
        def wps():
            return self.service

        @app.route(self.output_url+'<uuid>')
        def datafile(uuid):
            for data_file in os.listdir(self.output_path):
                if data_file == uuid:
                    file_ext = os.path.splitext(data_file)[1]
                    file_obj = open(os.path.join(self.output_path, data_file))
                    file_bytes = file_obj.read()
                    file_obj.close()
                    return flask.Response(file_bytes, mimetype=None)
            else:
                flask.abort(404)

        app.run(host=self.host, port=self.port, debug=None)