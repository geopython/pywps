from flask import Flask

from pywps.app import Service
from pywps import configuration


class MyFlask(Flask):
	def __init__(self, import_name):
		self.pywps_processes = None
		self.pywps_wps_service = None

		super(MyFlask, self).__init__(import_name)

	def say_hello(self):
		print("hello from MyFlask2")
		return True

	def load_pywps_app(self, processes, configuration_file):
		#load configuration file
		configuration.load_configuration(configuration_file)
		#store processes in method
		self.pywps_processes = processes
		#WPS service
		self.pywps_wps_service = Service(processes=processes)

		return True