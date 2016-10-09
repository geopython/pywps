#!/usr/bin/env python
##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################

"""
PyWPS wsgi script

    SetHandler python-program
    PythonHandler wps
    PythonDebug On
    PythonPath "sys.path+['/usr/local/pywps-VERSION/']"
    PythonAutoReload On

.. moduleauthor: Jachym Cepicky jachym bnhelp cz
"""

import pywps
from pywps.Exceptions import *


def application(environ, start_response):

    status = '200 OK'
    response_headers = [('Content-type', 'text/xml')]

    inputQuery = None
    if environ.get("REQUEST_METHOD", '') == "GET":
        inputQuery = environ.get("QUERY_STRING")
    elif "wsgi.input" in environ:
        inputQuery = environ.get('wsgi.input')

    response = ''
    try:
        if not inputQuery:
            raise NoApplicableCode("No query string found.")

        # create the WPS object
        wps = pywps.Pywps(environ["REQUEST_METHOD"], environ.get("PYWPS_CFG"))
        if wps.parseRequest(inputQuery):
            pywps.debug(wps.inputs)
            wps.performRequest(processes=environ.get("PYWPS_PROCESSES"))
            response_headers = [('Content-type', wps.request.contentType)]
            response = wps.response

    except WPSException, e:
        response = str(e)
    except Exception, e:
        response = str(e)

    start_response(status, response_headers)
    return response


if __name__ == '__main__':

    import os

    # import processes from the tests directory
    os.environ["PYWPS_PROCESSES"] =  os.path.join(
            os.path.split(
                os.path.dirname(
                    pywps.__file__
            )
        )[0],"tests","processes")

    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8081, application)
    srv.serve_forever()
