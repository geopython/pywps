PyWPS 4 Installation
====================

Dependencies
------------

To use PyWPS 4 the third party libraries GIT and GDAL need to be installed in the system.

In Debian based systems these can be installed with:

    $ sudo apt-get install git python-gdal
    
In Windows systems a Git client should be installed (e.g. GitHub for Windows).
    
Install PyWPS 4
---------------

Using pip: 

    $ sudo pip install -e git+https://github.com/geopython/pywps.git@master#egg=pywps

Or in alternative install it manually:

    $ git clone https://github.com/geopython/pywps.git
    
    $ cd pywps/
    
    $ sudo python setup.py install

Install example service
-----------------------

    $ git clone https://github.com/geopython/pywps-flask.git pywps-flask
    

Run example service
-------------------

    $ python demo.py
    
Access example service
----------------------

    http://localhost:5000
