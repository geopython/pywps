# encoding: utf-8

import sys, os

project = u'PyWPS'
copyright = u'2013, Jachym Cepicky'
version = '4.0'
release = '4.0'

extensions = ['sphinx.ext.autodoc']
exclude_patterns = ['_build']
source_suffix = '.rst'
master_doc = 'index'

pygments_style = 'sphinx'

html_theme = 'default'
htmlhelp_basename = 'PyWPSdoc'
