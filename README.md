# PyWPS 

PyWPS is an implementation of the Web Processing Service standard from
the Open Geospatial Consortium. PyWPS is written in Python.

[![Documentation Status](https://readthedocs.org/projects/pywps/badge/?version=latest)](http://pywps.readthedocs.org/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/geopython/pywps.png)](https://travis-ci.org/geopython/pywps)
[![PyPI](https://img.shields.io/pypi/dm/pywps.svg)]()
[![GitHub license](https://img.shields.io/github/license/geopython/pywps.svg)]()
[![Gitter Chat](http://img.shields.io/badge/chat-online-brightgreen.svg)](https://gitter.im/PyWPS)

# License

As of PyWPS 4.0.0, PyWPS is released under an
[MIT](https://en.wikipedia.org/wiki/MIT_License) license
(see [LICENSE.txt](LICENSE.txt)).

# Dependencies

See [requirements.txt](requirements.txt) file

# Run tests

Install and run [tox](http://testrun.org/tox/latest/):

```bash
pip install tox
tox
```

Or run the tests by hand, with either Python 2 or 3:

```bash
python tests/__init__.py
```

# Run web application

## Demo application

Clone PyWPS recursively with the demo application:

```bash
git clone --recursive git://github.com/geopython/pywps.git pywps-src
sudo python setup.py install
cd demo/
python demo.py
```
    
Or clone only demo app after having installed PyWPS:

```bash
git clone git://github.com/PyWPS/pywps-4-demo.git
cd demo/
python demo.py
```
 
## Apache configuration

1. Enable WSGI extension

2. Add configuration:

    ```apache
    WSGIDaemonProcess pywps user=user group=group processes=2 threads=5
    WSGIScriptAlias /pywps /path/to/www/htdocs/wps/pywps.wsgi

    <Directory /path/to/www/htdocs/wps/>
        WSGIProcessGroup group
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
    ```

3. Create wsgi file:

    ```python
    #!/usr/bin/env python3
    import sys
    sys.path.append('/path/to/src/pywps/')
    
    import pywps
    from pywps.app import Service, WPS, Process
    
    def pr1():
        """This is the execute method of the process
        """
        pass
    
    
    application = Service(processes=[Process(pr1)])
    ```

4. Run via web browser

    `http://localhost/pywps/?service=WPS&request=GetCapabilities&version=1.0.0`

5. Run in command line:
  
    ```bash
    curl 'http://localhost/pywps/?service=WPS&request=GetCapabilities&version=1.0.0'
    ```


# Issues

On Windows PyWPS does not support multiprocessing which is used when making
requests storing the response document and updating the status to displaying
to the user the progression of a process.
