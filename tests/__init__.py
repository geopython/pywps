##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import sys
import unittest

import os
import subprocess
import tempfile
import configparser
import pywps.configuration as config

from tests import test_capabilities
from tests import test_describe
from tests import test_execute
from tests import test_exceptions
from tests import test_inout
from tests import test_literaltypes
from tests import validator
from tests import test_ows
from tests import test_formats
from tests import test_dblog
from tests import test_wpsrequest
from tests import test_service
from tests import test_process
from tests import test_processing
from tests import test_assync
from tests import test_grass_location
from tests import test_storage
from tests import test_filestorage
from tests import test_s3storage
from tests.validator import test_complexvalidators
from tests.validator import test_literalvalidators


def find_grass():
    """Check whether GRASS is installed and return path to its GISBASE."""
    startcmd = ['grass', '--config', 'path']

    try:
        p = subprocess.Popen(startcmd,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        return None

    out, _ = p.communicate()

    str_out = out.decode("utf-8")
    gisbase = str_out.rstrip(os.linesep)

    return gisbase


def config_grass(gisbase):
    """Configure PyWPS to allow GRASS commands."""
    conf = configparser.ConfigParser()
    conf.add_section('grass')
    conf.set('grass', 'gisbase', gisbase)
    conf.set('grass', 'gui', 'text')

    _, conf_path = tempfile.mkstemp()
    with open(conf_path, 'w') as c:
        conf.write(c)

    config.load_configuration(conf_path)


def load_tests(loader=None, tests=None, pattern=None):
    """Load tests
    """
    gisbase = find_grass()
    if gisbase:
        config_grass(gisbase)

    return unittest.TestSuite([
        test_capabilities.load_tests(),
        test_execute.load_tests(),
        test_describe.load_tests(),
        test_inout.load_tests(),
        test_exceptions.load_tests(),
        test_ows.load_tests(),
        test_literaltypes.load_tests(),
        test_complexvalidators.load_tests(),
        test_literalvalidators.load_tests(),
        test_formats.load_tests(),
        test_dblog.load_tests(),
        test_wpsrequest.load_tests(),
        test_service.load_tests(),
        test_process.load_tests(),
        test_processing.load_tests(),
        test_assync.load_tests(),
        test_grass_location.load_tests(),
        test_storage.load_tests(),
        test_filestorage.load_tests(),
        test_s3storage.load_tests(),
    ])


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(load_tests())
    if not result.wasSuccessful():
        sys.exit(1)
