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
from os import name as OSNAME
from pywps import Soap 

EMPTYPARAMREGEX = re.compile('( \w+="")|( \w+="None")')

def response(response,targets,isSoap=False,contentType="application/xml"):
    """
    Print response to files given as input parameter.

    :param targets: file object or list of file objects. File name,
        mod_python request or java servlet response
    :type targets: string or list, 
    :param isSoap: print the response in SOAP envelope
    :type isSoap: bool
    :param response: the response object 
    :type response: file or string
    """


    # convert single file to array
    if type(targets) != type([]):
        targets = [targets]

    if isSoap:
        soap = Soap.SOAP()
        response = soap.getResponse(response)

    if isinstance(response,Exceptions.WPSException):
        response = response.__str__()


    if type(response) != types.FileType:
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
        elif OSNAME == "java" :
            _printResponseJava(f,response,contentType)

        # close and open again, if it is a file
        if type(response) == types.FileType:
            response.close()
            response = open(response.name,"rb")

def _printResponseModPython(request, response, contentType="application/xml"):

    if contentType:
        request.content_type = contentType

    if type(response) == types.FileType:
        request.write(response.read())
    else:
        request.write(response)

def _printResponseFile(fileOut, response, contentType="application/xml"):

    if fileOut == STDOUT and contentType:
        print "Content-Type: %s\n" % contentType
    elif fileOut.closed:
        fileOut = open(fileOut.name,"w")

    if type(response) == types.FileType:
        fileOut.write(response.read())
    else:
        fileOut.write(response)
    fileOut.flush()

    if fileOut != STDOUT:
        fileOut.close()

def _printResponseJava( resp, response,contentType="application/xml"):
    if contentType:
        resp.setContentType(contentType)
    toClient = resp.getWriter()

    if type(response) == types.FileType:
        toClient.println(response.read())
    else:
        toClient.println(response)

