##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('VERSION.txt') as ff:
    VERSION = ff.read().strip()

DESCRIPTION = ('PyWPS is an implementation of the Web Processing Service '
               'standard from the Open Geospatial Consortium. PyWPS is '
               'written in Python.')

KEYWORDS = 'PyWPS WPS OGC processing'

with open('requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()

with open('requirements-py2.txt') as f:
    INSTALL_REQUIRES_PY2 = f.read().splitlines()

CONFIG = {
    'name': 'pywps',
    'version': VERSION,
    'description': DESCRIPTION,
    'keywords': KEYWORDS,
    'license': 'MIT',
    'platforms': 'all',
    'author': 'Jachym Cepicky',
    'author_email': 'jachym.cepicky@gmail.com',
    'maintainer': 'Jachym Cepicky',
    'maintainer_email': 'jachym.cepicky@gmail.com',
    'url': 'http://pywps.org',
    'download_url': 'https://github.com/geopython/pywps',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS'
    ],
    'install_requires': INSTALL_REQUIRES,
    'packages': [
        'pywps',
        'pywps/app',
        'pywps/inout',
        'pywps/resources',
        'pywps/validator',
        'pywps/inout/formats'
    ],
    'scripts': [],
}

if sys.version_info.major < 3:
    CONFIG['install_requires'] += INSTALL_REQUIRES_PY2

setup(**CONFIG)
