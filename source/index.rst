################
Welcome to PyWPS
################

(Python Web Processing Service) is an implementation of the `Web processing
Service <http://www.opengeospatial.org/standards/wps>`_ standard from `Open
Geospatial Consortium <http://opengeospatial.org>`_.

It has been started in Mai 2006 as a project supported by
`DBU <http://dbu.de>`_ and is currently (2009) mainly sponsored by
`HS-RS <http://www.bnhelp.cz>`_. It offers an environment for programming own
processes (geofunctions or models) which can be accessed from the public. The
main advantage of PyWPS is, that it has been written with native support
for `GRASS GIS <http://grass.osgeo.org>`_. Access to GRASS modules via web
interface should be as easy as possible.

PyWPS is written in `Python <http://python.org>`_, your processes must use this language too.

.. {% block tables %}
  <p><strong>{{ _('Main topics:') }}</strong></p>
  <table class="contentstable" align="center"><tr>
    <td width="50%">
      <p class="biglink"><a class="biglink" href="{{ pathto("download/index") }}">{{ _('Download') }}</a><br>
         <span class="linkdescr">{{ _('Download the latest PyWPS') }}</span></p>
      <p class="biglink"><a class="biglink" href="{{ pathto("development/index") }}">{{ _('Development') }}</a><br>
         <span class="linkdescr">{{ _('Mailing lists, source code, ...') }}</span></p>
    </td><td width="50%">
      <p class="biglink"><a class="biglink" href="{{pathto("documentation/index") }}">{{ _('Documentation') }}</a><br>
         <span class="linkdescr">{{ _('PyWPS Documentation') }}</span></p>
      <p class="biglink"><a class="biglink" href="{{ pathto("community/index") }}">{{ _('Community') }}</a><br>
         <span class="linkdescr">{{ _('Support, Mailing lists, trackers, IRC, wiki, ...') }}</span></p>
    </td></tr>
  </table>
  {% endblock %}

.. image:: .static/pywpsfoss4g2011.png

Where you can found something more about PyWPS at `FOSS4G 2011, Denver <http://2011.foss4g.org>`_

    * `PyWPS Tutorial <http://2011.foss4g.org/sessions/tutorial-pywps>`_ Wed, 09/14/2011 - 3:00pm - 3:30pm Room: Century

        Lear more about how to get, install, configure, use it.

    * `PyWPS Presentation <http://2011.foss4g.org/sessions/pywps>`_ Thu, 09/15/2011 - 1:30pm - 2:00pm Room: Windows

        What it is, what's new, what will be new.

    * `WPS Shootout <http://2011.foss4g.org/sessions/wps-shootout>`_  Thu, 09/15/2011 - 4:00pm - 4:30pm Room: Windows

        How is it compatible with OGC WPS, what about other WPS
        implementations?

****
News
****
2013-04-10 MS Windows
    
    * How to setup PyWPS on Windows, thanks to Joost Boerboom http://publicwiki.deltares.nl/display/OET/Setting+up+PyWPS+in+a+Windows+environment

2012-06-26 PyWPS Moved to Github
    
    * PyWPS is moved to Github! https://geopython.github.com

2011-09-06 PyWPS 3.2.1 released
    
    * Download: https://wald.intevation.org/frs/download.php/910/pywps-3.2.1.tgz

2011-09-06 PyWPS 3.2.0 released
    
    * Download: https://wald.intevation.org/frs/download.php/900/pywps-3.2.0.tgz

2011-01-18 New course material added

    Again main wiki page moved. This time you can find it at
    http://wiki.rsg.pml.ac.uk/pywps/Main_Page

2010-05-05 New course material added

    New course material added to PyWPS source. See `documentation
    <documentation>`_ for details.

2010-01-22 PyWPS Recomended as THE WPS tool in GIGAS project

    PyWPS was recomended as WPS tool in the `GIGAS <http://www.thegigasforum.eu/>`_ project.

        PyWPS Web Processing Service: is a Python program which implements the
        OGC WPS 1.0.0 standard (with a few omissions). PyWPS was chosen as it
        is up to date with the WPS standard and has a low footprint, making it
        easy to install on most Linux systems.  Python was considered a good
        choice of implementation language as it is a very easy language to
        develop in and allows partners to easily integrate existing processing
        which may have been written in other languages. PyWPS documentation may
        be found at http://pywps.wald.intevation.org/documentation/index.html

    See  http://www.thegigasforum.eu/cgi-bin/download.pl?f=342.pdf
    for more.

2009-06-01 PyWPS 3.1.0

    PyWPS Development team proudly announces a new stable PyWPS version 3.1.0.

    Features: 
        * Up-to-date examples
        * New generic WPS JavaScript library
        * Multiple fixes in both, source code and templates
        * New style In- and Outputs Complex objects
        * Tons of bugs fixed
        * ...

    See ChangeLog for more details

    For downloading, go to our `download page </download/>`_

2009-02-03 PyWPS Has a new homepage

    Based on Sphinx http://sphinx.pocoo.org/

2008-11-06 PyWPS 3.0.0

    PyWPS Development team proudly announces a new stable PyWPS [1] version 3.0.0.

    Features of this version:

        * Support for OGC(R) WPS 1.0.0
        * New simple configuration files
        * New methods for custom process definition
        * Support for multiple WPS servers with one PyWPS Installation
        * Support for internationalization
        * Simple code structure
        * Python-htmltmpl templating system
        * New examples of processes
        * ...

    To download this version, please follow the link below [2] or check out PyWPS directly from subversion [3].

    NOTE: This versions processes are not fully compatible with previous versions of PyWPS. However, the upgrade should not be complicated. Please follow the examples from doc/examples/processes/ directory.
    What is PyWPS:

    PyWPS (Python Web Processing Service) is an implementation of the Web Processing Service (WPS) standard from Open Geospatial Consortium (OGC(R)). The main advantage of PyWPS is, that it has been written with native support for GRASS GIS, however, GRASS GIS is not required. Access to GRASS modules via the web interface should be as easy as possible. Processes can be written using GRASS GIS, but usage of other programs, like R package, GDAL or PROJ tools, is possible as well.

    Happy GISing!

    Jachym & PyWPS Development team

    * [1] http://pywps.wald.intevation.org
    * [2] http://wald.intevation.org/frs/download.php/525/pywps-3.0.0.tar.gz
    * [3] svn checkout https://svn.wald.intevation.org/svn/pywps/tags/pywps-3.0.0


2008-10-01 PyWPS 3.0.0rc3

    PyWPS Development team announces the next release candidate of a new PyWPS[1] version with number 3.0.0 (3.0.0rc3).

    Features of this release candidate:

        * Updated setup script
            * Templates are compiled automatically during installation
            * pywps.cfg is not installed to /etc/ by default
        * Added example for custom CGI wrapper in doc/ directory
        * Support for PYWPS_CFG environment variable - put your configuration file anywhere in the system
	* Example processes moved from pywps/processes to doc/examples/processes

    For more details, see original announcement of PyWPS 3.0.0. rc1 [1] and rc2 [2]

    To download and test this new release candidate, please follow the link below [2] or check out the RC directly from subversion [4].

    Please download & test!

    Happy GISing!

    Jachym & PyWPS Development team

    [1] http://lists.wald.intevation.org/pipermail/pywps-devel/2008-September/000365.html
    [2] http://lists.wald.intevation.org/pipermail/pywps-devel/2008-September/000369.html
    [3] http://wald.intevation.org/frs/download.php/495/pywps-3.0.0rc2.tar.gz
    [4] svn checkout https://svn.wald.intevation.org/svn/pywps/tags/pywps-3.0.0rc3


2008-10-01 French translation of the documentation

    I made the translation in french of the PyWPS .txt docs. (Here : http://geotribu.net/?q=node/45).
    I should start the pdf translation during this week.

    Arnaud

2008-10-01 PyWPS 3.0.0rc2

    PyWPS Development team announces the next release candidate of a new PyWPS[1] version with number 3.0.0 (3.0.0rc2).

    Features of this release candidate:

        * Fixed DescribeProcess template
        * Fixed some missing python packages
        * Fixed versions parameter in GetCapabilities

    For more details, see original announcement of PyWPS 3.0.0. rc1 [1]

    To download and test this new release candidate, please follow the link below [2] or check out the RC directly from subversion [3].

    For testing purposes, a public PyWPS-3.0.0 server is available [4].

    Please download & test!

    Happy GISing!

    Jachym & PyWPS Development team

    [1] http://lists.wald.intevation.org/pipermail/pywps-devel/2008-September/000365.html
    [2] http://wald.intevation.org/frs/download.php/495/pywps-3.0.0rc2.tar.gz
    [3] svn checkout https://svn.wald.intevation.org/svn/pywps/tags/pywps-3.0.0rc2
    [4] http://apps.esdi-humboldt.cz/cgi-bin/pywps_3_0?service=wps&request=getcapabilities


2008-10-01 PyWPS 3.0.0rc1

    PyWPS Development team announces the first release candidate of a new PyWPS[1] version with number 3.0.0 (3.0.0rc1).

    Features of this version:

        * Support for OGC(R) WPS 3.0.0
        * New simple configuration files
        * New methods for custom process definition
        * Support for multiple WPS servers with one PyWPS Installation
        * Support for internationalization
        * Simple code structure
        * Python-htmltmpl templating system
        * New examples of processes
        * ...

    To download and test this new release candidate, please follow the link below [2] or check out the RC directly from subversion [3].

    NOTE: This versions processes are note fully compatible with previous versions of PyWPS. However, the upgrade should not be complicated. Please follow the examples from pywps/processes/ directory.
    What is PyWPS:

    PyWPS (Python Web Processing Service) is an implementation of the Web Processing Service Standard (WPS) from Open Geospatial Consortium. The main advantage of PyWPS is, that it has been written with native support for GRASS GIS. Access to GRASS modules via web interface should be as easy as possible. Processes can be written using GRASS GIS, but usage of other programs like R,GDAL or PROJ tools is also possible.

    Please download & test!

    Happy GISing!

    Jachym & PyWPS Development team


2008-10-01 PyWPS 2.0.1

    Today, PyWPS 2.0.1 was released. It is a bugfix release, which fixes the "PyWPSdebug" issue reported by several people.

    Have fun!

    Jachym


2008-10-01 PyWPS 2.0.0

    http://pywps.wald.intevation.org

    After a year of development, Python Web Processing Service (PyWPS) 2.0.0 is available with a new stable release, which fixes a lot of bugs and instabilities from the  previous 1.0.0 version, as well as add a lot of new functionality.

    PyWPS implements OGC Web Processing Service 0.4.0 standard [1]. It is developed with native support for GRASS GIS [2], however, it can be used with other GIS command line tools too (PROJ, GDAL/OGR, ...), as well as with the R Project for Statistical Computing.

    OGC Web Processing Service specification provides client access across a network to pre-programmed calculations and/or computation models that operate on spatially referenced data. The calculation can be extremely simple or highly complex, with any number of data inputs and outputs. It does not specify the specific processes that could be implemented by a WPS. Instead, it specifies a generic mechanism that can be used to describe and web-enable any sort of geospatial process.

    Several client applications can be used with PyWPS, e.g. Embrio project [3] and there is also plugin for OpenLayers [4][5].

    Major changes:

    * New Process interface for easier coding
    * More stable, temporary files should be deleted in any case
    * More verbose, better debugging output
    * OGC WPS 0.4.0 still not yet fully implemented, but close to
    * ...

    New development should be focused at implementation of the OGC WPS 1.0.0 specification.

    Jachym & PyWPS Development Team

