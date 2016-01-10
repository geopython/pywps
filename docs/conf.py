# encoding: utf-8

import sys, os

project = u'PyWPS'
copyright = u'2013, Jachym Cepicky'
version = '4.0'
release = '4.0'
latex_logo = 'pywps.png'

extensions = ['sphinx.ext.autodoc']
exclude_patterns = ['_build']
source_suffix = '.rst'
master_doc = 'index'

pygments_style = 'sphinx'

html_theme = 'default'
htmlhelp_basename = 'PyWPSdoc'
html_logo = 'pywps.png'


class Mock(object):
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        return Mock()
    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'
        elif name[0] == name[0].upper():
            return Mock
        else:
            return Mock()

MOCK_MODULES = ['lxml', 'lxml.etree', 'lxml.builder']
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()
