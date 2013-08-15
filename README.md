pywps-4
=======

New version of PyWPS - written from scratch

Dependencies
============

lxml - http://lxml.de
owslib - https://github.com/geopython/OWSLib

path.py - pip install path.py
flask
werkzeug

Run tests
=========

[![Build Status](https://travis-ci.org/jachym/pywps-4.png)](https://travis-ci.org/jachym/pywps-4)



Install and run [tox](http://testrun.org/tox/latest/):

    $ pip install tox
    $ tox

Or run the tests by hand, with either python 2 or 3:

    $ python tests/__init__.py
