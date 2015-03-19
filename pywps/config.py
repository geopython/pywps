import os
import ConfigParser

config = None


def get_config_value(*args):
    """Get desired value from  configuration files

    :param section: section in configuration files
    :type section: string
    :param key: key in the section
    :type key: string
    :returns: value found in the configuration file
    """

    value = None

    if not config:
        load_configuration()

    if config.has_option(*args):
        value = config.get(*args)

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

    default_cfg = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.path.pardir,
        "default.cfg")

    pywps_cfg = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.path.pardir,
        "pywps.cfg")

    files = [default_cfg, pywps_cfg]

    config = ConfigParser.SafeConfigParser()
    config.read(files)