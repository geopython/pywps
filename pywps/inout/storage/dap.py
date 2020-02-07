##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging
from pywps import configuration as config
from .implementationbuilder import StorageImplementationBuilder
from .file import FileStorage

LOGGER = logging.getLogger('PYWPS')


class DapStorageBuilder(StorageImplementationBuilder):
    def build(self):
        file_path = config.get_config_value('dap', 'outputpath')
        base_url = config.get_config_value('dap', 'outputurl')
        return FileStorage(file_path, base_url)
