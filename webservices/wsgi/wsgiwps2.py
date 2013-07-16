#!/usr/bin/env python

"""
PyWPS wsgi script for gunicorn

    http://docs.gunicorn.org/en/latest/run.html

.. moduleauthor: Carsten Ehbrecht
"""

# Author:	Carsten Ehbrecht
#        	http://www.dkrz.de

import sys

#sys.path.append("/home/pingu/sandbox/climdaps/src/PyWPS")

import pywps
from pywps.Exceptions import *

import os

def dispatchWps(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type','text/xml')]
    start_response(status, response_headers)

    inputQuery = None
    if "REQUEST_METHOD" in environ and environ["REQUEST_METHOD"] == "GET":
        inputQuery = environ["QUERY_STRING"]
    elif "wsgi.input" in environ:
        inputQuery = environ['wsgi.input']

    if not inputQuery:
        err =  NoApplicableCode("No query string found.")
        return [err.getResponse()]

    try:
        # create the WPS object
        wps = pywps.Pywps(environ["REQUEST_METHOD"])
        if wps.parseRequest(inputQuery):
            pywps.debug(wps.inputs)
            wps.performRequest()
            return wps.response
        else:
            err = NoApplicableCode("you drive me nuts! %s" % (wps.UUID))
            return [err.getResponse()]
    except WPSException,e:
       return [e.getResponse()]
    except Exception, e:
        return [e.getResponse()]


