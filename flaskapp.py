import os
from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory, make_response
import pywps
import pywps.Exceptions
from pywps.Exceptions import *

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

@app.route('/')
def index():
    #start_response(status, response_headers)


    response_headers = [('Content-type','text/xml')]
    inputQuery = None
    if request.method == 'GET':
        inputQuery = request.query_string
    elif request.method == 'POST':
        #inputQuery = environ['wsgi.input']
        inputQuery = request.args


    if not request.args:
        err =  pywps.Exceptions.NoApplicableCode("No query string found.")
        resp = make_response(err.getResponse(), 200)
        resp.headers['mime-type'] = 'text/xml'
        resp.headers['content-type'] = 'text/xml'
        return resp

    # create the WPS object
    try:
        wps = pywps.Pywps(request.method)
        if wps.parseRequest(inputQuery):
            wps.performRequest()
        resp = make_response(wps.response, 200)
        resp.headers['content-type'] = 'text/xml'
        return resp
    except WPSException, e:
            print "########", dir(e)
            resp = make_response(e.getResponse(), 200)
            resp.headers['content-type'] = 'text/xml'
            return resp
    except Exception, e:
        resp = make_response(str(e), 200)
        resp.headers['content-type'] = 'text/xml'
        return resp

if __name__ == '__main__':
    app.run()
