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


    def store_raster_output(self, file_name, identifier):

        from subprocess import call

        call(["gdal_translate", "-of", "Rasterlite", file_name, "RASTERLITE:" + self.target + ",table=" + identifier])

        # returns process identifier (defined within the process)
        return identifier
