import psutil
import psycopg2 as postgresql

from flask import Flask

from pywps.app import Service
from pywps import dblog

from pywps import configuration


class ServerConnection():
	def __init__(self, processes=list()):

		self.application = Flask(__name__)

		self.db_cnt = postgresql.connect("dbname= 'pywps' user='janrudolf' password=''")
		self.db_cursor = self.db_cnt.cursor()

		self.wps = Service(processes=processes)

	def __del__(self):
		self.db_cnt.close()

	def get_process_pid(process_id):
		sql_query = "SELECT pid FROM pywps_requests WHERE uuid = '{}';".format(process_id)

		self.db_cursor.execute(sql_query)
		
		data = self.db_cursor.fetchone()

		if data:
			return data[0]
		
		return None

	def run(self):
		@self.application.route('/')
		def home():
			return "Home PyWPS"

		@self.application.route('/wps', methods=['POST', 'GET'])
		def wps():
			return self.wps

		@self.application.route('/processes/stop/<process_id>')
		def wps_process_stop(process_id):
			pid = self.get_process_pid(process_id)

			if pid:
				try:
					process = psutil.Process(pid=pid)
				except psutil.NoSuchProcess:
					print("Error: No such process with {}".format(pid))
				except psutil.ZombieProcess:
					print("Error: Zombie process")
				except psutil.AccessDenied:
					print("Error: Access denied")

				process.terminate()

			return 'Proces killed - %s' % process_id

		@self.application.route('/processes/pause/<process_id>')
		def wps_process_pause(process_id):
			pid = self.get_process_pid(process_id)

			if pid:
				try:
					process = psutil.Process(pid=pid)
				except psutil.NoSuchProcess:
					print("Error: No such process with {}".format(pid))
				except psutil.ZombieProcess:
					print("Error: Zombie process")
				except psutil.AccessDenied:
					print("Error: Access denied")

				process.suspend()

			return 'Process suspend - %s' % process_id

		@self.application.route('/processes/resume/<process_id>')
		def wps_process_resume(process_id):
			pid = self.get_process_pid(process_id)

			if pid:
				try:
					process = psutil.Process(pid=pid)
				except psutil.NoSuchProcess:
					print("Error: No such process with {}".format(pid))
				except psutil.ZombieProcess:
					print("Error: Zombie process")
				except psutil.AccessDenied:
					print("Error: Access denied")

				process.resume()

			return 'Process resume - %s' % process_id

		@self.application.route('/manage') # or /processes
		def wps_manage():
			return 'Manage'

		return self.application

#if __name__ == '__main__':
#	app.run(host='127.0.0.1', port=5005)
