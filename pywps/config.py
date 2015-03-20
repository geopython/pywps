import os
import ConfigParser
import tempfile

config = None


def get_config_value(section, option):
    """Get desired value from  configuration files

    :param section: section in configuration files
    :type section: string
    :param option: option in the section
    :type option: string
    :returns: value found in the configuration file
    """

    value = ''

    if not config:
        load_configuration()

    if config.has_section(section):
        if config.has_option(section, option):
            value = config.get(section, option)

            # Convert Boolean string to real Boolean values
            if value.lower() == "false":
                value = False
            elif value.lower() == "true":
                value = True

    return value


def load_configuration():
    """Load PyWPS configuration from configuration files.
    The later configuration file in the array overwrites configuration
    from the first.
    """
    global config

    config = ConfigParser.SafeConfigParser()

    # Set default values
    config.add_section('wps')
    config.set('wps', 'encoding', 'utf-8')
    config.set('wps', 'title', 'PyWPS Server')
    config.set('wps', 'version', '1.0.0')
    config.set('wps', 'abstract', '')
    config.set('wps', 'fees', 'NONE')
    config.set('wps', 'constraint', 'NONE')
    config.set('wps', 'serveraddress', 'http://')
    config.set('wps', 'keywords', '')
    config.set('wps', 'lang', 'en-CA')

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
    config.set('server', 'maxinputparamlength', '1024')
    config.set('server', 'maxfilesize', '3mb')
    config.set('server', 'tempPath', tempfile.gettempdir())
    config.set('server', 'processesPath', '')
    config.set('server', 'outputUrl', '')
    config.set('server', 'outputPath', '')
    config.set('server', 'logFile', '')
    config.set('server', 'logLevel', 'INFO')

    # Read configuration file
    pywps_cfg = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.path.pardir,
        "pywps.cfg")
    files = [pywps_cfg]
    config.read(files)