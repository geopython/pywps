"""Module for designed for printing any kind of response. CGI,
mod_python, Java Servlet and possibly others, which will come in the
future

.. data:: EMPTYPARAMREGEX

    Regular expression for empty parameter identificaion

"""

import types
from sys import stdout as STDOUT
from sys import stderr as STDERR
import re
from pywps import Exceptions

EMPTYPARAMREGEX = re.compile('( \w+="")|( \w+="None")')

def response(response,targets,isSoap=False,contentType="text/xml"):
    """
    Print response to files given as input parameter.

    :param targets: file object or list of file objects. File name,
        mod_python request or java servlet response
    :type targets: string or list, 
    :param isSoap: print the response in SOAP envelope
    :type isSoap: bool
    :param response: the response object. 
    """


    # convert single file to array
    if type(targets) != type([]):
        targets = [targets]

    if isSoap:
        soap = Soap.SOAP()
        response = soap.getResponse(response)

    if isinstance(response,Exceptions.WPSException):
        response = response.__str__()

    response = re.sub(EMPTYPARAMREGEX,"",response)

    # for each file in file descriptor
    for f in targets:

        # consider, if this CGI, mod_python or Java requested output
        # mod_python here
        if repr(type(f)) == "<type 'mp_request'>":
            _printResponseModPython(f,response,contentType)

        # file object (output, or sys.stdout)
        elif types.FileType == type(f):
            _printResponseFile(f,response,contentType)

        # java servlet response
        elif repr(type(f)).find("org.apache.catalina.connector") > -1 or \
                repr(f) == "<__main__.DummyHttpResponse instance at 0xc14>": 
            _printResponseJava(f,response,contentType)

def _printResponseModPython(request, response, contentType="text/xml"):

    if contentType:
        request.content_type = contentType
    request.write(response)

def _printResponseFile(fileOut, response, contentType="text/xml"):

    if fileOut == STDOUT and contentType:
        print "Content-Type: %s\n" % contentType
    elif fileOut.closed:
        fileOut = open(fileOut.name,"w")

    fileOut.write(response)
    fileOut.flush()

    if fileOut != STDOUT:
        f.close()

def _printResponseJava( resp, response,contentType="text/xml"):
    if contentType:
        resp.setContentType(contentType)
    toClient = resp.getWriter()
    toClient.println(response)

