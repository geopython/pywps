##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""
Implementation of logging for PyWPS-4
"""

import logging
from pywps import configuration
from pywps.exceptions import NoApplicableCode
from pywps._compat import PY2
import sqlite3
import datetime
import pickle
import json
import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, VARCHAR, Float, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

LOGGER = logging.getLogger('PYWPS')
_SESSION_MAKER = None
_LAST_SESSION = None


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
    request = Column(LargeBinary, nullable=False)


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

    session.close()
    return running


def get_stored():
    """Returns running processes ids
    """

    session = get_session()
    stored = session.query(RequestInstance)

    session.close()
    return stored


def get_first_stored():
    """Returns running processes ids
    """

    session = get_session()
    request = session.query(RequestInstance).first()

    return request


def store_status(uuid, wps_status, message=None, status_percentage=None):
    """Writes response to database
    """
    session = get_session()

    requests = session.query(ProcessInstance).filter_by(uuid=str(uuid))
    if requests.count():
        request = requests.one()
        request.time_end = datetime.datetime.now()
        request.message = str(message)
        request.percent_done = status_percentage
        request.status = wps_status
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
    global _LAST_SESSION

    if _LAST_SESSION:
        _LAST_SESSION.close()

    if _SESSION_MAKER:
        _SESSION_MAKER.close_all()
        _LAST_SESSION = _SESSION_MAKER()
        return _LAST_SESSION

    database = configuration.get_config_value('logging', 'database')
    echo = True
    level = configuration.get_config_value('logging', 'level')
    level_name = logging.getLevelName(level)
    if isinstance(level_name, int) and level_name >= logging.INFO:
        echo = False
    try:
        if database.startswith("sqlite") or database.startswith("memory"):
            engine = sqlalchemy.create_engine(database,
                                              connect_args={'check_same_thread': False},
                                              poolclass=StaticPool,
                                              echo=echo)
        else:
            engine = sqlalchemy.create_engine(database, echo=echo, poolclass=NullPool)
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise NoApplicableCode("Could not connect to database: {}".format(e.message))

    Session = sessionmaker(bind=engine)
    ProcessInstance.metadata.create_all(engine)
    RequestInstance.metadata.create_all(engine)

    _SESSION_MAKER = Session

    _LAST_SESSION = _SESSION_MAKER()
    return _LAST_SESSION


def store_process(uuid, request):
    """Save given request under given UUID for later usage
    """

    session = get_session()
    request_json = request.json
    if not PY2:
        # the BLOB type requires bytes on Python 3
        request_json = request_json.encode('utf-8')
    request = RequestInstance(uuid=str(uuid), request=request_json)
    session.add(request)
    session.commit()
    session.close()


def remove_stored(uuid):
    """Remove given request from stored requests
    """

    session = get_session()
    request = session.query(RequestInstance).filter_by(uuid=str(uuid)).first()
    session.delete(request)
    session.commit()
    session.close()
