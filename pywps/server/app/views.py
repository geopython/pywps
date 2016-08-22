# -*- coding: utf-8 -*-
import flask
import sqlalchemy
import psutil
import json

from pywps.constants import wps_response_status
from pywps.server.app import application, db

import models


def _get_process(pid):
    try:
        return (psutil.Process(pid=pid), None)
    except psutil.NoSuchProcess:
        return (None, 'No Such Process',)
    except psutil.ZombieProcess:
        return (None, 'Zombie Process')
    except psutil.AccessDenied:
        return (None, 'Access Denied')

def _pause_process(process, model_wps_request):
    process.suspend()

    model_wps_request.status = wps_response_status.PAUSED_STATUS

def _stop_process(process, model_wps_request):
    process.terminate()

    model_wps_request.status = wps_response_status.STOPPED_STATUS

def _resume_process(process, model_wps_request):
    process.resume()

    model_wps_request.status = wps_response_status.STORE_AND_UPDATE_STATUS

def _db_commit():
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise
    finally:
        db.session.close()

        return True


@application.route('/', methods=['GET'])
def pywps_index():
    return flask.render_template('index.html', active_page='home')


@application.route('/wps', methods=['POST', 'GET'])
def pywps_wps():
    return application.pywps_service


@application.route('/processes', methods=['GET'])
def pywps_processes():
    model_wps_requests = models.Request.query.filter(
        sqlalchemy.or_(
            models.Request.status == str(wps_response_status.STORE_AND_UPDATE_STATUS),
            models.Request.status == str(wps_response_status.STORE_STATUS)
        )
    )

    running_processes = []

    for model_wps_request in model_wps_requests:
        running_processes.append(
            {
                "uuid": model_wps_request.uuid
            }
        )

    return flask.jsonify({'processes': running_processes})


@application.route('/processes/<uuid>', methods=['GET', 'PUT', 'DELETE'])
def pywps_processes_uuid(uuid):
    model_wps_request = models.Request.query.filter(models.Request.uuid == str(uuid)).first()

    if not model_wps_request:
        response = {
            'success': False,
            'error': 'Invalid UUID'
        }

        return flask.jsonify(response)

    process, process_error = _get_process(model_wps_request.pid)

    if flask.request.method == 'GET':
        response = {
            'success': True,
            'status': model_wps_request.status,
            'message': model_wps_request.message
        }

        return flask.jsonify(response)

    if process_error is not None:
        response = {
            'success': False,
            'error': process_error
        }

        return flask.jsonify(response)

    if flask.request.method == 'PUT':
        data = json.loads(flask.request.data)

        if 'action' in data and data['action'] == 'pause':
            _pause_process(process, model_wps_request)

        elif 'action' in data and data['action'] == 'resume':
            _resume_process(process, model_wps_request)
        else:
            response = {
                'success': False,
                'error': 'Unknown action'
            }

            return flask.jsonify(response)

    if flask.request.method == 'DELETE':
        _stop_process(process, model_wps_request)

    _db_commit()

    response = {
        'success': True
    }

    return flask.jsonify(response)


@application.route('/manage')
def pywps_manage_page():
    processes = models.Request.query.order_by(models.Request.time_start)

    filter_identifiers = db.session.query(models.Request.identifier.distinct().label('identifier')).all()
    filter_identifiers = [filter_identifier.identifier for filter_identifier in filter_identifiers]

    return flask.render_template('manage_processes.html', active_page='manage_processes', processes=processes, filter_identifiers=filter_identifiers, wps_response_status=wps_response_status)


@application.route('/manage/table-entries', methods=['POST'])
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

    return flask.render_template('manage_processes_table_entries.html', processes=query.all(), wps_response_status=wps_response_status)


@application.route('/create-database-tables', methods=['GET',])
def create_database_tables():
    db.create_all()

    return 'OK'


@application.before_request
def before_request():
    db.get_engine(application).dispose()
