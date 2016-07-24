====================
PyWPS-4 Installation
====================

.. note:: This installation documentation was tested on the Ubuntu 14.04 LTS operating system.

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

Normal installation is standard Python package installation. If you want to contribute or work on PyWPS, the installation in the develop mode is also described.

Normal installation
-------------------

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

Create **/tmp/outputs** directory and change group and owner to the user that runs the Apache, that is **www-data** by default::

    $ sudo mkdir /tmp/outputs
    $ sudo chown www-data:www-data /tmp/outputs

PyWPS is installed and you can remove it now::
    
    $ cd ..    
    $ sudo rm -Rf pywps


Develop installation
--------------------

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

Create **/tmp/outputs** directory and change group and owner to the user that runs the Apache, that is **www-data** by default::

    $ sudo mkdir /tmp/outputs
    $ sudo chown www-data:www-data /tmp/outputs


Database
========

This section describes how to setup and connect SQLite and PostgreSQL with the PyWPS. 

More about how to connect other engines in the `SQLAlchemy Documentation <http://docs.sqlalchemy.org/en/latest/core/engines.html>`_.


SQLite
------

Change the **SQLAlchemyDatabaseUri** in the PyWPS configuration file under the **server** section::

   SQLAlchemyDatabaseUri=sqlite:////absolute/path/to/<database_name>

Create database tables by the GET HTTP request to::

   http://<URL_address>/create-db


PostgreSQL
----------

System configuration
~~~~~~~~~~~~~~~~~~~~

In the command line, switch to the postgres user::

   $ sudo su postgres

Create a user for the database system, fill your username::

   $ createuser --pwprompt <username>

Create a database with the utf-8 encoding, fill your username from the previous step and the desired database name::

   $ createdb -O<username> -Eutf-8 <database_name>

Exit the postgres's user prompt::

   $ exit

Edit the table, that looks like the one below, so that the **METHOD** column has only **md5** entries (in case you have a different version of PostgreSQL, edit the path to the file with proper version)::

   $ sudo $EDITOR /etc/postgresql/9.3/main/pg_hba.conf

+------------+------------+-----------+--------------+---------+ 
| TYPE       | DATABASE   | USER      | ADDRESS      | METHOD  |
+============+============+===========+==============+=========+
| local      | all        | all       |              | peer    |
+------------+------------+-----------+--------------+---------+
| host       | all        | all       | 127.0.0.1/32 | md5     |
+------------+------------+-----------+--------------+---------+
| host       | all        | all       | ::1/128      | md5     |
+------------+------------+-----------+--------------+---------+ 

Restart the PostgreSQL service::

   $ sudo service postgresql restart


PyWPS's configuration file setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change the **SQLAlchemyDatabaseUri** in the PyWPS configuration file under the **server** section::

   SQLAlchemyDatabaseUri=postgresql://<username>@localhost/<database_name>

Create database tables by the GET HTTP request to::

   http://<URL_address>/create-db


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



