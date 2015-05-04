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
    'install_requires': ['lxml', 'werkzeug', 'flask', 'path.py', 'owslib', 'jsonschema'],
    'packages': ['pywps'],
    'scripts': [],
    'name': 'pywps'
}

setup(**config)
