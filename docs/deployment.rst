.. _deployment:

===============================
Deployment to production server
===============================

As already described in :ref:`installation` section, there is no deployment
needed for PyWPS, if using flask-based server. But this is not intended to be
used production environment. For production, `Apache httpd
<https://httpd.apache.org/>`_ or `nginx <https://nginx.org/>`_ servers are
probably going to be used. PyWPS is running as `WSGI
<https://wsgi.readthedocs.io/en/latest/>`_ application on those servers. We
relay on `Werkzeug <http://werkzeug.pocoo.org/>`_ library to do the work for us.

Deoploying individual instance of PyWPS
---------------------------------------

PyWPS should be in  installed in your computer (as per :ref:`installation`). As
next step, you can now create several instances of your WPS server.

We advice, that each instance of PyWPS should have it's own  directory, where
the WSGI file along with available processes could live. Therefore create
directory for PyWPS instance::

    $ sudo mkdir /var/www/pywps/

    # create directory for your processes too
    $ sudo mkdir /var/www/pywps/processes

.. note:: In this configuration example, we will assume, there is only one
        instance of PyWPS on the server.
        
Each instance is represented by single `WSGI` script (written in Python), which

    1. Loads the configuration files
    2. Serves processes
    3. Takes care about maximum number of concurent processes and similar

Creating `WSGI` instance of PyWPS
---------------------------------

There is example WSGI script distributed along with PyWPS-Demo as described in
:ref:`installation`. The script is actually straight forward - in fact, it's
just wrapper around PyWPS server with list of processes and configuration files
passed. Here example of PyWPS WSGI script::

    $ $EDITOR /var/www/pywps/pywps.wcgi

.. code-block:: python
    :linenos:

    #!/usr/bin/env python3

    from pywps.app.Service import Service

    # processes need to be installed in PYTHON_PATH
    from processes.sleep import Sleep
    from processes.ultimate_question import UltimateQuestion
    from processes.centroids import Centroids
    from processes.sayhello import SayHello
    from processes.feature_count import FeatureCount
    from processes.buffer import Buffer
    from processes.area import Area

    processes = [
        FeatureCount(),
        SayHello(),
        Centroids(),
        UltimateQuestion(),
        Sleep(),
        Buffer(),
        Area()
    ]

    # Service accepts two parameters:
    # 1 - list of process instances
    # 2 - list of configuration files
    application = Service(
        processes,
        ['/var/www/pywps/pywps.cfg']
    )

.. note:: The WSGI script is using ideal state: that you have already some
        processes at hand and can directly include them. Also it assumes, that
        the configuration file already exists - which is not the case yet.

        Configuration is described in next chapter (:ref:`configuration`), as
        well as process creation and deployment (:ref:`process`).

Deployment on Apache2 httpd server
----------------------------------

First, the wsgi module must be installed and enabled::

    $ sudo apt-get install libapache2-mod-wsgi
    $ sudo a2enmod wsgi

You then can edit your site configuration file
(`/etc/apache2/sites-enabled/yoursite.conf`) and add following::

        # PyWPS-4
        WSGIDaemonProcess pywps user=www-data group=www-data processes=2 threads=5
        WSGIScriptAlias /pywps /var/www/pywps/pywps.wsgi

        <Directory /home/jachym/www/htdocs/wps/>
            WSGIScriptReloading On
            WSGIProcessGroup group
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>

.. note:: `WSGIScriptAlias` points to created `pywps.wsgi` script we have
        created - it will be available under the url http://localhost/pywps

And of course restart the server::
    
    $ sudo service apache2 restart


Deployment on nginx
-------------------

.. note:: We are currently missing documentation about `nginx` deployment.
        Please help us with documentation about nginx deployment of PyWPS.

You should be able to deploy PyWPS on nginx as standard WSGI application. The
best documentation is probably to be found at `Readthedocs
<http://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html>`_.

.. _deployment-testing:

Testing PyWPS instance deployment
---------------------------------

.. note:: For purpose of this documentation, we are going to assume, that you've
        installed PyWPS on `localhost` server domain name.

As stated, before, PyWPS should be available at http://localhost/pywps, we now
can visit the url (or use `wget`)::

    # the --content-error parameter makes sure, error response is displayed
    $ wget --content-error -O - "http://localhost/pywps"

The result should be XML-encoded error message.

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!-- PyWPS 4.0.0-alpha2 -->
    <ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">
        <ows:Exception exceptionCode="MissingParameterValue" locator="service" >
            <ows:ExceptionText>service</ows:ExceptionText>
        </ows:Exception>
    </ows:ExceptionReport>

The server responded with :py:class:`pywps.exceptions.MissingParameterValue` exception, telling
us, that the parameter `service` was not set.

This is complient with the OGC WPS standard, since each request mast have at
least `service` and `request` parameters.

We can say for now, that PyWPS instance is properly deployed on the server,
since it returns propper exception report.

We now have to configure the instance by editing the `pywps.cfg` file and add
some processes.
