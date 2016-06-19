import flask
import psutil

from pywps.app import Service
from pywps.server import db
from pywps import configuration


class ServerConnection():
	def __init__(self, processes=None, configuration_file=None):
		#load configuration file
		configuration.load_configuration(configuration_file)

		#assing Flask application handler
		self.application = flask.Flask(__name__, template_folder='templates')

		#load DB entries from the configuration files
		db_user = configuration.get_config_value('server', 'dbuser')
		db_password = configuration.get_config_value('server', 'dbpassword')
		db_name = configuration.get_config_value('server', 'dbname')

		#DB connect
		self.db = db.DBPostgreSQL(db_name, db_user, db_password)

		#WPS Service
		self.wps_service = Service(processes=processes)

	def _get_process_data_from_db_by_uuid(self, uuid):
		sql_query = "SELECT uuid, pid, operation, version, time_start, time_end, identifier, message, percent_done, status FROM pywps_requests WHERE uuid = '{}';".format(uuid)

		self.db.execute(sql_query)

		return self.db.fetchone()

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
		@self.application.route('/')
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
			return flask.render_template('processes.html')

		return self.application
