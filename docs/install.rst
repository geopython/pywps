====================
PyWPS-4 Installation
====================


.. note:: PyWPS-4 is not tested on MS Windows platform. Please join the
    development, if you need this platform to be supported. It's mainly because
    lack of multiprocessing library.  It is used to process asynchronous
    execution, i.e., when making requests storing the response document and
    updating a status document displaying the progress of execution.


Dependencies
~~~~~~~~~~~~

In the command line tool::

    $ sudo apt-get install git python-gdal python-pip
    $ sudo apt-get install python-dev libxml2-dev libxslt1-dev zlib1g-dev libpq-dev
    $ sudo apt install apache2
    $ sudo apt-get install postgresql postgresql-contrib
    $ sudo pip install virtualenv

Create a virtual enviroment and clone the PyWPS project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the command line tool::

    $ sudo virtualenv /var/www/gsoc-pywps-env
    $ cd /var/www/gsoc-pywps-env
    $ source bin/activate

Clone the PyWPS and an example application into the virtual enviroment::

    $ sudo git clone https://github.com/jan-rudolf/pywps
    $ sudo git clone https://github.com/jan-rudolf/gsoc-pywps-app

Change ownership and group permission according to your user account, replace the string user with your username::

    $ sudo chown -R user:user /var/www/gsoc-pywps-env


PyWPS-4
~~~~~~~

The easiest way to install PyWPS-4 is using the Python Package Index (PIP). 
It fetches the source code from the repository and installs it automatically in the system.
This might require superuser permissions (e.g. *sudo* in Debian based systems)::

    $ sudo pip install -e git+https://github.com/pywps/pywps-4.git@master#egg=pywps-dev

In alternative PyWPS-4 can be installed manually.
It requires the cloning of the source code from the repository and then the usage of the *setup.py* script.
An example again for Debian based systems (note the usage of *sudo* for install)::

    $ git clone https://github.com/pywps/pywps-4.git

    $ cd pywps-4/

Then install deps using pip::

    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt  # for developer tasks

And install PyWPS system-wide::

    $ sudo python setup.py install

The demo service
~~~~~~~~~~~~~~~~

To use PyWPS-4 the user must code processes and publish them through a service.
A demo service is available that makes up a good starting point for first time users.
It can be cloned directly into the user area:

    $ git clone https://github.com/pywps/pywps-4-demo.git

It may be run right away through the *demo.py* script. 
First time users should start by studying the demo project structure and then code their own processes.

Full more details please consult the :ref:`process` section.
