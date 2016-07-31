# -*- coding: utf-8 -*-
import flask
import sqlalchemy
import psutil

from pywps.constants import wps_response_status
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
	db.create_all()

	return flask.render_template('index.html', active_page='home')


@application.route('/wps', methods=['POST', 'GET'])
def pywps_wps():
	return application.pywps_service


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

		if flask.request.method == 'POST':
			#pause process
			process.suspend()

			model_request.status = wps_response_status.PAUSED_STATUS #status PAUSED running in WPSResponse.py

		if flask.request.method == 'PUT':
			#resume process
			process.resume()

			model_request.status = 2 #status STORE_AND_UPDATE_STATUS running in WPSResponse.py

		if flask.request.method == 'DELETE':
			#stop process
			process.terminate()

			model_request.status = wps_response_status.STOPPED_STATUS #status STOPPED in WPSResponse.py

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


@application.route('/manage')
def pywps_processes_page():
	processes = models.Request.query.order_by(models.Request.time_start)

	filter_identifiers = db.session.query(models.Request.identifier.distinct().label('identifier')).all()
	filter_identifiers = [filter_identifier.identifier for filter_identifier in filter_identifiers]

	return flask.render_template('processes.html', active_page='processes', processes=processes, filter_identifiers=filter_identifiers, wps_response_status=wps_response_status)

@application.route('/processes/table-entries', methods=['POST'])
def pywps_processes_table_entries():
	error = False

	data = flask.request.get_json()

	query = models.Request.query

	data_status = str(data['status']) if str(data['status']) != 'none' else False
	data_operation = str(data['operation']) if str(data['operation']) != '0' else False
	data_identifier = str(data['identifier']) if str(data['identifier']) != '0' else False
	try:
		data_pid = int(data['pid'])
	except:
		data_pid = 0 if (len(str(data['pid'])) > 0) else None

	data_uuid = str(data['uuid'])

	if not error and data_status:

		if data_status == "running":
			query = query.filter(
				sqlalchemy.or_(
					models.Request.status == str(wps_response_status.STORE_AND_UPDATE_STATUS), models.Request.status == str(wps_response_status.STORE_STATUS)
				)
			)
		elif data_status == "paused":
			query = query.filter(models.Request.status == str(wps_response_status.PAUSED_STATUS))
		elif data_status == "stopped":
			query = query.filter(models.Request.status == str(wps_response_status.STOPPED_STATUS))
		elif data_status == "finished":
			query = query.filter(models.Request.status == str(wps_response_status.DONE_STATUS))

	if not error and  data_operation:
		query = query.filter(models.Request.operation == data_operation)

	if not error and  data_identifier:
		query = query.filter(models.Request.identifier == data_identifier)

	if not error and data_pid != None:
		query = query.filter(models.Request.pid == data_pid)

	if not error and len(data_uuid) > 0:
		query = query.filter(models.Request.uuid.like('%{}%'.format(data_uuid)))

	query = query.order_by(models.Request.time_start)

	return flask.render_template('processes_table_entries.html', processes=query, wps_response_status=wps_response_status)
