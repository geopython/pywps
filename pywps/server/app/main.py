import flask
import psutil

from flask_sqlalchemy import SQLAlchemy

from pywps.app import Service
from pywps import configuration

import models


application = flask.Flask(__name__, template_folder='templates')
application.config['SQLALCHEMY_DATABASE_URI'] = r'postgresql://pywps_db_user@localhost/pywps'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)


class ServerConnection():
	def __init__(self, processes=None, configuration_file=None):
		#load configuration file
		#configuration.load_configuration(configuration_file)

		#assing Flask application handler
		self.application = application

		#WPS Service
		self.wps_service = Service(processes=processes)

	def _get_process_data_from_db_by_uuid(self, uuid):
		return models.Request.query.filter_by(uuid=uuid).first()

	def _get_process_by_uuid(self, uuid):
		data = self._get_process_data_from_db_by_uuid(uuid)

		if data:
			pid = data[1]

			try:
				process = psutil.Process(pid=pid)
			except psutil.NoSuchProcess:
				print("Error: No such process with {}".format(pid))
				return None
			except psutil.ZombieProcess:
				print("Error: Zombie process")
				return None
			except psutil.AccessDenied:
				print("Error: Access denied")
				return None

			return process
		
		return None

	def run(self):
		@self.application.route('/', methods=['GET', 'POST'])
		def pywps_index():
			return flask.render_template('index.html')

		@self.application.route('/wps', methods=['POST', 'GET'])
		def pywps_wps():
			return self.wps_service

		@self.application.route('/processes/stop/<uuid>')
		def pywps_process_stop(uuid):
			process = self._get_process_by_uuid(uuid)

			if process:
				process.terminate()
			else:
				response = {
					'uuid': uuid,
					'error': 'no_process',
					'error_message': 'No process'
				}

				return flask.jsonify(response)

			data = self._get_process_data_from_db_by_uuid(uuid)

			response = {
				'uuid': data[0],
				'pid': data[1],
				'time_start': data[4],
				'identifier': data[6],
				'status': 'stopped' 
			}

			return flask.jsonify(response)

		@self.application.route('/processes/pause/<uuid>')
		def pywps_process_pause(uuid):
			process = self._get_process_by_uuid(uuid)

			if process:
				process.suspend()
			else:
				response = {
					'uuid': uuid,
					'error': 'no_process',
					'error_message': 'No process'
				}

				return flask.jsonify(response)

			data = self._get_process_data_from_db_by_uuid(uuid)

			response = {
				'uuid': data[0],
				'pid': data[1],
				'time_start': data[4],
				'identifier': data[6],
				'status': 'paused' 
			}

			return flask.jsonify(response)

		@self.application.route('/processes/resume/<uuid>')
		def pywps_process_resume(uuid):
			process = self._get_process_by_uuid(uuid)

			if process:
				process.resume()
			else:
				response = {
					'uuid': uuid,
					'error': 'no_process',
					'error_message': 'No process'
				}

				return flask.jsonify(response)

			data = self._get_process_data_from_db_by_uuid(uuid)

			response = {
				'uuid': data[0],
				'pid': data[1],
				'time_start': data[4],
				'identifier': data[6],
				'status': 'resumed' 
			}

			return flask.jsonify(response)

		@self.application.route('/processes')
		def wps_processes():

			return flask.render_template('processes.html', )

		return self.application
