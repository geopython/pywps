"""
Implementation of logging for PyWPS-4
"""

import logging
from pywps import configuration
from pywps.exceptions import NoApplicableCode
import sqlite3
import datetime

LOGGER = logging.getLogger(__name__)
_CONNECTION = None

def log_request(uuid, request):
    """Write OGC WPS request (only the necessary parts) to database logging
    system
    """

    conn = get_connection()
    insert = """
        INSERT INTO
            pywps_requests (uuid, operation, version, time_start, identifier)
        VALUES
            ('{uuid}', '{operation}', '{version}', '{time_start}', '{identifier}')
    """.format(
        uuid=uuid,
        operation=request.operation,
        version=request.version,
        time_start=datetime.datetime.now().isoformat(),
        identifier=_get_identifier(request)
    )
    LOGGER.debug(insert)
    cur = conn.cursor()
    cur.execute(insert)
    conn.commit()
    close_connection()

def update_response(uuid, response, close=False):
    """Writes response to database
    """

    conn = get_connection()
    message = 'Null'
    status_percentage = 'Null'
    status = 'Null'

    if hasattr(response, 'message'):
        message = "'%s'" % response.message
    if hasattr(response, 'status_percentage'):
        status_percentage = response.status_percentage
    if hasattr(response, 'status'):
        status = "'%s'" % response.status

    update = """
        UPDATE
            pywps_requests
        SET
            time_end = '{time_end}', message={message},
            percent_done = {percent_done}, status={status}
        WHERE
            uuid = '{uuid}'
    """.format(
        time_end=datetime.datetime.now().isoformat(),
        message=message,
        percent_done=status_percentage,
        status=status,
        uuid=uuid
    )
    LOGGER.debug(update)
    cur = conn.cursor()
    cur.execute(update)
    conn.commit()
    close_connection()


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

def get_connection():
    """Get Connection for database
    """

    LOGGER.debug('Initializing database connection')
    global _CONNECTION

    if _CONNECTION:
        return _CONNECTION

    database = configuration.get_config_value('server', 'logdatabase')

    if not database:
        database = ':memory:'

    connection = sqlite3.connect(database)
    if check_db_table(connection):
        if check_db_columns(connection):
            _CONNECTION = connection
        else:
            raise NoApplicableCode("""
                Columns in the table 'pywps_requests' in database '%s' are in
                conflict
            """ % database)

    else:
        createsql = """
            CREATE TABLE pywps_requests(
                uuid VARCHAR(255) not null primary key,
                operation varchar(30) not null,
                version varchar(5) not null,
                time_start text not null,
                time_end text,
                identifier text,
                message text,
                percent_done float,
                status varchar(30)
            )
            """
        _CONNECTION = sqlite3.connect(database, check_same_thread=False)
        cursor = _CONNECTION.cursor()
        cursor.execute(createsql)
        _CONNECTION.commit()

    return _CONNECTION

def check_db_table(connection):
    """Check for existing pywps_requests table in the datase

    :return: boolean pywps_requests table is in database
    """

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            name
        FROM
            sqlite_master
        WHERE
            name='pywps_requests'
    """)
    table = cursor.fetchone()
    if table:
        LOGGER.debug('pywps_requests table exists')
        return True
    else:
        LOGGER.debug('pywps_requests table does not exist')
        return False


def check_db_columns(connection):
    """Simple check for existing columns in given database

    we will make just simple check, this is not django

    :return: all needed columns found
    :rtype: boolean
    """

    cur = connection.cursor()
    cur.execute("""PRAGMA table_info('pywps_requests')""")
    metas = cur.fetchall()
    columns = []
    for column in metas:
        columns.append(column[1])

    needed_columns = ['uuid', 'operation', 'version', 'time_start',
                      'time_end', 'identifier', 'message', 'percent_done',
                      'status']
    needed_columns.sort()

    columns.sort()

    if columns == needed_columns:
        return True
    else:
        return False

def close_connection():
    """close connection"""
    LOGGER.debug('Closing DB connection')
    global _CONNECTION
    if _CONNECTION:
        _CONNECTION.close()
    _CONNECTION = None

