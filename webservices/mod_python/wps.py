##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################
"""
PyWPS mod_python script

Do not forget to add following configuration to your .htaccess file or
server configuration file::

    SetEnv PYWPS_PROCESSES /usr/local/wps/processes/
    SetEnv PYWPS_CFG /usr/local/wps/pywps.cfg
    SetHandler python-program
    PythonHandler wps
    PythonDebug On
    PythonPath "sys.path+['/usr/local/pywps-VERSION/']"
    PythonAutoReload On

.. moduleauthor: Jachym Cepicky jachym bnhelp cz
"""


from mod_python import apache
import pywps
import pywps.response
from pywps.Exceptions import *
import traceback
import os

#from pywps.Exceptions import *

def handler(req):

    inputQuery = None
    if req.method == "GET":
        inputQuery = req.args
    else:
        inputQuery = req

    if not inputQuery:
        err =  NoApplicableCode("No query string found.")
        pywps.response.response(err,req)
        return apache.OK

    # set PYWPS_CFG and PYWPS_PROCESSES environment variable, which can not
    # bee seen from mod_python
    env_vars = req.subprocess_env.copy()
    if env_vars.has_key("PYWPS_CFG"):
        os.environ["PYWPS_CFG"] = env_vars["PYWPS_CFG"]
    if env_vars.has_key("PYWPS_PROCESSES"):
        os.environ["PYWPS_PROCESSES"] = env_vars["PYWPS_PROCESSES"]

    # create the WPS object
    try:
        wps = pywps.Pywps(req.method)
        if wps.parseRequest(inputQuery):
            pywps.debug(wps.inputs)
            wps.performRequest()
            pywps.response.response(wps.response, req,
                    wps.parser.isSoap, self.wps.parser.isSoapExecute,contentType = wps.request.contentType)
            return apache.OK
    except WPSException,e:
        pywps.response.response(e, req) 
        return apache.OK
    except Exception, e:
        req.content_type = "text/plain"
        traceback.print_exc(file = req)
        return apache.OK
