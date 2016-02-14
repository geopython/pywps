import os
from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory, make_response
import pywps
from pywps.Exceptions import *
import pywps.Exceptions
from pywps.Exceptions import NoApplicableCode

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

@app.route('/')
def index():
    #start_response(status, response_headers)


    response_headers = [('Content-type','text/xml')]
    inputQuery = None
    if request.method == 'GET':
        inputQuery = str(request.args)
        print inputQuery
    elif request.method == 'POST':
        #inputQuery = environ['wsgi.input']
        inputQuery = request.args
    

    if not request.args:
        print pywps.Exceptions
        err =  pywps.Exceptions.NoApplicableCode("No query string found.")
        resp = make_response(err, 200)
        resp.headers['mime-type'] = 'text/xml'
        resp.headers['content-type'] = 'text/xml'
        return [err.getResponse()]

    # create the WPS object
    try:
        #resp = make_response(err, 200)
        #resp.headers['mime-type'] = 'text/xml'
        #resp.headers['content-type'] = 'text/xml'
        wps = pywps.Pywps(request.method)
        #if wps.parseRequest(inputQuery):
        pywps.debug(inputQuery)
        wps.performRequest()
        return wps.response
    except WPSException,e:
        return [e]
    except Exception, e:
        return [e]

if __name__ == '__main__':
    app.run()
