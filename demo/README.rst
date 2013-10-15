PyWPS-4 demo application
========================

This is a simple demo app written using PyWPS 4. It has been tested with
QGIS 1.8.


Installation
~~~~~~~~~~~~
The app depends on PyWPS and several other libraries that are listed in
``requirements.txt``. You can install them with pip::

    $ pip install -r requirements.txt
    $ pip install -e git+https://github.com/jachym/pywps-4.git@master#egg=pywps-dev


Running
~~~~~~~
Simply run the python file::

    $ python app.py

By default the app listens on port ``5000``. This can be changed via the
``$PORT`` environment variable.
