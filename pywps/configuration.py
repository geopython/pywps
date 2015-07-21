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
    """

    global config

    if PY2:
        config = ConfigParser.SafeConfigParser()
    else:
        config = configparser.SafeConfigParser()

    # Set default values
    config.add_section('wps')
    config.set('wps', 'encoding', 'utf-8')
    config.set('wps', 'title', 'PyWPS Server')
    config.set('wps', 'version', '1.0.0')
    config.set('wps', 'abstract', '')
    config.set('wps', 'fees', 'NONE')
    config.set('wps', 'constraint', 'NONE')
    config.set('wps', 'serveraddress', 'http://localhost')
    config.set('wps', 'serverport', '5000')
    config.set('wps', 'keywords', '')
    config.set('wps', 'lang', 'en-EN')

    config.add_section('provider')
    config.set('provider', 'providerName', 'Your Company Name')
    config.set('provider', 'individualName', 'Your Name')
    config.set('provider', 'positionName', 'Your Position')
    config.set('provider', 'role', 'Your Role')
    config.set('provider', 'deliveryPoint', 'Street')
    config.set('provider', 'city', 'City')
    config.set('provider', 'postalCode', '000 00')
    config.set('provider', 'country', 'LU')
    config.set('provider', 'electronicalMailAddress', 'login@server.org')
    config.set('provider', 'providerSite', 'http://foo.bar')
    config.set('provider', 'phoneVoice', 'False')
    config.set('provider', 'phoneFacsimile', 'False')
    config.set('provider', 'administrativeArea', 'False')
    config.set('provider', 'onlineResource', 'http://foo.bar')
    config.set('provider', 'hoursOfService', '00:00-24:00')
    config.set('provider', 'contactInstructions', 'NONE')

    config.add_section('server')
    config.set('server', 'maxoperations', '30')
    config.set('server', 'maxsingleinputsize', '1mb')
    config.set('server', 'maxrequestsize', '3mb')
    config.set('server', 'tempPath', tempfile.gettempdir())
    config.set('server', 'processesPath', '')
    config.set('server', 'outputUrl', '/')
    config.set('server', 'outputPath', tempfile.gettempdir())
    config.set('server', 'logFile', '')
    config.set('server', 'logLevel', 'INFO')

    if not cfgfiles:
        cfgfiles = _get_default_config_files_location()

    if type(cfgfiles) != type(()):
        cfgfiles = (cfgfiles)

    loaded_files = config.read(cfgfiles)
    if loaded_files:
        print('Configuration file(s) {} loaded'.format(loaded_files))
    else:
        print('No configuration files loaded. Using default values.')

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

    # configuration file as environment variable
    if os.getenv("PYWPS_CFG"):

        # Windows or Unix
        if sys.platform == 'win32':
            PYWPS_INSTALL_DIR = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
            cfgfiles = (os.getenv("PYWPS_CFG"))
        else:
            cfgfiles = (os.getenv("PYWPS_CFG"))

    # try to eastimate the default location
    else:
        # Windows or Unix
        if sys.platform == 'win32':
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
    return newsize
