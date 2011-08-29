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

#   SETUP
name = 'pywps'
#   END of SETUP

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
import sys,os

doclines = __doc__.split("\n")


dist =  setup(
        name = name,
        version = 'trunk',
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
            'pywps.Wps.Execute',
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
                    'pywps.Wps.Execute':'pywps/Wps/Execute',
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
        scripts=['wps.py']
)

# check, if we are really installing
dryRun = False
install = False
for arg in sys.argv:
    if arg == "--dry-run":
        dryRun = True
    if arg == "install":
        install = True

# post installation part
if not dryRun and install and not os.environ.has_key("FAKEROOTKEY"):
    # compile templates
    # compiling before installing is necessary, because the apache
    # webserver has not the permission to create new files in the 
    # python site-packages directory
    from pywps.Template import TemplateProcessor

    # make sure, we will not import pywps from  local directory
    baseDir = os.path.join(dist.command_obj["install_egg_info"].install_dir,
            name,"Templates")

    versionDirs = ['1_0_0']

    template_files = ['GetCapabilities', 'DescribeProcess','Execute']

    for version in versionDirs:
        for template_file in template_files:
            print "Compiling template "+template_file+" in "+baseDir
            template_file = os.path.join(baseDir,version,
                                    template_file + '.tmpl')
            template = TemplateProcessor(fileName=template_file,compile=True)
else:
    print "dry-run only, templates are not complied"



