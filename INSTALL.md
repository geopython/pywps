PyWPS 4 Installation
====================

Dependencies on Debian based systems
------------------------------------

	$ sudo apt-get install git python-lxml python-gdal python-werkzeug python-flask python-jsonschema python-unipath python-owslib

Dependencies on other systems
-----------------------------

	1. Install Git
	
	2. Install GDAL
	
	3. Install Python libraries

Install PyWPS 4
----------------

Manual installation

    $ git clone https://github.com/jachym/pywps-4.git
    
    $ cd pywps-4/
    
    $ sudo python setup.py install
    
or using Pip 

	$ sudo pip install -e git+https://github.com/jachym/pywps-4.git@master#egg=pywps


Install demo service
--------------------

	$ git clone git@github.com:ldesousa/pywps-4-demo.git pywps-4-demo
	

Run demo
--------

	$ python demo.py
	
Access demo
-----------

	http://localhost:5000