##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
from pywps import configuration as config
from pywps.exceptions import NoApplicableCode
from .. import STORE_TYPE
from pywps.inout.formats import DATA_TYPE
from . import DbStorage
import sqlalchemy

LOGGER = logging.getLogger('PYWPS')


class PgStorage(DbStorage):

    def __init__(self):
        # TODO: more databases in config file
        # create connection string
        dbsettings = "db"
        self.dbname = config.get_config_value(dbsettings, "dbname")
        self.user = config.get_config_value(dbsettings, "user")
        self.password = config.get_config_value(dbsettings, "password")
        self.host = config.get_config_value(dbsettings, "host")
        self.port = config.get_config_value(dbsettings, "port")

        self.target = "dbname={} user={} password={} host={} port={}".format(
            self.dbname, self.user, self.password, self.host, self.port
        )

        self.schema_name = config.get_config_value(dbsettings, "schema_name")

        self.initdb()

    def store_raster_output(self, file_name, identifier):

        from subprocess import call, run, Popen, PIPE

        # Convert raster to an SQL query
        command1 = ["raster2pgsql", "-a", file_name, self.schema_name + "." + identifier]
        p = Popen(command1, stdout=PIPE)
        # Apply the SQL query
        command2 = ["psql", "-h", "localhost", "-p", "5432", "-d", self.dbname]
        run(command2, stdin=p.stdout)

        return identifier

    def initdb(self):

        from sqlalchemy.schema import CreateSchema

        dbsettings = "db"
        connstr = 'postgresql://{}:{}@{}:{}/{}'.format(
            config.get_config_value(dbsettings, "user"),
            config.get_config_value(dbsettings, "password"),
            config.get_config_value(dbsettings, "host"),
            config.get_config_value(dbsettings, "port"),
            config.get_config_value(dbsettings, "dbname")
        )

        engine = sqlalchemy.create_engine(connstr)
        schema_name = config.get_config_value('db', 'schema_name')

        # Create schema; if it already exists, skip this
        try:
            engine.execute(CreateSchema(schema_name))
        # programming error - schema already exists)
        except sqlalchemy.exc.ProgrammingError:
            pass
