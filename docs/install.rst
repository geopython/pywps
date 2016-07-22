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

PyWPS-4 runs on Python 2.7, 3.3 or newer.

Prior to installing PyWPS-4, Git and the Python bindings for GDAL must be
installed in the system.  In Debian based systems these packages can be
installed with a tool like *apt*::

    $ sudo apt-get install git python-gdal


PyWPS-4
~~~~~~~

The easiest way to install PyWPS-4 is using the Python Package Index (PIP).  It
fetches the source code from the repository and installs it automatically in the
system.  This might require superuser permissions (e.g. *sudo* in Debian based
systems)::

    $ sudo pip install -e git+https://github.com/geopython/pywps.git@master#egg=pywps-dev

In alternative PyWPS-4 can be installed manually.
It requires the cloning of the source code from the repository and then the
usage of the `setup.py` script.  An example again for Debian based systems (note
the usage of `sudo` for install)::

    $ git clone https://github.com/geopython/pywps.git pywps-4

    $ cd pywps-4/

Then install deps using pip::

    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt  # for developer tasks

And install PyWPS system-wide::

    $ sudo python setup.py install

The demo service
~~~~~~~~~~~~~~~~

To use PyWPS-4 the user must code processes and publish them through a service.
A demo service is available that makes up a good starting point for first time
users. This launches a very simple builtin server (`flask
<http://flask.pocoo.org/>`_), which is good enough for testing but probably not
what you want to use in production.  It can be cloned directly into the user
area::

    $ git clone https://github.com/geopython/pywps-demo.git

It may be run right away through the `demo.py` script.  First time users should
start by studying the demo project structure and then code their own processes.

Full more details please consult the :ref:`process` section.
