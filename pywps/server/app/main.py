import psutil
import psycopg2 as postgresql

from flask import Flask

from pywps.app import Service
from pywps import dblog, configuration


class ServerConnection():
	def __init__(self, processes=None, configuration_file=None):
		configuration.load_configuration(configuration_file)
		self.processes = processes
		
		self.application = Flask(__name__)

		self.db_connect = postgresql.connect("dbname= 'pywps' user='janrudolf' password=''")
		self.db_cursor = self.db_connect.cursor()

		self.wps_service = Service(processes=processes)

	def __del__(self):
		self.db_connect.close()

	def get_process_by_uuid(self, uuid):
		sql_query = "SELECT pid FROM pywps_requests WHERE uuid = '{}';".format(uuid)

		self.db_cursor.execute(sql_query)
		
		data = self.db_cursor.fetchone()

		if data:
			pid = data[0]

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
			process = self.get_process_by_uuid(uuid)

			if process:
				process.terminate()
			else:
				return 'No known process with uuid=%s' % uuid

			return 'Proces killed - %s' % uuid

		@self.application.route('/processes/pause/<uuid>')
		def wps_process_pause(uuid):
			process = self.get_process_by_uuid(uuid)

			if process:
				process.suspend()
			else:
				return 'No known process with uuid=%s' % uuid

			return 'Process suspend - %s' % uuid

		@self.application.route('/processes/resume/<uuid>')
		def wps_process_resume(uuid):
			process = self.get_process_by_uuid(uuid)

			if process:
				process.resume()
			else:
				return 'No known process with uuid=%s' % uuid

			return 'Process resume - %s' % uuid

		@self.application.route('/manage') # or /processes
		def wps_manage():
			return 'Manage'

		return self.application

#if __name__ == '__main__':
#	app.run(host='127.0.0.1', port=5005)
