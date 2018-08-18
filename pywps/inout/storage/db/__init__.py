##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
from abc import ABCMeta, abstractmethod
from pywps import configuration as config
from pywps.inout.formats import DATA_TYPE
from pywps.exceptions import NoApplicableCode
from .. import STORE_TYPE
from .. import StorageAbstract
import sqlalchemy


LOGGER = logging.getLogger('PYWPS')


class DbStorage(StorageAbstract):

    def __init__(self):
        # get db_type from configuration
        try:
            self.db_type = config.get_config_value('db', 'db_type').lower()
        except KeyError:
            raise Exception("Database type has not been specified")

    @staticmethod
    def get_db_type():
        from . import sqlite
        from . import pg
        # create an instance of the appropriate class
        db_type = config.get_config_value('db', 'db_type').lower()
        if db_type == "pg":
            storage = pg.PgStorage()
        elif db_type == "sqlite":
            storage = sqlite.SQLiteStorage()
        else:
            raise Exception("Unknown database type: '{}'".format(config.get_config_value('db', 'db_type').lower()))

        return storage

    def initdb(self):
        pass

    def store(self, output):
        """ Creates reference that is returned to the client
        """
        pass

    def store_vector_output(self, file_name, identifier):
        pass

    def store_raster_output(self, file_name, identifier):
        pass

    def store_other_output(self, file_name, identifier, uuid):
        pass
