"""Configuration handler

.. param:: config

    Configuration object
"""

import os,sys
import pywps
import ConfigParser

config = None

def getConfigValue(*args):
    """Get desired value from  configuration files

    :param section: section in configuration files
    :type section: string
    :param key: key in the section
    :type key: string
    :returns: value found in the configuration file
    :rtype: string
    """

    if not config:
        loadConfiguration()

    value = config.get(*args)

    # Convert Boolean string to real Boolean values
    if value.lower() == "false":
        value = False
    elif value.lower() == "true" :
        value = True
    return value

def setConfigValue(*args):
    """set desired value from  configuration files

    :param section: section in configuration files
    :type section: string
    :param option: option in the section
    :type option: string
    :param value: option in the section
    :type value: string
    :returns: value found in the configuration file
    :rtype: string
    """
    #Note this function is mainly used in the unnitest
    #RawConfigParser.set(section, option, value)
    if not config:
        loadConfiguration()

    value = config.set(*args)

    # Convert Boolean string to real Boolean values



def loadConfiguration(cfgfiles=None):
    """Load PyWPS configuration from configuration files.
    The later configuration file in the array overwrites configuration
    from the first.

    :param cfgfiles: list of file names, where to get configuration from.
    :type cfgfiles: list of strings
    """
    global config

    if cfgfiles == None:
        cfgfiles = _getDefaultConfigFilesLocation()

    if type(cfgfiles) != type(()):
        cfgfiles = (cfgfiles)

    config = ConfigParser.ConfigParser()
    config.read(cfgfiles)
   
def _getDefaultConfigFilesLocation():
    """Get the locations of the standard configuration files. This are

    Unix/Linux:
        1. `pywps/default.cfg`
        2. `/etc/pywps.cfg`
        3. `pywps/etc/pywps.cfg`
        4. `$HOME/.pywps.cfg`

    Windows:
        1. `pywps\\default.cfg`
        2. `pywps\\etc\\default.cfg`
    
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
            cfgfiles = (os.path.join(PYWPS_INSTALL_DIR,"pywps","default.cfg"),
                    os.getenv("PYWPS_CFG"))
        else:
            cfgfiles = (os.path.join(pywps.__path__[0],"default.cfg"),
                    os.getenv("PYWPS_CFG"))

    # try to eastimate the default location
    else:
        # Windows or Unix
        if sys.platform == 'win32':
            PYWPS_INSTALL_DIR = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
            cfgfiles = (os.path.join(PYWPS_INSTALL_DIR,"pywps","default.cfg"),
                    os.path.join(PYWPS_INSTALL_DIR, "pywps","etc","pywps.cfg"))
        else:
            homePath = os.getenv("HOME")
            if homePath:
                cfgfiles = (os.path.join(pywps.__path__[0],"default.cfg"),
                        os.path.join(pywps.__path__[0],"etc", "pywps.cfg"), "/etc/pywps.cfg",
                    os.path.join(os.getenv("HOME"),".pywps.cfg" ))
            else: 
                cfgfiles = (os.path.join(pywps.__path__[0],"default.cfg"),
                        os.path.join(pywps.__path__[0],"etc",
                            "pywps.cfg"), "/etc/pywps.cfg")

    return cfgfiles
