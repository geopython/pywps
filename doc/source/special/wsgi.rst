PyWPS and WSGI
**************

For more detailed information about WSGI, please visit their `website <http://wsgi.org/wsgi/>_`.
In general WSGI is preferred over mod_python mode.

* Install `mod_wsgi` for Apache server (if you are using it)
* Locate `webservices/wsgi/wsgiwps.py` which provides the WSGI interface
* Configure Apache server to something similar as::
    
     SetEnv PYTHONPATH /usr/local/src/pywps/ # is not installed the 'clean' way
     SetEnv PYWPS_CFG /usr/local/src/pywpsworkdir/pywps.cfg
     SetEnv PYWPS_PROCESSES /usr/local/src/pywpsworkdir/processes
    <Directory /usr/local/src/pywps/>
        Order allow,deny
        Allow from all
    </Directory>
    WSGIScriptAlias /wps /usr/local/src/pywps/webservices/wsgi/wpswsgi.py
