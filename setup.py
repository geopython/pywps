###############################################################################
#
# Copyright (C) 2014-2015 PyWPS Development Team, represented by Jachym Cepicky
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

DESCRIPTION = 'PyWPS - Python implementation of OGC Web Processing Service'

CONFIG = {
    'description': DESCRIPTION,
    'author': 'Jachym Cepicky',
    'url': 'http://pywps.org',
    'download_url': 'https://github.com/PyWPS/pywps-4',
    'author_email': 'jachym.cepicky@gmail.com',
    'version': '4.0',
    'install_requires': [
        'lxml',
        'werkzeug',
        'unipath',
        'OWSLib',
        'jsonschema'
    ],
    'packages': [
        'pywps',
        'pywps/app',
        'pywps/inout',
        'pywps/resources',
        'pywps/validator',
        'pywps/inout/formats'
    ],
    'scripts': [],
    'name': 'pywps'
}

if sys.version_info.major < 3:
    CONFIG['install_requires'].append('flufl.enum')

setup(**CONFIG)
