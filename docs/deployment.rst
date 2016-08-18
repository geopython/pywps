.. _deployment:

=================================
Deployment to a production server
=================================

As already described in the :ref:`installation` section, no specific deployment
procedures are for PyWPS when using flask-based server. But this formula is not 
intended to be used in a production environment. For production, `Apache httpd
<https://httpd.apache.org/>`_ or `nginx <https://nginx.org/>`_ servers are
more advised. PyWPS is runs as a `WSGI
<https://wsgi.readthedocs.io/en/latest/>`_ application on those servers. PyWPS
relies on the `Werkzeug <http://werkzeug.pocoo.org/>`_ library for this purpose.

Deoploying an individual PyWPS instance
---------------------------------------

PyWPS should be installed in your computer (as per the :ref:`installation` 
section). As a following step, you can now create several instances of your WPS 
server.

It is advisable for each PyWPS instance to have its own directory, where the 
WSGI file along with available processes should reside. Therefore create a new
directory for the PyWPS instance::

    $ sudo mkdir /var/www/pywps/

    # create a directory for your processes too
    $ sudo mkdir /var/www/pywps/processes

.. note:: In this configuration example it is assumed that there is only one
        instance of PyWPS on the server.
        
Each instance is represented by a single `WSGI` script (written in Python), 
which:

    1. Loads the configuration files
    2. Serves processes
    3. Takes care about maximum number of concurrent processes and similar

Creating a PyWPS `WSGI` instance
--------------------------------

An example WSGI script is distributed along with PyWPS-Demo service, as 
described in the :ref:`installation` section. The script is actually 
straightforward - in fact, it's a just wrapper around the PyWPS server with a 
list of processes and configuration files passed as arguments. Here is an 
example of a PyWPS WSGI script::

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

.. note:: The WSGI script is assuming that there are already some
        processes at hand that can be directly included. Also it assumes, that
        the configuration file already exists - which is not the case yet.

        The Configuration is described in next chapter (:ref:`configuration`), 
        as well as process creation and deployment (:ref:`process`).

Deployment on Apache2 httpd server
----------------------------------

First, the WSGI module must be installed and enabled::

    $ sudo apt-get install libapache2-mod-wsgi
    $ sudo a2enmod wsgi

You then can edit your site configuration file
(`/etc/apache2/sites-enabled/yoursite.conf`) and add the following::

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

.. note:: `WSGIScriptAlias` points to the `pywps.wsgi` script created
        before - it will be available under the url http://localhost/pywps

And of course restart the server::
    
    $ sudo service apache2 restart


Deployment on nginx
-------------------

.. note:: We are currently missing documentation about `nginx`.
        Please help documenting the deployment of PyWPS to nginx.

You should be able to deploy PyWPS on nginx as a standard WSGI application. The
best documentation is probably to be found at `Readthedocs
<http://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html>`_.

.. _deployment-testing:

Testing the deployment of a PyWPS instance
------------------------------------------

.. note:: For the purpose of this documentation, it is assumed that you've
        installed PyWPS using the `localhost` server domain name.

As stated, before, PyWPS should be available at http://localhost/pywps, we now
can visit the url (or use `wget`)::

    # the --content-error parameter makes sure, error response is displayed
    $ wget --content-error -O - "http://localhost/pywps"

The result should be an XML-encoded error message.

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!-- PyWPS 4.0.0-alpha2 -->
    <ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">
        <ows:Exception exceptionCode="MissingParameterValue" locator="service" >
            <ows:ExceptionText>service</ows:ExceptionText>
        </ows:Exception>
    </ows:ExceptionReport>

The server responded with the :py:class:`pywps.exceptions.MissingParameterValue` 
exception, telling us that the parameter `service` was not set. This is  
compliant with the OGC WPS standard, since each request mast have at least the 
`service` and `request` parameters. We can say for now, that this PyWPS 
instance is properly deployed on the server, since it returns proper exception 
report.

We now have to configure the instance by editing the `pywps.cfg` file and adding
some processes.
