import flask
import psutil

from pywps.server.app import application
from pywps.server.app import db

import models


def _get_process_by_uuid(uuid):
	data = models.Request.query.filter(models.Request.uuid == uuid).first()

	if data:
		pid = data.pid

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
	process = _get_process_by_uuid(uuid)

	if process:
		process.terminate()
	else:
		response = {
		'uuid': uuid,
		'error': 'no_process',
		'error_message': 'No process'
		}

		return flask.jsonify(response)

	model_request = models.Request.query.filter(models.Request.uuid == uuid).first()

	response = {
	'uuid': data.uuid,
	'pid': data.pid,
	'time_start': data.time_start,
	'identifier': data.identifier,
	'status': 'stopped'
	}

	return flask.jsonify(response)

@application.route('/processes/pause/<uuid>')
def pywps_process_pause(uuid):
	process = _get_process_by_uuid(uuid)

	if process:
		process.suspend()
	else:
		response = {
		'uuid': uuid,
		'error': 'no_process',
		'error_message': 'No process'
		}

		return flask.jsonify(response)

	request_data = models.Request.query.filter(models.Request.uuid == uuid).first()

	if request_data:
		request_data.message = 'PyWPS: process paused'

		db.session.commit()

		response = {
		'uuid': request_data.uuid,
		'pid': request_data.uuid,
		'time_start': request_data.time_start,
		'identifier': request_data.identifier
		}

	return flask.jsonify(response)

@application.route('/processes/resume/<uuid>')
def pywps_process_resume(uuid):
	process = _get_process_by_uuid(uuid)

	if process:
		process.resume()
	else:
		response = {
		'uuid': uuid,
		'error': 'no_process',
		'error_message': 'No process'
		}

		return flask.jsonify(response)

	request_data = models.Request.query.filter(models.Request.uuid == uuid).first()

	if request_data:
		request_data.message = 'PyWPS: process resumed'

		db.session.commit()

		response = {
		'uuid': request_data.uuid,
		'pid': request_data.pid,
		'time_start': request_data.time_start,
		'identifier': request_data.identifier,
		'status': 'resumed'
		}

	return flask.jsonify(response)

@application.route('/processes')
def wps_processes():
	processes = models.Request.query.all()

	return flask.render_template('processes.html', processes=processes)

@application.route('/create-db')
def create_db():
	db.create_all()
	return 'OK'
