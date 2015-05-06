import sys
import os
import pywps
import tempfile

from pywps._compat import PY2
if PY2:
    import ConfigParser
else:
    import configparser


class PyWPSConfig(object):

    def __init__(self, config_path=''):
        self.config = None
        self.config_path = config_path
        self.load_configuration()

    def get_config_value(self, section, option):
        """Get desired value from  configuration files

        :param section: section in configuration files
        :type section: string
        :param option: option in the section
        :type option: string
        :returns: value found in the configuration file
        """

        value = ''

        if self.config.has_section(section):
            if self.config.has_option(section, option):
                value = self.config.get(section, option)

                # Convert Boolean string to real Boolean values
                if value.lower() == "false":
                    value = False
                elif value.lower() == "true":
                    value = True

        return value

    def load_configuration(self):
        """Load PyWPS configuration from configuration files.
        The later configuration file in the array overwrites configuration
        from the first.
        """

        if PY2:
            configuration = ConfigParser.SafeConfigParser()
        else:
            configuration = configparser.SafeConfigParser()

        # Set default values
        configuration.add_section('wps')
        configuration.set('wps', 'encoding', 'utf-8')
        configuration.set('wps', 'title', 'PyWPS Server')
        configuration.set('wps', 'version', '1.0.0')
        configuration.set('wps', 'abstract', '')
        configuration.set('wps', 'fees', 'NONE')
        configuration.set('wps', 'constraint', 'NONE')
        configuration.set('wps', 'serveraddress', 'http://')
        configuration.set('wps', 'keywords', '')
        configuration.set('wps', 'lang', 'en-CA')

        configuration.add_section('provider')
        configuration.set('provider', 'providerName', 'Your Company Name')
        configuration.set('provider', 'individualName', 'Your Name')
        configuration.set('provider', 'positionName', 'Your Position')
        configuration.set('provider', 'role', 'Your Role')
        configuration.set('provider', 'deliveryPoint', 'Street')
        configuration.set('provider', 'city', 'City')
        configuration.set('provider', 'postalCode', '000 00')
        configuration.set('provider', 'country', 'LU')
        configuration.set('provider', 'electronicalMailAddress', 'login@server.org')
        configuration.set('provider', 'providerSite', 'http://foo.bar')
        configuration.set('provider', 'phoneVoice', 'False')
        configuration.set('provider', 'phoneFacsimile', 'False')
        configuration.set('provider', 'administrativeArea', 'False')
        configuration.set('provider', 'onlineResource', 'http://foo.bar')
        configuration.set('provider', 'hoursOfService', '00:00-24:00')
        configuration.set('provider', 'contactInstructions', 'NONE')

        configuration.add_section('server')
        configuration.set('server', 'maxoperations', '30')
        configuration.set('server', 'maxinputparamlength', '1024')
        configuration.set('server', 'maxfilesize', '3mb')
        configuration.set('server', 'tempPath', tempfile.gettempdir())
        configuration.set('server', 'processesPath', '')
        configuration.set('server', 'outputUrl', '/')
        configuration.set('server', 'outputPath', '/')
        configuration.set('server', 'logFile', '')
        configuration.set('server', 'logLevel', 'INFO')

        # try to estimate the default location if no user defined file has been set
        # Windows or Unix
        if os.path.exists(self.config_path):
            configuration.read(self.config_path)
        else:
            if sys.platform == 'win32':
                PYWPS_INSTALL_DIR = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
                cfg_files = (os.path.join(PYWPS_INSTALL_DIR, "pywps", "pywps.cfg"),
                             os.path.join(PYWPS_INSTALL_DIR, "pywps.cfg"))
            else:
                home_path = os.getenv("HOME")
                if home_path:
                    cfg_files = (os.path.join(pywps.__path__[0], "pywps.cfg"),
                                 os.path.join(pywps.__path__[0], os.path.pardir, "pywps.cfg"),
                                 "/etc/pywps.cfg",
                                 os.path.join(os.getenv("HOME"), ".pywps.cfg"))
                else:
                    cfg_files = (os.path.join(pywps.__path__[0], "pywps.cfg"),
                                 os.path.join(pywps.__path__[0], os.path.pardir, "pywps.cfg"),
                                 "/etc/pywps.cfg")
            configuration.read(cfg_files)
        self.config = configuration


#config = PyWPSConfig()