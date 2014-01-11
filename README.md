pywps-4
=======

New version of PyWPS, written from scratch.

* [Documentation](http://pywps.rtfd.org), hosted by ReadTheDocs.
* Continuous integration with Travis: 
  [![Build Status](https://travis-ci.org/jachym/pywps-4.png)](https://travis-ci.org/jachym/pywps-4)
* [Demo application](http://pywps.grep.ro/)


Dependencies
============

* lxml (http://lxml.de)
* werkzeug (http://werkzeug.pocoo.org)


Run tests
=========

Install and run [tox](http://testrun.org/tox/latest/):

    $ pip install tox
    $ tox

Or run the tests by hand, with either python 2 or 3:

    $ python tests/__init__.py

Run web application
===================

Apache configuration
--------------------
1. Enable WSGI extension
2. Add configuration:

    WSGIDaemonProcess pywps user=user group=group processes=2 threads=5
    WSGIScriptAlias /pywps /path/to/www/htdocs/wps/pywps.wsgi

    <Directory /path/to/www/htdocs/wps/>
        WSGIProcessGroup group
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>

3. Create wsgi file
    
    #!/usr/bin/env python3

    import sys
    sys.path.append('/path/to/src/pywps-4/')

    import pywps
    from pywps.app import Service, WPS, Process

    def pr1():
        """This is the execute method of the process
        """
        pass


    application = Service(processes=[Process(pr1)])

4. Run via web browser

    http://localhost/pywps/?service=wps&request=getcapabilities

5. Run in command line: TBD
