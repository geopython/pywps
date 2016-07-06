"""
Reads the PyWPS configuration file
"""
# Author:    Calin Ciociu
#            
# License:
#
# Web Processing Service implementation
# Copyright (C) 2015 PyWPS Development Team, represented by Jachym Cepicky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import logging
import sys
import os
import tempfile
import pywps

from pywps._compat import PY2
if PY2:
    import ConfigParser
else:
    import configparser


config = None
LOGGER = logging.getLogger("PYWPS")


def get_config_value(section, option):
    """Get desired value from  configuration files

    :param section: section in configuration files
    :type section: string
    :param option: option in the section
    :type option: string
    :returns: value found in the configuration file
    """

    if not config:
        load_configuration()

    value = ''

    if config.has_section(section):
        if config.has_option(section, option):
            value = config.get(section, option)

            # Convert Boolean string to real Boolean values
            if value.lower() == "false":
                value = False
            elif value.lower() == "true":
                value = True

    return value


def load_configuration(cfgfiles=None):
    """Load PyWPS configuration from configuration files.
    The later configuration file in the array overwrites configuration
    from the first.

    :param cfgfiles: list of configuration files
    """

    global config

    LOGGER.info('loading configuration')
    if PY2:
        config = ConfigParser.SafeConfigParser()
    else:
        config = configparser.ConfigParser()

    LOGGER.debug('setting default values')
    config.add_section('server')
    config.set('server', 'encoding', 'utf-8')
    config.set('server', 'language', 'en-US')
    config.set('server', 'url', 'http://localhost/wps')
    config.set('server', 'maxprocesses', '30')
    config.set('server', 'maxsingleinputsize', '1mb')
    config.set('server', 'maxrequestsize', '3mb')
    config.set('server', 'temp_path', tempfile.gettempdir())
    config.set('server', 'processes_path', '')
    outputpath = tempfile.gettempdir()
    config.set('server', 'outputurl', 'file:///%s' % outputpath)
    config.set('server', 'outputpath', outputpath)
    config.set('server', 'logfile', '')
    config.set('server', 'loglevel', 'INFO')
    config.set('server', 'workdir',  tempfile.gettempdir())
    config.set('server', 'parallelprocesses', '2')

    config.add_section('metadata:main')
    config.set('metadata:main', 'identification_title', 'PyWPS Processing Service')
    config.set('metadata:main', 'identification_abstract', 'PyWPS is an implementation of the Web Processing Service standard from the Open Geospatial Consortium. PyWPS is written in Python.')
    config.set('metadata:main', 'identification_keywords', 'PyWPS,WPS,OGC,processing')
    config.set('metadata:main', 'identification_keywords_type', 'theme')
    config.set('metadata:main', 'identification_fees', 'NONE')
    config.set('metadata:main', 'identification_accessconstraints', 'NONE')
    config.set('metadata:main', 'provider_name', 'Organization Name')
    config.set('metadata:main', 'provider_url', 'http://pywps.org/')
    config.set('metadata:main', 'contact_name', 'Lastname, Firstname')
    config.set('metadata:main', 'contact_position', 'Position Title')
    config.set('metadata:main', 'contact_address', 'Mailing Address')
    config.set('metadata:main', 'contact_city', 'City')
    config.set('metadata:main', 'contact_stateorprovince', 'Administrative Area')
    config.set('metadata:main', 'contact_postalcode', 'Zip or Postal Code')
    config.set('metadata:main', 'contact_country', 'Country')
    config.set('metadata:main', 'contact_phone', '+xx-xxx-xxx-xxxx')
    config.set('metadata:main', 'contact_fax', '+xx-xxx-xxx-xxxx')
    config.set('metadata:main', 'contact_email', 'Email Address')
    config.set('metadata:main', 'contact_url', 'Contact URL')
    config.set('metadata:main', 'contact_hours', 'Hours of Service')
    config.set('metadata:main', 'contact_instructions', 'During hours of service.  Off on weekends.')
    config.set('metadata:main', 'contact_role', 'pointOfContact')

    config.add_section('grass')
    config.set('grass', 'gisbase', '')

    if not cfgfiles:
        cfgfiles = _get_default_config_files_location()

    if isinstance(cfgfiles, str):
        cfgfiles = [cfgfiles]

    loaded_files = config.read(cfgfiles)
    if loaded_files:
        LOGGER.info('Configuration file(s) %s loaded', loaded_files)
    else:
        LOGGER.info('No configuration files loaded. Using default values')

    _check_config()

def _check_config():
    """Check some configuration values
    """
    workdir = get_config_value('server', 'workdir')

    if not os.path.isdir(workdir):
        LOGGER.warning('server->workdir configuration value %s is not directory'
                % workdir)


def _get_default_config_files_location():
    """Get the locations of the standard configuration files. These are
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
    """Get real size of given obeject

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
    LOGGER.debug('Calculated real size of %s is %s', mbsize, newsize)
    return newsize
