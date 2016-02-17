###############################################################################
#
# Copyright (C) 2014-2016 PyWPS Development Team, represented by Jachym Cepicky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
###############################################################################

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
