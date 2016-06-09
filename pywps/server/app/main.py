from flask import Flask

from pywps.app import Service


class ServerConnection():
	def __init__(self, processes=list()):

		self.application = Flask(__name__)

		self.wps = Service(processes=processes)

	def run(self):
		@self.application.route('/')
		def home():
			return "Home PyWPS"

		@self.application.route('/wps')
		def wps():
			return self.wps

		@self.application.route('/process/stop/<process_id>')
		def wps_process_stop(process_id):
			return 'Proces stop %s' % process_id

		@self.application.route('/process/pause/<process_id>')
		def wps_process_pause(process_id):
			return 'Process pause %s' % process_id

		@self.application.route('/process/resume/<process_id>')
		def wps_process_resume(process_id):
			return 'Process resume %s' % process_id

		@self.application.route('/manage')
		def wps_manage():
			return 'Manage'

		return self.application

#if __name__ == '__main__':
#	app.run(host='127.0.0.1', port=5005)
