from flask import Flask

from pywps import configuration


class PyWPSFlask(Flask):
	def __init__(self, import_name):
		self.pywps_processes = None
		self.pywps_wps_service = None

		super(PyWPSFlask, self).__init__(import_name)

	def load_pywps_app(self, processes, configuration_file):
		#store processes in method attribute
		self.pywps_processes = processes
		#WPS service
		from pywps import Service
		self.pywps_wps_service = Service(processes=processes, cfgfiles=[configuration_file])
		#set database connection
		self.config['SQLALCHEMY_DATABASE_URI'] = configuration.get_config_value('server', 'SQLAlchemyDatabaseUri')
		
		return True