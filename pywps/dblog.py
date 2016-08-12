"""
Implementation of logging for PyWPS-4
"""
import logging
import datetime
import json
import os

from pywps.server.app import db, models


#LOGGER = logging.getLogger(__name__)

def _get_identifier(request):
    """Get operation identifier
    """

    if request.operation == 'execute':
        return request.identifier
    elif request.operation == 'describeprocess':
        if request.identifiers:
            return ','.join(request.identifiers)
        else:
            return 'Null'
    else:
        return 'NULL'


def log_request(uuid, request):
    """Write OGC WPS request (only the necessary parts) to database logging
    system
    """
    r = models.Request(
        uuid=str(uuid),
        pid=os.getpid(), 
        operation=request.operation, 
        version=request.version, 
        time_start=datetime.datetime.now().isoformat(), 
        identifier=_get_identifier(request)
    )

    if r:
        db.session.add(r)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()


def get_running():
    """Returns running processes ids
    """
    result = []

    data = models.Request.query.filter(models.Request.percent_done < 100)

    for entry in data:
        result.append(entry)

    return result


def get_stored():
    """Returns running processes ids
    """
    result = []

    data = models.StoredRequest.query.with_entities(models.StoredRequest.uuid)

    for entry in data:
        result.append(entry)

    return result

def get_first_stored():
    """Returns running processes ids
    """
    return models.StoredRequest.query.first()



def update_response(uuid, response, close=False):
    """Writes response to database
    """
    message = None
    status_percentage = None
    status = None

    if hasattr(response, 'message'):
        message = "%s" % response.message
    if hasattr(response, 'status_percentage'):
        status_percentage = response.status_percentage
    if hasattr(response, 'status'):
        status = "%s" % response.status


    try:
        r = models.Request.query.filter(models.Request.uuid == str(uuid)).one()
    except:
        r = None

    if r:
        r.time_end = datetime.datetime.now().isoformat()
        r.pid = os.getpid()
        r.message = message
        r.percent_done = status_percentage
        r.status = status

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()


def store_process(uuid, request):
    """Save given request under given UUID for later usage
    """
    print("bum")
    r = models.StoredRequest(uuid=str(uuid), request=request.json)

    if r:
        db.session.add(r)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()
    

def remove_stored(uuid):
    """Remove given request from stored requests
    """
    print("bum2")
    models.StoredRequest.query.delete()


