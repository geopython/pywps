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

doclines = __doc__.split("\n")

setup(
        name = 'pywps',
        version = '0.1',
        maintainer="Jachym Cepicky",
        maintainer_email = 'jachym.cepicky@centrum.cz',
        author = 'Jachym Cepicky',
        author_email = 'jachym.cepicky@centrum.cz',
        url = 'http://les-ejk.cz/?cat=pywps',
        license = "http://www.gnu.org/licenses/gpl.html",
        download_url="http://les-ejk.cz/?cat=pywps",
        description=doclines[0],
        platforms=["any"],
        classifiers= classifiers,
        long_description = "\n".join(doclines[1:]),

        packages = ['pywps','pywps.Wps','pywps.etc','pywps.processes','pywps.Wps.ogc'],
        package_dir={'pywps':"pywps",
                     'pywps.Wps':'pywps/Wps',
                     'pywps.etc':'pywps/etc',
                     'pywps.processes':'pywps/processes',
                     'pywps.Wps.ogc':'pywps/Wps/ogc'
                     },
        scripts=['wps.py'],
)

