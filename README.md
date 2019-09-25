# PyWPS

PyWPS is an implementation of the Web Processing Service standard from
the Open Geospatial Consortium. PyWPS is written in Python.

[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://pywps.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/geopython/pywps.png)](https://travis-ci.org/geopython/pywps)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/19d53c45a3854e37b89523cf9bb1d262)](https://www.codacy.com/project/cehbrecht/pywps/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=geopython/pywps&amp;utm_campaign=Badge_Grade_Dashboard)
[![Coverage Status](https://coveralls.io/repos/github/geopython/pywps/badge.svg?branch=master)](https://coveralls.io/github/geopython/pywps?branch=master)
[![PyPI](https://img.shields.io/pypi/dm/pywps.svg)]()
[![GitHub license](https://img.shields.io/github/license/geopython/pywps.svg)]()

[![Join the chat at https://gitter.im/geopython/pywps](https://badges.gitter.im/geopython/pywps.svg)](https://gitter.im/geopython/pywps?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# License

As of PyWPS 4.0.0, PyWPS is released under an
[MIT](https://en.wikipedia.org/wiki/MIT_License) license
(see [LICENSE.txt](LICENSE.txt)).

# Dependencies

See [requirements.txt](requirements.txt) file

# Run tests

```bash
pip install -r requirements-dev.txt
# run unit tests
python -m unittest tests
# run code coverage
python -m coverage run --source=pywps -m unittest tests
python -m coverage report -m
```

# Run web application

## Example service

Clone the example service after having installed PyWPS:

```bash
git clone git://github.com/geopython/pywps-flask.git pywps-flask
cd pywps-flask
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
