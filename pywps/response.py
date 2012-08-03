"""Module for designed for printing any kind of response. CGI,
mod_python, Java Servlet and possibly others, which will come in the
future

.. data:: EMPTYPARAMREGEX

    Regular expression for empty parameter identificaion

"""

import types
from sys import stdout as STDOUT
from sys import stderr as STDERR
import re, logging, cStringIO
from pywps import Exceptions
from os import name as OSNAME
from pywps import Soap 
import pywps.Ftp



def response(response,targets,soapVersion=None,isSoap=False,isSoapExecute=False,contentType="application/xml",isPromoteStatus=False):
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
        response = soap.getResponse(response,soapVersion,isSoapExecute,isPromoteStatus)

    if isinstance(response,Exceptions.WPSException):
        response = response.__str__()



    # for each file in file descriptor
    for f in targets:

        # consider, if this CGI, mod_python or Java requested output
        # mod_python here
        if repr(type(f)) == "<type 'mp_request'>":
            _printResponseModPython(f,response,contentType)

        # file object (output, or sys.stdout)
        elif types.FileType == type(f):
            _printResponseFile(f,response,contentType)

        # pywps.Ftp.FTP object 
        elif isinstance(f, pywps.Ftp.FTP):
             _sendResponseFTP(f,response)
             logging.debug("Response document successfuly send to ftp server")

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

def _sendResponseFTP(ftpConnection, response):
    try:
        ftpConnection.connect()
        ftpConnection.relogin()
        # In case the response is a file, we can send it directly
        if type(response) == types.FileType:
            ftpConnection.storbinary("STOR " + ftpConnection.fileName, response)
        else:
            # We need a read-only memory file desciptor
            responseFile = cStringIO.StringIO(response)
            # Send the file to the ftp server use the filename specified in the FTP object
            ftpConnection.storbinary("STOR " + ftpConnection.fileName, responseFile)
            responseFile.close()
            
        ftpConnection.close()
    except Exception, e:
        traceback.print_exc(file=pywps.logFile)
        self.cleanEnv()
        raise pywps.NoApplicableCode("FTP error: " +  e.__str__())


def _printResponseJava( resp, response,contentType="application/xml"):
    if contentType:
        resp.setContentType(contentType)
    toClient = resp.getWriter()

    if type(response) == types.FileType:
        toClient.println(response.read())
    else:
        toClient.println(response)
