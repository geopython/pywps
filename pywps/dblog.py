##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""
Database interface for PyWPS-4
"""

import logging
import sys

from pywps import configuration
from pywps.exceptions import NoApplicableCode

import sqlite3
import datetime
import pickle
import json
import os
from multiprocessing import Lock

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, VARCHAR, Float, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from pywps.response.status import WPS_STATUS

from types import SimpleNamespace as ns

LOGGER = logging.getLogger('PYWPS')
_SESSION_MAKER = None

_tableprefix = configuration.get_config_value('logging', 'prefix')
_schema = configuration.get_config_value('logging', 'schema')

Base = declarative_base()

# Use custom lock scheme for the database because there is no unified database lock mechanism
_db_lock = None


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
    timestamp = Column(DateTime(), nullable=False)
    request = Column(LargeBinary, nullable=False)


class StorageRecord(Base):
    __tablename__ = '{}storage_records'.format(_tableprefix)

    uuid = Column(VARCHAR(255), primary_key=True, nullable=False)
    type = Column(VARCHAR(255), nullable=False)
    pretty_filename = Column(VARCHAR(255), nullable=True)
    mimetype = Column(VARCHAR(255), nullable=True)
    timestamp = Column(DateTime(), nullable=False)
    data = Column(LargeBinary, nullable=False)


class StatusRecord(Base):
    __tablename__ = '{}status_records'.format(_tableprefix)

    # Process uuid
    uuid = Column(VARCHAR(255), primary_key=True, nullable=False)
    # Time stamp for creation time
    timestamp = Column(DateTime(), nullable=False)
    # json data used in template
    data = Column(LargeBinary, nullable=False)


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


def get_process_counts():
    """Returns running and stored process counts and
    """

    session = get_session()
    stored_query = session.query(RequestInstance.uuid)
    running_count = (
        session.query(ProcessInstance)
        .filter(ProcessInstance.status.in_([WPS_STATUS.STARTED, WPS_STATUS.PAUSED]))
        .count()
    )
    stored_count = stored_query.count()
    session.close()
    return running_count, stored_count


def pop_first_stored():
    """Gets the first stored process and delete it from the stored_requests table
    """
    session = get_session()
    request = session.query(RequestInstance).first()

    if request:
        delete_count = session.query(RequestInstance).filter_by(uuid=request.uuid).delete()
        if delete_count == 0:
            LOGGER.debug("Another thread or process took the same stored request")
            request = None

        session.commit()
    session.close()
    return request


def pop_first_stored_with_limit(target_limit):
    """Gets n first stored process to reach target_count
    """
    session = get_session()

    # Cleanup crashed request
    if sys.platform == "linux":
        running = session.query(ProcessInstance) \
            .filter(ProcessInstance.status.in_([WPS_STATUS.STARTED, WPS_STATUS.PAUSED]))

        failed = []
        for uuid, pid in ((p.uuid, p.pid) for p in running):
            # No process with this pid, the process has crashed
            if not os.path.exists(os.path.join("/proc", str(pid))):
                failed.append(uuid)
                continue

            # If we can't read the environ, that mean the process belong another user
            # which mean that this is not our process, thus our process has crashed
            # this not work because root is the user for the apache
            # if not os.access(os.path.join("/proc", str(pid), "environ"), os.R_OK):
            #     failed.append(uuid)
            #     continue

        for uuid in failed:
            _set_process_failed(uuid)

        running = session.query(ProcessInstance) \
            .filter(ProcessInstance.status.in_([WPS_STATUS.STARTED, WPS_STATUS.PAUSED]))

        if running.count() >= target_limit:
            return None

        request = session.query(RequestInstance) \
            .order_by(RequestInstance.timestamp.asc()) \
            .first()

        if request:
            delete_count = session.query(RequestInstance).filter_by(uuid=request.uuid).delete()
            if delete_count == 0:
                LOGGER.debug("WARNING should not happen: Another thread or process took the same stored request")
                request = None

            # Ensure the process is marked as started to be included in running_count
            process_instance = session.query(ProcessInstance).filter_by(uuid=str(request.uuid)).one()
            if process_instance:
                process_instance.pid = os.getpid()
                process_instance.time_end = datetime.datetime.now()
                process_instance.message = 'PyWPS Process started'
                process_instance.status = WPS_STATUS.STARTED

            session.commit()
        session.close()
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


# Update or create a store instance
def update_storage_record(store_instance):
    session = get_session()
    r = session.query(StorageRecord).filter_by(uuid=str(store_instance.uuid))
    if r.count():
        store_instance_record = r.one()
        store_instance_record.type = store_instance.__class__.__name__
        store_instance_record.pretty_filename = store_instance.pretty_filename
        store_instance_record.mimetype = store_instance.mimetype
        store_instance_record.data = store_instance.dump()
    else:
        store_instance_record = StorageRecord(
            uuid=str(store_instance.uuid),
            type=store_instance.__class__.__name__,
            timestamp=datetime.datetime.now(),
            pretty_filename=store_instance.pretty_filename,
            mimetype=store_instance.mimetype,
            data=store_instance.dump()
        )
        session.add(store_instance_record)
    session.commit()
    session.close()


# Get store instance data from uuid
def get_storage_record(uuid):
    session = get_session()
    r = session.query(StorageRecord).filter_by(uuid=str(uuid))
    if r.count():
        store_instance_record = r.one()
        # Copy store_instance_record content to unlink data from session
        # TODO: get dynamic list of attributes
        attrs = ["uuid", "type", "timestamp", "pretty_filename", "mimetype", "data"]
        store_instance_record = ns(**{k: getattr(store_instance_record, k) for k in attrs})
        store_instance_record.data = store_instance_record.data
        session.close()
        return store_instance_record
    session.close()
    return None


# Update or create a store instance
def update_status_record(uuid, data):
    session = get_session()
    r = session.query(StatusRecord).filter_by(uuid=str(uuid))
    if r.count():
        status_record = r.one()
        status_record.timestamp = datetime.datetime.now()
        status_record.data = json.dumps(data).encode("utf-8")
    else:
        status_record = StatusRecord(
            uuid=str(uuid),
            timestamp=datetime.datetime.now(),
            data=json.dumps(data).encode("utf-8")
        )
        session.add(status_record)
    session.commit()
    session.close()


# Get store instance data from uuid
def get_status_record(uuid):
    session = get_session()
    r = session.query(StatusRecord).filter_by(uuid=str(uuid))
    if r.count():
        status_record = r.one()
        # Ensure new item
        # TODO: get dynamic list of attributes
        attrs = ["uuid", "timestamp", "data"]
        status_record = ns(**{k: getattr(status_record, k) for k in attrs})
        status_record.data = json.loads(status_record.data.decode("utf-8"))
        session.close()
        return status_record
    session.close()
    return None


def update_pid(uuid, pid):
    """Update actual pid for the uuid processing
    """
    session = get_session()

    requests = session.query(ProcessInstance).filter_by(uuid=str(uuid))
    if requests.count():
        request = requests.one()
        request.pid = pid
        session.commit()
    session.close()


def _set_process_failed(uuid):
    store_status(uuid, WPS_STATUS.FAILED, "Process crashed", 100)
    session = get_session()
    # Update status record
    r = session.query(StatusRecord).filter_by(uuid=str(uuid))
    if r.count():
        status_record = r.one()
        data = json.loads(status_record.data.decode("utf-8"))
        data["status"].update({
            "status": "failed",
            "code": "ProcessCrashed",
            "locator": "None",
            "message": "Process crashed"
        })
        LOGGER.debug(str(data))
        status_record.data = json.dumps(data).encode("utf-8")
    session.commit()
    session.close()


def cleanup_crashed_process():
    # TODO: implement other platform
    if sys.platform != "linux":
        return

    session = get_session()

    stored_query = session.query(RequestInstance.uuid)
    running_cur = (
        session.query(ProcessInstance)
        .filter(ProcessInstance.status.in_([WPS_STATUS.STARTED, WPS_STATUS.PAUSED]))
        .filter(~ProcessInstance.uuid.in_(stored_query))
    )

    failed = []
    running = [(p.uuid, p.pid) for p in running_cur]
    session.close()

    for uuid, pid in running:
        # No process with this pid, the process has crashed
        if not os.path.exists(os.path.join("/proc", str(pid))):
            failed.append(uuid)
            continue

        # If we can't read the environ, that mean the process belong another user
        # which mean that this is not our process, thus our process has crashed
        # this not work because root is the user for the apache
        # if not os.access(os.path.join("/proc", str(pid), "environ"), os.R_OK):
        #     failed.append(uuid)
        #     continue
        pass

    for uuid in failed:
        _set_process_failed(uuid)

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


def _get_lock():
    global _db_lock
    if _db_lock is None:
        # Default lock work accross all forked process, but does not work with multiple process
        _db_lock = Lock()
    return _db_lock


def get_session():
    """Get Connection for database
    """
    LOGGER.debug('Initializing database connection')
    global _SESSION_MAKER

    if _SESSION_MAKER:
        return _SESSION_MAKER()

    database = configuration.get_config_value('logging', 'database')
    echo = configuration.get_config_value('logging', 'database_echo') == 'true'
    try:
        if ":memory:" in database:
            engine = sqlalchemy.create_engine(database,
                                              echo=echo,
                                              connect_args={'check_same_thread': False},
                                              poolclass=StaticPool)
        elif database.startswith("sqlite"):
            engine = sqlalchemy.create_engine(database,
                                              echo=echo,
                                              connect_args={'check_same_thread': False},
                                              poolclass=NullPool)
        else:
            engine = sqlalchemy.create_engine(database, echo=echo, poolclass=NullPool)
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise NoApplicableCode("Could not connect to database: {}".format(e.message))

    Session = sessionmaker(bind=engine)
    ProcessInstance.metadata.create_all(engine)
    RequestInstance.metadata.create_all(engine)

    _SESSION_MAKER = Session

    return _SESSION_MAKER()


def store_process(request):
    """Save given request under given UUID for later usage
    """

    session = get_session()
    request_json = request.json
    # the BLOB type requires bytes on Python 3
    request_json = request_json.encode('utf-8')
    request = RequestInstance(uuid=str(request.uuid), request=request_json, timestamp=datetime.datetime.now())
    session.add(request)
    session.commit()
    session.close()
