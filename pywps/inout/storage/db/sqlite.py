##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
from pywps import configuration as config
from .. import STORE_TYPE
from pywps.inout.formats import DATA_TYPE
from pywps.exceptions import NoApplicableCode
from . import DbStorage

LOGGER = logging.getLogger('PYWPS')


class SQLiteStorage(DbStorage):

    def __init__(self):

        self.target = config.get_config_value("db", "dblocation")

    def store_vector_output(self, file_name, identifier):
        """ Open output file, connect to SQLite database and copiy data there
        """
        from osgeo import ogr

        drv = ogr.GetDriverByName("SQLite")
        dsc_out = drv.CreateDataSource(self.target)

        # connect to a database and copy output there
        LOGGER.debug("Database: {}".format(self.target))
        dsc_in = ogr.Open(file_name)
        if dsc_in is None:
            raise Exception("Reading data failed.")
        if dsc_out is None:
            raise NoApplicableCode("Could not connect to the database.")
        layer = dsc_out.CopyLayer(dsc_in.GetLayer(), identifier,
                                  ['OVERWRITE=YES'])

        if layer is None:
            raise Exception("Writing output data to the database failed.")

        dsc_out.Destroy()
        dsc_in.Destroy()

        # returns process identifier (defined within the process)
        return identifier

    def store_raster_output(self, file_name, identifier):

        from subprocess import call

        call(["gdal_translate", "-of", "Rasterlite", file_name, "RASTERLITE:" + self.target + ",table=" + identifier])

        # returns process identifier (defined within the process)
        return identifier

    def store_other_output(self, file_name, identifier, uuid):

        from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, func, create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        base = declarative_base()

        engine = create_engine("sqlite:///{}".format(self.target))

        # Create table
        class Other_output(base):
            __tablename__ = identifier

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

        url = '{}.{}'.format(self.target, output.identifier)

        # returns value for database storage defined in the STORE_TYPE class,
        # name of the output file and a reference
        return (STORE_TYPE.DB, output.file, url)
