============
PyWPS-4 Installation
============

PyWPS-4 is under development and there is no stable release yet.

Dependencies
~~~~~~~~~~~~

To install PyWPS-4 you need Python 2.7, 3.3 or newer.
GIT and GDAL need to be installed in the system::

    $ sudo apt-get install git python-gdal

Installing from the source repository using PIP::

    $ sudo pip install -e git+https://github.com/jachym/pywps-4.git@master#egg=pywps-dev

Or manual installation::

    $ git clone https://github.com/jachym/pywps-4.git

    $ cd pywps-4/

    $ sudo python setup.py install

This automatically installs the dependencies
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