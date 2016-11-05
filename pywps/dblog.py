##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


"""
Implementation of logging for PyWPS-4
"""

import logging
from pywps import configuration
from pywps.exceptions import NoApplicableCode
import sqlite3
import datetime
import pickle
import json
import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, VARCHAR, Float, DateTime, BLOB
from sqlalchemy.orm import sessionmaker

LOGGER = logging.getLogger('PYWPS')
_SESSION_MAKER = None


_tableprefix = configuration.get_config_value('logging', 'prefix')
_schema = configuration.get_config_value('logging', 'schema')

Base = declarative_base()


class ProcessInstance(Base):
    __tablename__ = '{}requests'.format(_tableprefix)

    uuid = Column(VARCHAR(255), primary_key=True, nullable=False)
    pid = Column(Integer, nullable=False)
    operation = Column(VARCHAR(30), nullable=False)
    version = Column(VARCHAR(5), nullable=False)
    time_start = Column(DateTime(), nullable=False)
    time_end = Column(DateTime(), nullable=True)
    identifier = Column(VARCHAR(255), nullable=True)
    message = Column(String, nullable=True)
    percent_done = Column(Float, nullable=True)
    status = Column(Integer, nullable=True)


class RequestInstance(Base):
    __tablename__ = '{}stored_requests'.format(_tableprefix)

    uuid = Column(VARCHAR(255), primary_key=True, nullable=False)
    request = Column(BLOB, nullable=False)


def log_request(uuid, request):
    """Write OGC WPS request (only the necessary parts) to database logging
    system
    """

    pid = os.getpid()
    operation = request.operation
    version = request.version
    time_start = datetime.datetime.now()
    identifier = _get_identifier(request)

    session = get_session()
    request = ProcessInstance(
        uuid=str(uuid), pid=pid, operation=operation, version=version,
        time_start=time_start, identifier=identifier)

    session.add(request)
    session.commit()
    session.close()
    # NoApplicableCode("Could commit to database: {}".format(e.message))


def get_running():
    """Returns running processes ids
    """

    session = get_session()
    running = session.query(ProcessInstance).filter(
        ProcessInstance.percent_done < 100).filter(
            ProcessInstance.percent_done > -1)

    return running


def get_stored():
    """Returns running processes ids
    """

    session = get_session()
    stored = session.query(RequestInstance)

    return stored


def get_first_stored():
    """Returns running processes ids
    """

    session = get_session()
    request = session.query(RequestInstance).first()

    return request


def update_response(uuid, response, close=False):
    """Writes response to database
    """

    session = get_session()
    message = None
    status_percentage = None
    status = None

    if hasattr(response, 'message'):
        message = response.message
    if hasattr(response, 'status_percentage'):
        status_percentage = response.status_percentage
    if hasattr(response, 'status'):
        status = response.status

        if status == '200 OK':
            status = 3
        elif status == 400:
            status = 0

    requests = session.query(ProcessInstance).filter_by(uuid=str(uuid))
    if requests.count():
        request = requests.one()
        request.time_end = datetime.datetime.now()
        request.message = message
        request.percent_done = status_percentage
        request.status = status
        session.commit()
        session.close()


def _get_identifier(request):
    """Get operation identifier
    """

    if request.operation == 'execute':
        return request.identifier
    elif request.operation == 'describeprocess':
        if request.identifiers:
            return ','.join(request.identifiers)
        else:
            return None
    else:
        return None


def get_session():
    """Get Connection for database
    """

    LOGGER.debug('Initializing database connection')
    global _SESSION_MAKER

    database = configuration.get_config_value('logging', 'database')
    echo = True
    level = configuration.get_config_value('logging', 'level')
    if level in ['INFO']:
        echo = False
    try:
        engine = sqlalchemy.create_engine(database, echo=echo)
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise NoApplicableCode("Could not connect to database: {}".format(e.message))

    Session = sessionmaker(bind=engine)
    ProcessInstance.metadata.create_all(engine)
    RequestInstance.metadata.create_all(engine)

    _SESSION_MAKER = Session

    return _SESSION_MAKER()


def store_process(uuid, request):
    """Save given request under given UUID for later usage
    """

    session = get_session()
    request = RequestInstance(uuid=str(uuid), request=request.json)
    session.add(request)
    session.commit()
    session.close()


def remove_stored(uuid):
    """Remove given request from stored requests
    """

    session = get_session()
    request = session.query(RequestInstance).filter_by(name='uuid').first()
    session.delete(request)
    session.commit()
    session.close()
