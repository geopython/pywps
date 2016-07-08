import flask
import psutil

from pywps.server.app import application, db

import models


def _get_process(pid):
	try:
		process = psutil.Process(pid=pid)
	except psutil.NoSuchProcess:
		return (None, 'No Such Process')
	except psutil.ZombieProcess:
		return (None, 'Zombie Process')
	except psutil.AccessDenied:
		return (None, 'Access Denied')
	return (process, None)


@application.route('/', methods=['GET'])
def pywps_index():
	return flask.render_template('index.html', active_page='home')


@application.route('/wps', methods=['POST', 'GET'])
def pywps_wps():
	return application.pywps_wps_service


@application.route('/processes/<uuid>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def pywps_processes(uuid):
	process = None
	process_error = None

	model_request = models.Request.query.filter(models.Request.uuid == uuid).first()

	if model_request:
		process, process_error = _get_process(model_request.pid)

		if not process:
			return 'NOT OK - {}'.format(process_error)

		if flask.request.method == 'GET':
			pass

		if flask.request.method == 'POST':
			#pause process
			process.suspend()

			model_request.status = 4 #status PAUSED running in WPSResponse.py

		if flask.request.method == 'PUT':
			#resume process
			process.resume()

			model_request.status = 2 #status STORE_AND_UPDATE_STATUS running in WPSResponse.py

		if flask.request.method == 'DELETE':
			#stop process
			process.terminate()

			model_request.status = 5 #status STOPPED in WPSResponse.py

		db.session.commit()

	response = {
		'status': model_request.status,
		'time_end': model_request.time_end,
		'error': process_error
	}

	return flask.jsonify(response)

#@application.route('/processes/stop/<uuid>')
#def pywps_process_stop(uuid):
#	process = _get_process_by_uuid(uuid)
#
#	if process:
#		process.terminate()
#	else:
#		response = {
#		'uuid': uuid,
#		'error': 'no_process',
#		'error_message': 'No process'
#		}
#
#		return flask.jsonify(response)
#
#	model_request = models.Request.query.filter(models.Request.uuid == uuid).first()
#
#	response = {
#	'uuid': data.uuid,
#	'pid': data.pid,
#	'time_start': data.time_start,
#	'identifier': data.identifier,
#	'status': 'stopped'
#	}
#
#	return flask.jsonify(response)
#
#@application.route('/processes/pause/<uuid>')
#def pywps_process_pause(uuid):
#	process = _get_process_by_uuid(uuid)
#
#	if process:
#		process.suspend()
#	else:
#		response = {
#		'uuid': uuid,
#		'error': 'no_process',
#		'error_message': 'No process'
#		}
#
#		return flask.jsonify(response)
#
#	request_data = models.Request.query.filter(models.Request.uuid == uuid).first()
#
#	if request_data:
#		request_data.message = 'PyWPS: process paused'
#
#		db.session.commit()
#
#		response = {
#		'uuid': request_data.uuid,
#		'pid': request_data.uuid,
#		'time_start': request_data.time_start,
#		'identifier': request_data.identifier
#		}
#
#	return flask.jsonify(response)
#
#@application.route('/processes/resume/<uuid>')
#def pywps_process_resume(uuid):
#	process = _get_process_by_uuid(uuid)
#
#	if process:
#		process.resume()
#	else:
#		response = {
#		'uuid': uuid,
#		'error': 'no_process',
#		'error_message': 'No process'
#		}
#
#		return flask.jsonify(response)
#
#	request_data = models.Request.query.filter(models.Request.uuid == uuid).first()
#
#	if request_data:
#		request_data.message = 'PyWPS: process resumed'
#
#		db.session.commit()
#
#		response = {
#		'uuid': request_data.uuid,
#		'pid': request_data.pid,
#		'time_start': request_data.time_start,
#		'identifier': request_data.identifier,
#		'status': 'resumed'
#		}
#
#	return flask.jsonify(response)

@application.route('/processes')
def pywps_processes_page():
	processes = models.Request.query.all()

	return flask.render_template('processes.html', active_page='processes', processes=processes)


@application.route('/create-db')
def create_db():
	db.create_all()

	return 'OK'
