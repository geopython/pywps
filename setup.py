"""PyWPS: Implementation of OGC's Web Processing Service in Python

PyWPS is simple cgi set of scripts, which (nearly) fills standard of OGC
(http://opengis.org) Web Processing Service. This standard describes the
way how geoinformation operations should be served via networks.

PyWPS provides environment for writing own scripts with help of GIS GRASS
modules (http://grass.itc.it). User of PyWPS can easily focuse on writing
own GRASS-scripts, without taking care on how the data will be imported and
served back to the client. Providing GRASS funktionality on the Internet
should be as easy as possible.
"""

classifiers=[
          'Development Status :: 0.1',
          'Environment :: CGI',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU/GPL',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications :: Email',
          'Topic :: Office/Business',
          'Topic :: Software Development :: Bug Tracking',
          ]


from distutils.core import setup
import sys

doclines = __doc__.split("\n")

# win or *nix
data_files= []
if sys.platform.find('linux')>-1:
    data_files= [('/etc/', ['pywps/etc/pywps.cfg']) ]

setup(
        name = 'pywps',
        version = '3.0.0',
        maintainer="Jachym Cepicky",
        maintainer_email = 'jachym@les-ejk.cz',
        author = 'Jachym Cepicky',
        author_email = 'jachym@les-ejk.cz',
        url = 'http://pywps.wald.intevation.org',
        license = "http://www.gnu.org/licenses/gpl.html",
        download_url="http://pywps.wald.intevation.org",
        description=doclines[0],
        platforms=["any"],
        classifiers= classifiers,
        long_description = "\n".join(doclines[1:]),

        packages = [
            'pywps',
            'pywps.Wps',
            'pywps.etc',
            'pywps.Parser',
            'pywps.Process',
            'pywps.Templates',
            'pywps.Templates.1_0_0',
            'pywps.Templates.1_0_0.inc',
        ],
        package_dir={
                    'pywps':"pywps",
                    'pywps.Wps':'pywps/Wps',
                    'pywps.Parser':'pywps/Parser',
                    'pywps.Process':'pywps/Process',
                    'pywps.Templates':'pywps/Templates',
                    'pywps.Templates.1_0_0':'pywps/Templates/1_0_0',
                    'pywps.Templates.1_0_0.inc':'pywps/Templates/1_0_0/inc',
                },
        package_data={
                    'pywps':
                    ['Templates/1_0_0/*.tmpl',
                     'processes/*.py-dist','processes/README',
                     'default.cfg'],
                    'pywps.Templates.1_0_0': ['inc/*.tmpl']
                },
        data_files=[
                    ('/etc/', ['pywps/etc/pywps.cfg'])
                ],
        scripts=['wps.py']
)

