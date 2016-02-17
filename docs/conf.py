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

project = u'PyWPS'

license = ('This work is licensed under a Creative Commons Attribution 4.0 '
           'International License')

copyright = ('Copyright (C) 2014-2016 PyWPS Development Team, '
             'represented by Jachym Cepicky.')
copyright += license

with open('../VERSION.txt') as f:
    version = f.read().strip()

release = version
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

with open('../requirements.txt') as f:
    MOCK_MODULES = f.read().splitlines()

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()
