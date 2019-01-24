.. _deployment:

Deployment to a production server
=================================

As already described in the :ref:`installation` section, no specific deployment
procedures are for PyWPS when using flask-based server. But this formula is not 
intended to be used in a production environment. For production, `sudo service apache2 restartApache httpd
<https://httpd.apache.org/>`_ or `nginx <https://nginx.org/>`_ servers are
more advised. PyWPS is runs as a `WSGI
<https://wsgi.readthedocs.io/en/latest/>`_ application on those servers. PyWPS
relies on the `Werkzeug <http://werkzeug.pocoo.org/>`_ library for this purpose.

Deploying an individual PyWPS instance
--------------------------------------

PyWPS should be installed in your computer (as per the :ref:`installation` 
section). As a following step, you can now create several instances of your WPS 
server.

It is advisable for each PyWPS instance to have its own directory, where the 
WSGI file along with available processes should reside. Therefore create a new
directory for the PyWPS instance::

    $ sudo mkdir /path/to/pywps/

    # create a directory for your processes too
    $ sudo mkdir /path/to/pywps/processes

.. note:: In this configuration example it is assumed that there is only one
        instance of PyWPS on the server.
        
Each instance is represented by a single `WSGI` script (written in Python), 
which:

    1. Loads the configuration files
    2. Serves processes
    3. Takes care about maximum number of concurrent processes and similar

Creating a PyWPS `WSGI` instance
--------------------------------

An example WSGI script is distributed along with the pywps-flask service, as 
described in the :ref:`installation` section. The script is actually 
straightforward - in fact, it's a just wrapper around the PyWPS server with a 
list of processes and configuration files passed as arguments. Here is an 
example of a PyWPS WSGI script::

    $ $EDITOR /path/to/pywps/pywps.wsgi

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
        ['/path/to/pywps/pywps.cfg']
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

        # PyWPS
        WSGIDaemonProcess pywps home=/path/to/pywps user=www-data group=www-data processes=2 threads=5
        WSGIScriptAlias /pywps /path/to/pywps/pywps.wsgi process-group=pywps

        <Directory /path/to/pywps/>
            WSGIScriptReloading On
            WSGIProcessGroup pywps
            WSGIApplicationGroup %{GLOBAL}
            Require all granted
        </Directory>

.. note:: `WSGIScriptAlias` points to the `pywps.wsgi` script created
        before - it will be available under the url http://localhost/pywps

.. note:: Please make sure that the `logs`, `workdir`, and `outputpath` directories are writeable to the Apache user.
        The `outputpath` directory need also be accessible from the URL mentioned in `outputurl` configuration.

And of course restart the server::
    
    $ sudo service apache2 restart


Deployment on Nginx-Gunicorn
----------------------------

.. note:: We will use Greenunicorn  for pyWPS deployment, since it is a very simple to configurate server. 

   For difference between WSGI server consult:  `WSGI comparison <https://www.digitalocean.com/community/tutorials/a-comparison-of-web-servers-for-python-based-web-applications>`_.
   
   uWSGU is more popular than gunicorn, best documentation is probably to be found at `Readthedocs <https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html>`_.

We need nginx and gunicorn server::

   $ apt install nginx-full
   $ apt install gunicorn3

It is assumed that PyWPS  is installed in your system (if not see: ref:`installation`) and we will use pywps-flask as installation example.

First, cloning the pywps-flask example to the root / (you need to be sudoer or root to run the examples)::
   
   $ cd /
   $ git clone https://github.com/geopython/pywps-flask.git

Second, preparing the WSGI script for gunicorn. It is necessary that the 
WSGI script located in the pywps-flask service is identified as a python module by gunicorn, 
this is done by creating a link with .py extention to the wsgi file::  
   
   $ cd /pywps-flask/wsgi
   $ ln -s ./pywps.wsgi ./pywps_app.py 
   
Gunicorn can already be tested by setting python path on the command options::
   
   $ gunicorn3 -b 127.0.0.1:8081  --workers $((2*`nproc --all`)) --log-syslog  --pythonpath /pywps-flask wsgi.pywps_app:application   
  
The command will start a gunicorn instance on the localhost IP and port 8081, logging to systlog 
(/var/log/syslog), using pywps process folder /pywps-flask/processes and loading module wsgi.pywps_app and object/function application for WSGI.  

.. note::  Gunicorn uses a prefork model where the master process forks processes (workers) 
   that willl accept incomming connections. The --workers flag sets the number of processes, 
   the default values is 1 but the recomended value is 2 or 4 times the number of CPU cores.      

Next step is to configure NGINX,  by pointing to the WSGI server by changing the location paths of the  default  
site file but editing file /etc/nginx/sites-enabled as follows::: 
   
   server {
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name _;

        #better to redirect / to wps application
        location / {
        return 301 /wps;
        }

        location /wps {
                # with try_files active there will be problems
                #try_files $uri $uri/ =404;

                proxy_set_header Host $host;
                proxy_redirect          off;
                proxy_set_header        X-NginX-Proxy true;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_pass http://127.0.0.1:8081;
                }
   
   }
 
It is likely that part of the proxy configuration is already set on the file /etc/nginx/proxy.conf.  
Of course the necessatyrestart of nginx :: 
   
   $ service nginx restart
   
The service will now be available on the IP of the server or localhost ::
   
   http://localhost/wps?request=GetCapabilities&service=wps
 
The current gunicorn instance was launched by the user. In a production server it is necessary to set gunicorn as a service  

On ubuntu 16.04  the systemcltd system requires a service file that will start the gunicorn3 service. The service file (/lib/systemd/system/gunicorn.service)
has to be configure as follows::

   [Unit]
   Description=gunicorn3 daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   PIDFile=/var/run/gunicorn3.pid
   Environment=WORKERS=3
   ExecStart=/usr/bin/gunicorn3 -b 127.0.0.1:8081   --preload --workers $WORKERS --log-syslog --pythonpath /pywps-flask wsgi.pywps_app:application
   ExecReload=/bin/kill -s HUP $MAINPID
   ExecStop=/bin/kill -s TERM $MAINPID
   
   [Install]
   WantedBy=multi-user.target

And then enable the service and then reload the systemctl daemon::
   
   $ systemctl enable gunicorn3.service
   $ systemctl daemon-reload
   $ systemctl restart gunicorn3.service

And  to check that everything is ok::
   
   $ systemctl status gunicorn3.service

.. note::
   
   Todo NGIX + uWSGI


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
    <ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">
        <ows:Exception exceptionCode="MissingParameterValue" locator="service">
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
