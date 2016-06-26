from flask import Flask

from pywps.app import Service
from pywps import configuration


class PyWPSFlask(Flask):
	def __init__(self, import_name):
		self.pywps_processes = None
		self.pywps_wps_service = None

		super(PyWPSFlask, self).__init__(import_name)

	def load_pywps_app(self, processes, configuration_file):
		#load configuration file
		configuration.load_configuration(configuration_file)
		#store processes in method attribute
		self.pywps_processes = processes
		#WPS service
		self.pywps_wps_service = Service(processes=processes)
		#set database connection
		self.config['SQLALCHEMY_DATABASE_URI'] = configuration.get_config_value('server', 'SQLAlchemyDatabaseUri')
		
		return True