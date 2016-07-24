====================
PyWPS-4 Installation
====================

.. note:: PyWPS-4 is not tested on MS Windows platform. Please join the
    development, if you need this platform to be supported. It's mainly because
    lack of multiprocessing library.  It is used to process asynchronous
    execution, i.e., when making requests storing the response document and
    updating a status document displaying the progress of execution.


Dependencies
============

In the command line::

    $ sudo apt-get install git python-gdal python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libpq-dev apache2 postgresql postgresql-contrib
    $ sudo pip install virtualenv


Installation
============

Standard installation is standard Python package installation. If you want to contribute or work on PyWPS, installation in the develop mode is also described.

Standard
--------

In the command line::

    $ sudo virtualenv /var/www/gsoc-pywps-env
    $ cd /var/www/gsoc-pywps-env
    $ source bin/activate

Clone the PyWPS and the example application into the activated virtual enviroment::

    $ sudo git clone https://github.com/jan-rudolf/pywps
    $ sudo git clone https://github.com/jan-rudolf/gsoc-pywps-app

Change ownership and group permission according to your user account, replace the string user with your username::

    $ sudo chown -R <user>:<user> /var/www/gsoc-pywps-env

Install Python packages and install the PyWPS::

    $ cd pywps
    $ pip install -r requirements.txt
    $ python setup.py install

Create /tmp/outputs directory and change group and owner to the user that runs the Apache, that is www-data by default::

    $ sudo mkdir /tmp/outputs
    $ sudo chown www-data:www-data /tmp/outputs

PyWPS is installed and you can remove it now::
    
    $ cd ..    
    $ sudo rm -Rf pywps


Develop 
-------

In the command line::

    $ sudo virtualenv /var/www/gsoc-pywps-env
    $ cd /var/www/gsoc-pywps-env
    $ source bin/activate

Clone the PyWPS and the example application into the activated virtual enviroment::

    $ sudo git clone https://github.com/jan-rudolf/pywps
    $ sudo git clone https://github.com/jan-rudolf/gsoc-pywps-app

Change ownership and group permission according to your user account, replace the string user with your username::

    $ sudo chown -R <user>:<user> /var/www/gsoc-pywps-env

Install Python packages and install the PyWPS::

    $ cd pywps
    $ pip install -r requirements.txt
    $ python setup.py develop

Create /tmp/outputs directory and change group and owner to the user that runs the Apache, that is www-data by default::

    $ sudo mkdir /tmp/outputs
    $ sudo chown www-data:www-data /tmp/outputs


Apache
======

In the case you want to server PyWPS on the Apache web server, here is an example of the virtual host configuration file. All paths and names are according the Installation subsection.  

.. code::
   
    <VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        ServerName pywps.loc
        ServerAlias www.pywps.loc

        ServerAdmin webmaster@localhost
        #DocumentRoot /var/www/html

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf

        WSGIProcessGroup pywps.loc
        WSGIDaemonProcess pywps.loc processes=2 threads=15 display-name=%{GROUP} 
        WSGIScriptAlias / /var/www/gsoc-pywps-env/gsoc-pywps-app/wsgi.py

        Alias "/outputs" "/tmp/outputs/"
        <Directory "/tmp/outputs">
            Require all granted
        </Directory>

        <Directory /var/www/gsoc-pywps-env/gsoc-pywps-app>
            Order allow,deny
            Allow from all 
        </Directory> 
    </VirtualHost>



Database
========

TBA


SQLite
------

TBA


PostgreSQL
----------

This describe how to create a database and set it up with the PyWPS.

In the command line, switch to postgres user::

   $ sudo su postgre

Create a user for the database system::

   $ createuser --pwprompt <user>

Create a database with the utf-8 encoding::

   $ createdb -O<user> -Eutf-8 <database_name>

dskfjsdlkfj::

   $ exit



