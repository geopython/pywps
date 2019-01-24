.. _installation:

Installation
============

.. note:: PyWPS is not tested on the MS Windows platform. Please join the
    development team if you need this platform to be supported. This is mainly 
    because of the lack of a multiprocessing library.  It is used to process 
    asynchronous execution, i.e., when making requests storing the response 
    document and updating a status document displaying the progress of 
    execution.


Dependencies and requirements
-----------------------------

PyWPS runs on Python 2.7, 3.3 or higher. PyWPS is currently tested and
developed on Linux (mostly Ubuntu).  In the documentation we take this 
distribution as reference.

Prior to installing PyWPS, Git and the Python bindings for GDAL must be
installed in the system.  In Debian based systems these packages can be
installed with a tool like *apt*::

    $ sudo apt-get install git python-gdal

Alternatively, if GDAL is already installed on your system you can
install the GDAL Python bindings via pip with::

    $ pip install GDAL==1.10.0 --global-option=build_ext --global-option="-I/usr/include/gdal"

Download and install
--------------------

Using pip
        The easiest way to install PyWPS is using the Python Package Index
        (PIP).  It fetches the source code from the repository and installs it
        automatically in the system.  This might require superuser permissions
        (e.g. *sudo* in Debian based systems)::

            $ sudo pip install -e git+https://github.com/geopython/pywps.git@master#egg=pywps-dev

.. todo::

  * document Debian / Ubuntu package support


Manual installation
        Manual installation of PyWPS requires `downloading <https://pywps.org/download>`_ the
        source code followed by usage of the `setup.py` script.  An example again for Debian based systems (note
        the usage of `sudo` for install)::

            $ tar zxf pywps-x.y.z.tar.gz
            $ cd pywps-x.y.z/

        Then install the package dependencies using pip::

            $ pip install -r requirements.txt
            $ pip install -r requirements-gdal.txt  # for GDAL Python bindings (if python-gdal is not already installed by `apt-get`)
            $ pip install -r requirements-dev.txt  # for developer tasks

        To install PyWPS system-wide run::

            $ sudo python setup.py install

For Developers
        Installation of the source code using Git and Python's virtualenv tool::

            $ virtualenv my-pywps-env
            $ cd my-pywps-env
            $ source bin/activate
            $ git clone https://github.com/geopython/pywps.git
            $ cd pywps

        Then install the package dependencies using pip as described in the Manual installation section. To install
        PyWPS::

            $ python setup.py install

        Note that installing PyWPS via a virtualenv environment keeps the installation of PyWPS and its
        dependencies isolated to the virtual environment and does not affect other parts of the system.  This
        installation option is handy for development and / or users who may not have system-wide administration
        privileges.

.. _flask:

The Flask service and its sample processes
------------------------------------------

To use PyWPS the user must code processes and publish them through a service.
An example service is available that makes up a good starting point for first time
users. It launches a very simple built-in server (relying on the `Flask Python
Microframework <http://flask.pocoo.org/>`_), which is good enough for testing but probably not
appropriate for production.  This example service can be cloned directly into the user
area::

    $ git clone https://github.com/geopython/pywps-flask.git

It may be run right away through the `demo.py` script.  First time users should
start by studying the structure of this project and then code their own processes.

There is also an example service

Full more details please consult the :ref:`process` section. The example service 
contains some basic processes too, so you could get started with some examples 
(like `area`, `buffer`, `feature_count` and `grassbuffer`). These processes are 
to be taken just as inspiration and code documentation - most of them do not
make any sense (e.g. `sayhello`).
