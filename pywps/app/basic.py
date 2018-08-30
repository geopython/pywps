##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################
"""
XML tools
"""

import logging
from werkzeug.wrappers import Response
from pywps import __version__

LOGGER = logging.getLogger('PYWPS')


def get_xpath_ns(version):
    """Get xpath namespace for specified WPS version
    currently 1.0.0 or 2.0.0 are supported
    """

    def xpath_ns(ele, path):
        """Function, which will return xpath namespace for given
        element and xpath
        """
        if version == "1.0.0":
            from pywps import namespaces100
            nsp = namespaces100
        elif version == "2.0.0":
            from pywps import namespaces200
            nsp = namespaces200
        return ele.xpath(path, namespaces=nsp)

    return xpath_ns


def xml_response(doc):
    """XML response serializer"""
    response = Response(doc, content_type='text/xml')
    response.status_percentage = 100
    return response
