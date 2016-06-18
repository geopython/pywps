import flask
import psutil
import psycopg2 as postgresql

from pywps.app import Service
from pywps import configuration


class ServerConnection():
	def __init__(self, processes=None, configuration_file=None):
		configuration.load_configuration(configuration_file)
		self.processes = processes

		self.application = flask.Flask(__name__)

		db_user = configuration.get_config_value('server', 'dbuser')
		db_password = configuration.get_config_value('server', 'dbpassword')
		db_name = configuration.get_config_value('server', 'dbname')

		self.db_connect = postgresql.connect("dbname= '{}' user='{}' password='{}'".format(db_name, db_user, db_password))
		self.db_cursor = self.db_connect.cursor()

		self.wps_service = Service(processes=processes)

	def __del__(self):
		self.db_connect.close()

	def _get_process_data_from_db_by_uuid(self, uuid):
		sql_query = "SELECT uuid, pid, operation, version, time_start, time_end, identifier, message, percent_done, status FROM pywps_requests WHERE uuid = '{}';".format(uuid)

		self.db_cursor.execute(sql_query)

		return self.db_cursor.fetchone()

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
		def wps_home():
			return "Home PyWPS"

		@self.application.route('/wps', methods=['POST', 'GET'])
		def wps():
			return self.wps_service

		@self.application.route('/processes/stop/<uuid>')
		def wps_process_stop(uuid):
			process = self._get_process_by_uuid(uuid)

			if process:
				process.terminate()
			else:
				return 'No known process with uuid=%s' % uuid

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
		def wps_process_pause(uuid):
			process = self._get_process_by_uuid(uuid)

			if process:
				process.suspend()
			else:
				return 'No known process with uuid=%s' % uuid

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
		def wps_process_resume(uuid):
			process = self._get_process_by_uuid(uuid)

			if process:
				process.resume()
			else:
				return 'No known process with uuid=%s' % uuid

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
			return 'Processes'

		return self.application
