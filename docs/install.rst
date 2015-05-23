============
PyWPS-4 Installation
============

Note that PyWPS-4 is still under development, there is no stable release yet.


Dependencies
~~~~~~~~~~~~

PyWPS-4 runs on Python 2.7, 3.3 or newer.

Prior to installing PyWPS-4, Git and the Python bindings for GDAL must be installed in the system. 
In Debian based systems these packages can be installed with a tool like *apt*::

    $ sudo apt-get install git python-gdal


PyWPS-4
~~~~~~~

The easiest to install PyWPS-4 is using the Python Package Index (PIP). 
It fetches the source code from the repository and installs it automatically in the system.
This might require superuser permissions (e.g. *sudo* in Debian based systems)::

    $ sudo pip install -e git+https://github.com/jachym/pywps-4.git@master#egg=pywps-dev

In alternative PyWPS-4 can be installed manually.
It requires the cloning of the source code from the repository and then the usage of the *setup.py* script.
An example again for Debian based systems (note the usage of *sudo* for install)::

    $ git clone https://github.com/jachym/pywps-4.git

    $ cd pywps-4/

    $ sudo python setup.py install

During installation the following dependencies will be automatically installed:
*   lxml_
*   werkzeug_
*   unipath_
*   owslib_
*   jsonschema_

.. _lxml: http://lxml.de/
.. _werkzeug: http://werkzeug.pocoo.org/
.. _unipath: https://github.com/mikeorr/Unipath
.. _owslib: http://geopython.github.io/OWSLib/
.. _jsonschema: http://json-schema.org/


The demo service
~~~~~~~~~~~~~~~~

To use PyWPS-4 the user must code processes and publish them through a service.
A demo service is available that makes up a good starting point for first time users.
It can be cloned directly into the user area:

	$ git clone https://github.com/jachym/pywps-4-demo.git
	
It may be run right away through the *demo.py* script. 
First time users should start by studying the demo service structure and then code their own processes.

Full more details please consult the `process`_ section.