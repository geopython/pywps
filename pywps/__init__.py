"""
This package contains classes necessary for input parsing OGC WPS requests,
working with list of processes, executing them and redirecting OGC WPS
responses back to client.

example how to use this module::

    import sys

    request="service=wps&request=getcapabilities"

    wps = Pywps(pywps.METHOD_GET)

    if wps.parserRequest(request):
        response = wps.performRequest()

        if response:
            wps.printResponse(sys.stdout)


.. moduleauthor:: Jachym Cepicky <jachym bnhelp cz>

.. data:: METHOD_GET

    String for HTTP GET method identification

.. data:: METHOD_POST

    String for HTTP POST method identification

.. data:: OWS_NAMESPACE

    Namespace of OGC OWS 1.1. standard

.. data:: WPS_NAMESPACE

    Namespace of OGC OWS 1.0.0 standard

.. data:: XLINK_NAMESPACE

    Namespace of OGC OWS 1.0.0 standard

.. data:: PYWPS_INSTALL_DIR

    Directory, where Pywps is installed

.. data:: DEFAULT_LANG

    Default language for WPS instance

.. data:: DEFAULT_VERSION

    Default version of WPS instance

.. data:: config

    Configuration file parser

.. data:: responsePrinter

    :class:`ResponsePrinter` instance, which will print the resulting
    response for you.

"""

__all__ = [ "Parser","processes", "Process", "Exceptions", "Wps", "Templates","Template","XSLT","Ftp"]

# Author:   Jachym Cepicky
#           http://les-ejk.cz
# License:
#
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import pywps
import config
import response
import Parser
import Exceptions
import Wps
from Exceptions import *

import logging, uuid

# global variables
METHOD_GET="GET"
METHOD_POST="POST"
OWS_NAMESPACE = "http://www.opengis.net/ows/1.1"
WPS_NAMESPACE = "http://www.opengis.net/wps/1.0.0"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"

PYWPS_INSTALL_DIR = None # this working directory
DEFAULT_LANG = "en-CA"
DEFAULT_VERSION = "1.0.0"

LOGGER = logging.getLogger(__name__)

logFile = None

class Pywps(object):
    """This is main PyWPS Class, which parses the request, performs the
    desired operation and writes required response back.

    :param method: Used HTTP method, which is either :data:`METHOD_POST`
        or :data:`METHOD_GET`:
    :type method: string
    :param configFiles: List of configuration files. Ignore, if you want to use standard files location
    :type configFiles: list

    .. attribute:: method

        METHOD_GET or METHOD_POST

    .. attribute:: parser

        WPS request parser

    .. attribute:: inputs

        Parsed inputs object

    .. attribute:: request

        GetCapabilities, DescribeProcess or Execute (response) object

    .. attribute:: parser

        GetCapabilities, DescribeProcess or Execute, POST or GET (parsing) object

    .. attribute:: languages

        List of supported languages

    .. attribute:: versions

        Default supported versions

    .. attribute:: logFile

        File objects, where some logs are written to.

        .. note:: Use ::

                import logging
                LOGGER = logging.getLogger(__name__)
                LOGGER.debug("hallo world")

            for any debugging information, you want to get



    """

    method = METHOD_GET                     # HTTP POST or GET

    inputs = None # parsed input values
    request = None # object with getcapabilities/describeprocess/execute
    parser = None

    languages = [DEFAULT_LANG]
    versions=[DEFAULT_VERSION]
    UUID = None

    def __init__(self, method=METHOD_GET, configFiles=None):
        """Class constructor
        """

        # get settings
        config.loadConfiguration(configFiles)
        self.setLogFile()
        self.UUID = uuid.uuid1().__str__()

        self.languages = config.getConfigValue("wps","lang").split(",")
        DEFAULT_LANG = self.languages[0]

        # set default version
        self.versions = config.getConfigValue("wps","version").split(",")
        DEFAULT_VERSION = self.versions[0]

        # find out the request method
        self.method = method


    def parseRequest(self,queryStringObject):
        """
        Parse input OGC WPS request, which is either URL Query string or
        file object, e.g.  :mod:`sys.stdin`

        :param queryStringObject: string or file object with the request
        :returns: Dictionary of parsed input values
        :rtype: dict
        """

        # decide, which method to use
        # HTTP GET vs. HTTP POST
        if self.method == METHOD_GET:
            from Parser.Get import Get
            self.parser = Get(self)
        else:
            from pywps.Parser.Post import Post
            self.parser = Post(self)

        self.inputs = self.parser.parse(queryStringObject)
        return self.inputs

    def performRequest(self,inputs = None, processes=None):
        """Performs the desired WPS Request.

        :param inputs: idealy self.inputs (Default) object, result from
            parseRequest. Default is self.inputs
        :rtype: pywps.Wps.Response
        """

        if inputs == None:
            inputs = self.inputs

        # the modules are imported first, when the request type is known
        if inputs.has_key("request"):
            if inputs["request"]  == "getcapabilities":
                from pywps.Wps.GetCapabilities import GetCapabilities
                self.request = GetCapabilities(self,processes=processes)
            elif inputs["request"]  == "describeprocess":
                from pywps.Wps.DescribeProcess import DescribeProcess
                self.request = DescribeProcess(self, processes=processes)
            elif inputs["request"]  == "execute":
                from pywps.Wps.Execute import Execute
                self.request = Execute(self,processes=processes)
        elif inputs.has_key("wsdl"):
            inputs["version"]="1.0.0"
            from pywps.Wps.Wsdl import Wsdl
            self.request = Wsdl(self)
        else:
            raise Exceptions.InvalidParameterValue("request",
                "Unsupported request type '%s'" % inputs["request"])
        self.response = self.request.response
        return self.response

    def setLogFile(self, clear_handlers=False):
        """Set :data:`logFile`. Default is sys.stderr
        """
        global logFile
        fileName = config.getConfigValue("server","logFile")
        logLevel = eval("logging."+config.getConfigValue("server","logLevel").upper())
        format = "PyWPS [%(asctime)s] %(levelname)s: %(message)s"

        if clear_handlers and len(logging.root.handlers) > 0:
            # somehow need to clear handlers for async processes
            logging.root.handlers[:] = []
        
        if not fileName:
            logging.basicConfig(level=logLevel,format=format)
        else:
            logging.basicConfig(filename=fileName,level=logLevel,format=format)
            logFile = open(fileName, "a")


def debug(debug,code="Debug"):
    """Print debug argument to standard error

    .. note:: Deprecated from 3.2, use ::

            import logging
            LOGGER = logging.getLogger(__name__)
            ...
            LOGGER.debug("Hallo world")

        or similar. See Python module :mod:`logging` for more details

    :param debug: debugging text, which should be printed to the
        :data:`logFile`
    :type debug: string
    :param code: text, which will be printed to the
        :data:`logFile`
        direct after 'PyWPS' and before the debug text
    :type code: string.
    """
    LOGGER.debug(debug)

    #dbg = config.getConfigValue("server","debug")
    #if dbg == True or (type(dbg) == type("") and \
    #        dbg.lower() == "true") or int(dbg) != 0:
    #    print >>logFile, "PyWPS %s: %s" % (code,debug.__str__()[0:160]),
    #    if len(debug.__str__()) > 160:
    #        print >>logFile, "...",
    #    print >>logFile, "\n"

