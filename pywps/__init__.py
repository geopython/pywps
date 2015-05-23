"""
This package contains classes necessary for input parsing OGC WPS requests,
working with list of processes, executing them and redirecting OGC WPS
responses back to client.
"""

import os,sys

PYWPS_INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))

namespaces = {
    'xlink': "http://www.w3.org/1999/xlink",
    'wps': "http://www.opengis.net/wps/1.0.0",
    'ows': "http://www.opengis.net/ows/1.1",
    'gml': "http://www.opengis.net/gml",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

class PyWPS:
    """OGC Web Processsing Service  implementation
    """

    pass


from pywps.app import (
    Process,
    Service,
    WPSRequest,
    WPSResponse,
    LiteralInput,
    LiteralOutput,
    ComplexInput,
    ComplexOutput,
    Format
)

from pywps.formats import FORMATS


if __name__ == "__main__":
    pass

