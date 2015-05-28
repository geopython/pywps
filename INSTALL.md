PyWPS 4 Installation
====================

Dependencies
------------

To use PyWPS 4 the third party libraries GIT and GDAL need to be installed in the system.

In Debian based systems this can be installed with

    $ sudo apt-get install git python-gdal
    
In Windows systems this can be installed by

    Installing a GIT client (e.g. GitHub for Windows)
    
Install PyWPS 4
----------------

Using Pip 

	$ sudo pip install -e git+https://github.com/jachym/pywps-4.git@master#egg=pywps

or manual installation

    $ git clone https://github.com/jachym/pywps-4.git
    
    $ cd pywps-4/
    
    $ sudo python setup.py install

Install demo service
--------------------

	$ git clone git@github.com:ldesousa/pywps-4-demo.git pywps-4-demo
	

Run demo
--------

	$ python demo.py
	
Access demo
-----------

	http://localhost:5000