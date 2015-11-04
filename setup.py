import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'PyWPS - Python implementation of OGC Web Processing Service',
    'author': 'Jachym Cepicky',
    'url': 'http://pywps.org',
    'download_url': 'https://github.com/jachym/pywps-4',
    'author_email': 'jachym.cepicky@gmail.com',
    'version': '4.0',
    'install_requires': ['lxml', 'werkzeug', 'unipath', 'owslib', 'jsonschema'],
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
    config['install_requires'].append('flufl.enum')

setup(**config)
