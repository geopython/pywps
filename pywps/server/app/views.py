import flask
import psutil

from pywps.server.app import application
from pywps.server.app import db
from pywps import configuration

import models


def get_process_data_from_db_by_uuid(uuid):
	return models.Request.query.filter_by(uuid=uuid).first()

def get_process_by_uuid(uuid):
	data = get_process_data_from_db_by_uuid(uuid)

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


@application.route('/', methods=['GET', 'POST'])
def pywps_index():
	return flask.render_template('index.html')

@application.route('/wps', methods=['POST', 'GET'])
def pywps_wps():
	return application.pywps_wps_service

@application.route('/processes/stop/<uuid>')
def pywps_process_stop(uuid):
	process = get_process_by_uuid(uuid)

	if process:
		process.terminate()
	else:
		response = {
		'uuid': uuid,
		'error': 'no_process',
		'error_message': 'No process'
		}

		return flask.jsonify(response)

	data = get_process_data_from_db_by_uuid(uuid)

	response = {
	'uuid': data[0],
	'pid': data[1],
	'time_start': data[4],
	'identifier': data[6],
	'status': 'stopped'
	}

	return flask.jsonify(response)

@application.route('/processes/pause/<uuid>')
def pywps_process_pause(uuid):
	process = get_process_by_uuid(uuid)

	if process:
		process.suspend()
	else:
		response = {
		'uuid': uuid,
		'error': 'no_process',
		'error_message': 'No process'
		}

		return flask.jsonify(response)

	data = get_process_data_from_db_by_uuid(uuid)

	response = {
	'uuid': data[0],
	'pid': data[1],
	'time_start': data[4],
	'identifier': data[6],
	'status': 'paused'
	}

	return flask.jsonify(response)

@application.route('/processes/resume/<uuid>')
def pywps_process_resume(uuid):
	process = get_process_by_uuid(uuid)

	if process:
		process.resume()
	else:
		response = {
		'uuid': uuid,
		'error': 'no_process',
		'error_message': 'No process'
		}

		return flask.jsonify(response)

	data = get_process_data_from_db_by_uuid(uuid)

	response = {
	'uuid': data[0],
	'pid': data[1],
	'time_start': data[4],
	'identifier': data[6],
	'status': 'resumed'
	}

	return flask.jsonify(response)

@application.route('/processes')
def wps_processes():
	return flask.render_template('processes.html')

@application.route('/create-db')
def create_db():
	db.create_all()
	return 'OK'
