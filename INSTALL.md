PyWPS 4 Installation
========================

Dependencies:

	$ sudo apt-get install git python-lxml python-gdal python-werkzeug python-flask python-jsonschema python-unipath python-owslib


Install PyWPS 4:

	$ pip install -e git+https://github.com/jachym/pywps-4.git@master#egg=pywps-dev

	or

	$ pip install -e git+https://github.com/ldesousa/pywps-4.git@Testing#egg=pywps-ldesousa-dev


Run demo:

	$ python demo.py