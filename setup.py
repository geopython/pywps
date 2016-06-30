"""PyWPS: Implementation of OGC's Web Processing Service in Python

PyWPS is simple cgi set of scripts, which (nearly) fills standard of OGC
(http://opengis.org) Web Processing Service. This standard describes the
way how geoinformation operations should be served via networks.

PyWPS provides environment for writing own scripts with help of GIS GRASS
modules (http://grass.osgeo.it). User of PyWPS can easily focuse on writing
own GRASS-scripts, without taking care on how the data will be imported and
served back to the client. Providing GRASS funktionality on the Internet
should be as easy as possible.
"""

import sys
import os
import pywps
from pywps.Template import TemplateProcessor

def get_current_path():
    return os.path.abspath(os.path.dirname(__file__))

def get_templates_path(base):
    return os.path.join(base, 'pywps', 'Templates')

def compile_templates(base):
    versionDirs = ['1_0_0']

    template_files = ['GetCapabilities', 'DescribeProcess','Execute']

    for version in versionDirs:
        for template_file in template_files:
            print "Compiling template "+template_file+" in "+base
            template_file = os.path.join(base,version,template_file + '.tmpl')
            template = TemplateProcessor(fileName=template_file,compile=True)

# First compile templates
PYWPS_PATH=get_current_path()
TEMPLATES_PATH=get_templates_path(PYWPS_PATH)
compile_templates(TEMPLATES_PATH)


name = 'pywps'

classifiers=[
           'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications :: Email',
          'Topic :: Office/Business',
          'Topic :: Software Development :: Bug Tracking',
          ]


#from distutils.core import setup
from setuptools import setup
import sys,os,traceback

doclines = __doc__.split("\n")

with open('requirements.txt') as fh:
  install_requires = fh.read().splitlines()


dist =  setup(
        name = name,
        version = '3.2.6',
        maintainer="Jachym Cepicky",
        maintainer_email = 'jachym.cepicky@gmail.com',
        author = 'Jachym Cepicky',
        author_email = 'jachym.cepicky@gmail.com',
        url = 'http://pywps.org',
        license = "http://www.gnu.org/licenses/gpl.html",
        download_url="http://pywps.org/download/",
        description=doclines[0],
        zip_safe=False,
        platforms=["any"],
        classifiers= classifiers,
        long_description = "\n".join(doclines[1:]),

        packages = [
            'pywps',
            'pywps.Wps',
            'pywps.Wps.Execute',
            'pywps.XSLT',
            'pywps.Parser',
            'pywps.Process',
            'pywps.processes',
            'pywps.Templates',
            'pywps.Templates.1_0_0',
        ],
        package_dir={
                    'pywps':"pywps",
                    'pywps.Wps':'pywps/Wps',
                    'pywps.Wps.Execute':'pywps/Wps/Execute',
                    'pywps.XSLT':'pywps/XSLT',
                    'pywps.Parser':'pywps/Parser',
                    'pywps.Process':'pywps/Process',
                    'pywps.Templates':'pywps/Templates',
                    'pywps.Templates.1_0_0':'pywps/Templates/1_0_0',
                    'pywps.Templates.1_0_0.inc':'pywps/Templates/1_0_0/inc',
                },
        package_data={
                    'pywps':
                    ['Templates/1_0_0/*.tmplc',
                     'XSLT/*.xsl',
                     'processes/*.py-dist','processes/README',
                     'default.cfg']
                },
        requires=[
            'ordereddict',
            ],
        install_requires=install_requires,
        scripts=['wps.py']
)
