##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import sys

project = u'PyWPS'

license = ('This work is licensed under a Creative Commons Attribution 4.0 '
           'International License')

copyright = ('Copyright (C) 2014-2016 PyWPS Development Team, '
             'represented by Jachym Cepicky.')
copyright += license

with open('../VERSION.txt') as f:
    version = f.read().strip()

release = version
latex_logo = '_static/pywps.png'

extensions = [
    'sphinx.ext.extlinks',
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'pywps.ext_autodoc'
]

exclude_patterns = ['_build']
source_suffix = '.rst'
master_doc = 'index'

pygments_style = 'sphinx'

html_static_path = ['_static']

htmlhelp_basename = 'PyWPSdoc'
# html_logo = 'pywps.png'

html_theme = 'alabaster'
# alabaster settings
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'searchbox.html',
    ]
}
html_theme_options = {
    'show_related': True,
    'travis_button': True,
    'github_banner': True,
    'github_user': 'geopython',
    'github_repo': 'pywps',
    'github_button': True,
    'logo': 'pywps.png',
    'logo_name': False
}


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

# with open('../requirements.txt') as f:
#    MOCK_MODULES = f.read().splitlines()

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()

todo_include_todos = True
