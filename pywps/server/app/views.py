# -*- coding: utf-8 -*-
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


@application.route('/processes/<uuid>', methods=['POST', 'PUT', 'DELETE'])
def pywps_processes(uuid):
	process = None
	process_error = None

	model_request = models.Request.query.filter(models.Request.uuid == uuid).first()

	if model_request:
		process, process_error = _get_process(model_request.pid)

		if not process:
			response = {
				'status': model_request.status,
				'time_end': model_request.time_end,
				'error': process_error
			}
			
			return flask.jsonify(response)

		#if flask.request.method == 'GET':
		#	pass

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

		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise
		finally:
			db.session.close()

	response = {
		'status': model_request.status,
		'time_end': model_request.time_end,
		'error': process_error
	}

	return flask.jsonify(response)


@application.route('/processes')
def pywps_processes_page():
	processes = models.Request.query.all()

	return flask.render_template('processes.html', active_page='processes', processes=processes)

@application.route('/processes/table-entries', methods=['POST'])
def pywps_processes_table_entries():
	data = flask.request.get_json()
	#print(data)
	#print(data['status'])

	query = models.Request.query

	if len(data['pid']) > 0:
		query = query.filter(models.Request.pid == int(data['pid']))

	if len(data['uuid']) > 0:
		query = query.filter(models.Request.uuid.like('%{}%'.format(str(data['uuid']))))

	return flask.render_template('processes_table_entries.html', processes=query.all())


@application.route('/create-db')
def create_db():
	db.create_all()

	return 'OK'
