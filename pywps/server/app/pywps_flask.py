from flask import Flask

from pywps import configuration


class PyWPSFlask(Flask):
    def __init__(self, import_name):
        self.pywps_processes = None
        self.pywps_service = None

        super(PyWPSFlask, self).__init__(import_name)

    def wsgi_app(self, *args):
        #create database tables if doesnt exist with first request
        from pywps.server.app import db
        db.create_all()

        return super(PyWPSFlask, self).wsgi_app(*args)

    def run_pywps(self, processes=None, configuration_file=None, run_locally=None):
        #bound PyWPS processes
        self.pywps_processes = processes

        #WPS service
        from pywps import Service
        self.pywps_service = Service(processes=processes, cfgfiles=[configuration_file])

        #set database connection
        self.config['SQLALCHEMY_DATABASE_URI'] = configuration.get_config_value('server', 'SQLAlchemyDatabaseUri')

        if run_locally:
            self.run(host='0.0.0.0')
