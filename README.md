pywps-4
=======

New version of PyWPS, written from scratch.

* [Documentation](http://pywps.rtfd.org), hosted by ReadTheDocs.
* Continuous integration with Travis: 
  [![Build Status](https://travis-ci.org/jachym/pywps-4.png)](https://travis-ci.org/jachym/pywps-4)


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
