PyWPS and WSGI
**************

For more detailed informations about WSGI, visit their `homepage <http://wsgi.org/wsgi/>_`
In general wsgi is prefered before mod_python mode

* Install `mod_wsgi` for Apache server (if you are using it)
* There is the `webservices/wsgi/wsgiwps.py` script, which provides the
  WSGI interface
* Configure apache server to something similar as::
    
     SetEnv PYTHONPATH /usr/local/src/pywps/ # is not installed the 'clean' way
     SetEnv PYWPS_CFG /usr/local/src/pywpsworkdir/pywps.cfg
     SetEnv PYWPS_PROCESSES /usr/local/src/pywpsworkdir/processes
    <Directory /usr/local/src/pywps/>
        Order allow,deny
        Allow from all
    </Directory>
    WSGIScriptAlias /wps /usr/local/src/pywps/webservices/wsgi/wpswsgi.py
