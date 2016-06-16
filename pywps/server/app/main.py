import psutil
import psycopg2 as postgresql

from flask import Flask

from pywps.app import Service
from pywps import dblog

from pywps import configuration


class ServerConnection():
	def __init__(self, processes=list()):

		self.application = Flask(__name__)

		self.db_cnt = postgresql.connect("dbname= 'pywps' user='janrudolf' password='1Straskov-Vodochody12'")

		self.wps = Service(processes=processes)

	def run(self):
		@self.application.route('/')
		def home():
			return "Home PyWPS"

		@self.application.route('/wps', methods=['POST', 'GET'])
		def wps():
			return self.wps

		@self.application.route('/processes/stop/<process_id>')
		def wps_process_stop(process_id):
			sql_query = "SELECT pid FROM pywps_requests WHERE uuid = '{}';".format(process_id)

			cur = self.db_cnt.cursor()
			cur.execute(sql_query)

			data = cur.fetchone()

			if data:
				pid = data[0]

				try:
					process_p = psutil.Process(pid=pid)

				except psutil.NoSuchProcess:
					#no process with this pid
					print("Error: No such process with {}".format(pid))
				except psutil.ZombieProcess:
					print("Error: Zombie process")
				except psutil.AccessDenied:
					print("Error: Access denied")

				process_p.terminate()

				print('Process {} killed...'.format(pid))

			return 'Proces killed - %s' % process_id

		@self.application.route('/processes/pause/<process_id>')
		def wps_process_pause(process_id):
			"""
			print("ahoj")
			print(process_id)
			sql = "SELECT pid FROM pywps_requests;"
			print(sql)
			
			database = configuration.get_config_value('server', 'logdatabase')
			
			cnt = sqlite3.connect(database)

			cur = cnt.cursor()
			res = cur.execute(sql)

			data = res.fetchall()

			print(data)

			if data:
				pid = data[0]
			
			dblog.close_connection()
			"""

			sql_query = "SELECT pid FROM pywps_requests WHERE uuid = '{}';".format(process_id)

			cur = self.db_cnt.cursor()
			cur.execute(sql_query)

			data = cur.fetchone()

			if data:
				pid = data[0]

				try:
					process_p = psutil.Process(pid=pid)

				except psutil.NoSuchProcess:
					#no process with this pid
					print("Error: No such process with {}".format(pid))
				except psutil.ZombieProcess:
					print("Error: Zombie process")
				except psutil.AccessDenied:
					print("Error: Access denied")

				process_p.suspend()

				print('Process pid={} suspended...'.format(pid))

			return 'Process suspend - %s' % process_id

		@self.application.route('/processes/resume/<process_id>')
		def wps_process_resume(process_id):
			sql_query = "SELECT pid FROM pywps_requests WHERE uuid = '{}';".format(process_id)

			cur = self.db_cnt.cursor()
			cur.execute(sql_query)

			data = cur.fetchone()

			if data:
				pid = data[0]

				try:
					process_p = psutil.Process(pid=pid)

				except psutil.NoSuchProcess:
					#no process with this pid
					print("Error: No such process with {}".format(pid))
				except psutil.ZombieProcess:
					print("Error: Zombie process")
				except psutil.AccessDenied:
					print("Error: Access denied")

				process_p.resume()

				print('Process pid={} resuming...'.format(pid))

			return 'Process resume - %s' % process_id

		@self.application.route('/manage') # or /processes
		def wps_manage():
			return 'Manage'

		return self.application

	def __del__(self):
		self.db_cnt.close()

#if __name__ == '__main__':
#	app.run(host='127.0.0.1', port=5005)
