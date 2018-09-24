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

    def store_vector_output(self, file_name, identifier):
        """ Open output file, connect to PG database and copy data there
        """
        from osgeo import ogr

        db_location = self.schema_name + "." + identifier
        dsc_out = ogr.Open("PG:" + self.target)

        # connect to a database and copy output there
        LOGGER.debug("Database: {}".format(self.target))
        dsc_in = ogr.Open(file_name)
        if dsc_in is None:
            raise Exception("Reading data failed.")
        if dsc_out is None:
            raise NoApplicableCode("Could not connect to the database.")
        layer = dsc_out.CopyLayer(dsc_in.GetLayer(), db_location,
                                  ['OVERWRITE=YES'])

        if layer is None:
            raise Exception("Writing output data to the database failed.")

        dsc_out.Destroy()
        dsc_in.Destroy()

        # returns process identifier (defined within the process)
        return identifier

    def store_raster_output(self, file_name, identifier):

        from subprocess import run, Popen, PIPE

        # Convert raster to an SQL query
        command1 = ["raster2pgsql", "-a", file_name, self.schema_name + "." + identifier]
        p = Popen(command1, stdout=PIPE)
        # Apply the SQL query
        command2 = ["psql", "-h", "localhost", "-p", "5432", "-d", self.dbname]
        run(command2, stdin=p.stdout)

        return identifier

    def store_other_output(self, file_name, identifier, uuid):

        from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, func, create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        base = declarative_base()

        engine = create_engine(
            'postgresql://{}:{}@{}:{}/{}'.format(
                self.dbname,
                self.password,
                self.host,
                self.port,
                self.user
            )
        )

        # Create table
        class Other_output(base):
            __tablename__ = identifier
            __table_args__ = {'schema': self.schema_name}

            primary_key = Column(Integer, primary_key=True)
            uuid = Column(String(64))
            data = Column(LargeBinary)
            timestamp = Column(DateTime(timezone=True), server_default=func.now())

        Session = sessionmaker(engine)
        session = Session()

        base.metadata.create_all(engine)

        # Open file as binary
        with open(file_name, "rb") as data:
            out = data.read()

            # Add data to table
            output = Other_output(uuid=uuid, data=out)
            session.add(output)
            session.commit()

        return identifier

    def store(self, output):
        """ Creates reference that is returned to the client
        """

        DATA_TYPE.is_valid_datatype(output.output_format.data_type)

        if output.output_format.data_type is DATA_TYPE.VECTOR:
            self.store_vector_output(output.file, output.identifier)
        elif output.output_format.data_type is DATA_TYPE.RASTER:
            self.store_raster_output(output.file, output.identifier)
        elif output.output_format.data_type is DATA_TYPE.OTHER:
            self.store_other_output(output.file, output.identifier, output.uuid)
        else:
            # This should never happen
            raise Exception("Unknown data type")

        url = '{}.{}.{}'.format(self.dbname, self.schema_name, output.identifier)

        # returns value for database storage defined in the STORE_TYPE class,
        # name of the output file and a reference
        return (STORE_TYPE.DB, output.file, url)
