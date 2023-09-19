##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""
Reads the PyWPS configuration file
"""

import configparser
import logging
import os
import sys
import tempfile

import pywps

__author__ = "Calin Ciociu"

from pywps.util import file_uri

RAW_OPTIONS = [('logging', 'format'), ]

CONFIG = None
LOGGER = logging.getLogger("PYWPS")

wps_strict = True


class EnvInterpolation(configparser.BasicInterpolation):
    """
    Configuration parser class to allow env variable interpolation.

    With this interpolator it is possible to use env variables as
    part of the values in an cfg file.

    Example (given an env variable HOSTNAME=localhost):

    [server]
    url = http://${HOSTNAME}/wps


    ==> http://localhost/wps


    This code is an adaption from the configuation parsing in the pycsw
    project.
    See also
    - https://github.com/geopython/pycsw/blob/3.0.0-alpha3/pycsw/core/util.py
    - https://stackoverflow.com/a/49529659

    """

    def before_get(self, parser, section, option, value, defaults):
        """Expand env variables when returning values."""
        value = super().before_get(parser, section, option, value, defaults)
        return os.path.expandvars(value)


def get_config_value(section, option, default_value=''):
    """Get desired value from  configuration files

    :param section: section in configuration files
    :type section: string
    :param option: option in the section
    :type option: string
    :param default_value: default value for configuration
    :type default_value: string
    :returns: value found in the configuration file
    """

    if not CONFIG:
        load_configuration()

    value = default_value

    if CONFIG.has_section(section):
        if CONFIG.has_option(section, option):
            raw = (section, option) in RAW_OPTIONS
            value = CONFIG.get(section, option, raw=raw)

            # Convert Boolean string to real Boolean values
            if value.lower() == "false":
                value = False
            elif value.lower() == "true":
                value = True

    return value


def load_hardcoded_configuration():
    """Load PyWPS hardcoded configuration."""

    global CONFIG

    LOGGER.debug('loading harcoded configuration')
    CONFIG = configparser.ConfigParser(os.environ, interpolation=EnvInterpolation())

    tmpdir = tempfile.gettempdir()

    CONFIG.add_section('server')
    CONFIG.set('server', 'encoding', 'utf-8')
    CONFIG.set('server', 'language', 'en-US')
    CONFIG.set('server', 'url', 'http://localhost/wps')
    CONFIG.set('server', 'maxprocesses', '30')
    CONFIG.set('server', 'maxsingleinputsize', '1mb')
    CONFIG.set('server', 'maxrequestsize', '3mb')
    CONFIG.set('server', 'temp_path', tmpdir)
    CONFIG.set('server', 'processes_path', '')
    CONFIG.set('server', 'outputurl', file_uri(tmpdir))
    CONFIG.set('server', 'outputpath', tmpdir)
    CONFIG.set('server', 'allowedinputpaths', '')
    CONFIG.set('server', 'workdir', tmpdir)
    CONFIG.set('server', 'parallelprocesses', '2')
    CONFIG.set('server', 'sethomedir', 'false')
    CONFIG.set('server', 'cleantempdir', 'true')
    CONFIG.set('server', 'storagetype', 'file')
    CONFIG.set('server', 'storage_copy_function', 'copy')
    CONFIG.set("server", "default_mimetype", "text/xml")
    CONFIG.set("server", "json_indent", "2")

    CONFIG.add_section('processing')
    CONFIG.set('processing', 'mode', 'default')
    CONFIG.set('processing', 'path', os.path.dirname(os.path.realpath(sys.argv[0])))
    CONFIG.set('processing', 'drmaa_native_specification', '')

    CONFIG.add_section('logging')
    CONFIG.set('logging', 'file', '')
    CONFIG.set('logging', 'level', 'DEBUG')
    CONFIG.set('logging', 'database', 'sqlite:///:memory:')
    CONFIG.set('logging', 'prefix', 'pywps_')
    CONFIG.set('logging', 'format', '%(asctime)s] [%(levelname)s] file=%(pathname)s line=%(lineno)s module=%(module)s function=%(funcName)s %(message)s')  # noqa

    CONFIG.add_section('metadata:main')
    CONFIG.set('metadata:main', 'identification_title', 'PyWPS Processing Service')
    CONFIG.set('metadata:main', 'identification_abstract', 'PyWPS is an implementation of the Web Processing Service standard from the Open Geospatial Consortium. PyWPS is written in Python.')  # noqa
    CONFIG.set('metadata:main', 'identification_keywords', 'PyWPS,WPS,OGC,processing')
    CONFIG.set('metadata:main', 'identification_keywords_type', 'theme')
    CONFIG.set('metadata:main', 'identification_fees', 'NONE')
    CONFIG.set('metadata:main', 'identification_accessconstraints', 'NONE')
    CONFIG.set('metadata:main', 'provider_name', 'Organization Name')
    CONFIG.set('metadata:main', 'provider_url', 'https://pywps.org/')
    CONFIG.set('metadata:main', 'contact_name', 'Lastname, Firstname')
    CONFIG.set('metadata:main', 'contact_position', 'Position Title')
    CONFIG.set('metadata:main', 'contact_address', 'Mailing Address')
    CONFIG.set('metadata:main', 'contact_city', 'City')
    CONFIG.set('metadata:main', 'contact_stateorprovince', 'Administrative Area')
    CONFIG.set('metadata:main', 'contact_postalcode', 'Zip or Postal Code')
    CONFIG.set('metadata:main', 'contact_country', 'Country')
    CONFIG.set('metadata:main', 'contact_phone', '+xx-xxx-xxx-xxxx')
    CONFIG.set('metadata:main', 'contact_fax', '+xx-xxx-xxx-xxxx')
    CONFIG.set('metadata:main', 'contact_email', 'Email Address')
    CONFIG.set('metadata:main', 'contact_url', 'Contact URL')
    CONFIG.set('metadata:main', 'contact_hours', 'Hours of Service')
    CONFIG.set('metadata:main', 'contact_instructions', 'During hours of service.  Off on weekends.')
    CONFIG.set('metadata:main', 'contact_role', 'pointOfContact')

    CONFIG.add_section('grass')
    CONFIG.set('grass', 'gisbase', '')

    CONFIG.add_section('s3')
    CONFIG.set('s3', 'bucket', '')
    CONFIG.set('s3', 'prefix', '')
    CONFIG.set('s3', 'public', 'false')
    CONFIG.set('s3', 'encrypt', 'false')
    CONFIG.set('s3', 'region', '')


def load_configuration(cfgfiles=None):
    """Load PyWPS configuration from configuration files.

    The later configuration file in the array overwrites configuration
    from the first.

    :param cfgfiles: list of configuration files
    """

    global CONFIG

    load_hardcoded_configuration()

    if not cfgfiles:
        cfgfiles = _get_default_config_files_location()

    if isinstance(cfgfiles, str):
        cfgfiles = [cfgfiles]

    if 'PYWPS_CFG' in os.environ:
        cfgfiles.append(os.environ['PYWPS_CFG'])

    loaded_files = CONFIG.read(cfgfiles, encoding='utf-8')
    if loaded_files:
        LOGGER.info('Configuration file(s) {} loaded'.format(loaded_files))
    else:
        LOGGER.info('No configuration files loaded. Using default values')

    _check_config()


def _check_config():
    """Check some configuration values
    """
    global CONFIG

    def checkdir(confid):

        confvalue = get_config_value('server', confid)

        if not os.path.isdir(confvalue):
            LOGGER.warning('server->{} configuration value {} is not directory'.format(confid, confvalue))

        if not os.path.isabs(confvalue):
            LOGGER.warning('server->{} configuration value {} is not absolute path, making it absolute to {}'.format(
                           confid, confvalue, os.path.abspath(confvalue)))
            CONFIG.set('server', confid, os.path.abspath(confvalue))

    [checkdir(n) for n in ['workdir', 'outputpath']]


def _get_default_config_files_location():
    """Get the locations of the standard configuration files.

    These are:
    Unix/Linux:
        1. `/etc/pywps.cfg`
        2. `$HOME/.pywps.cfg`
    Windows:
        1. `pywps\\etc\\default.cfg`
    Both:
        1. `$PYWPS_CFG environment variable`

    :returns: configuration files
    :rtype: list of strings
    """

    is_win32 = sys.platform == 'win32'
    if is_win32:
        LOGGER.debug('Windows based environment')
    else:
        LOGGER.debug('UNIX based environment')

    if os.getenv("PYWPS_CFG"):
        LOGGER.debug('using PYWPS_CFG environment variable')
        # Windows or Unix
        if is_win32:
            PYWPS_INSTALL_DIR = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
            cfgfiles = (os.getenv("PYWPS_CFG"))
        else:
            cfgfiles = (os.getenv("PYWPS_CFG"))

    else:
        LOGGER.debug('trying to estimate the default location')
        # Windows or Unix
        if is_win32:
            PYWPS_INSTALL_DIR = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
            cfgfiles = (os.path.join(PYWPS_INSTALL_DIR, "pywps", "etc", "pywps.cfg"))
        else:
            homePath = os.getenv("HOME")
            if homePath:
                cfgfiles = (os.path.join(pywps.__path__[0], "etc", "pywps.cfg"), "/etc/pywps.cfg",
                            os.path.join(os.getenv("HOME"), ".pywps.cfg"))
            else:
                cfgfiles = (os.path.join(pywps.__path__[0], "etc",
                            "pywps.cfg"), "/etc/pywps.cfg")

    return cfgfiles


def get_size_mb(mbsize):
    """Get real size of given object in Mb.

    """

    size = mbsize.lower()

    import re

    units = re.compile("[gmkb].*")
    newsize = float(re.sub(units, '', size))

    if size.find("g") > -1:
        newsize *= 1024
    elif size.find("m") > -1:
        newsize *= 1
    elif size.find("k") > -1:
        newsize /= 1024
    else:
        newsize *= 1
    LOGGER.debug('Calculated real size of {} is {}'.format(mbsize, newsize))
    return newsize
