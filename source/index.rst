################
Welcome to PyWPS
################

(Python Web Processing Service) is implementation of `Web processing
Service <http://www.opengeospatial.org/standards/wps>`_ standard from `Open
Geospatial Consortium <http://opengeospatial.org>`_.

It has been started on Mai 2006 as project supported by
`DBU <http://dbu.de">`_ and currently (2009) maily sponsored by
`HS-RS <http://www.bnhelp.cz>`_. It offers environment for programming own
process (geofunctions or models) which can be accessed from the public. The
main advantage of PyWPS is, that it has been written with native support
for `GRASS GIS <http://grass.itc.it>`_. Access GRASS modules via web
interace should be as easy as possible.

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

****
News
****

----------------------
2008-11-06 PyWPS 3.0.0
----------------------

    PyWPS Development team announces new stable version of PyWPS [1] with number 3.0.0.

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

    For download this version, please follow the link below [2] or download PyWPS from subversion directly [3].

    NOTE: This version processes are note fully compatible with previous versions of PyWPS. However, the upgrade should not be complicated, please follow examples from doc/examples/processes/ directory.
    What is PyWPS:

    PyWPS (Python Web Processing Service) is implementation of Web Processing Service standard from Open Geospatial Consortium (OGC(R)). The main advantage of PyWPS is, that it has been written with native support for GRASS GIS, however, GRASS GIS is not required. Access GRASS modules via web interace should be as easy as possible. Processes can be written using GRASS GIS, but usage of other programs, like R package, GDAL or PROJ tools, is possible as well.

    Happy GISing!

    Jachym & PyWPS Development team

    * [1] http://pywps.wald.intevation.org
    * [2] http://wald.intevation.org/frs/download.php/525/pywps-3.0.0.tar.gz
    * [3] svn checkout https://svn.wald.intevation.org/svn/pywps/tags/pywps-3.0.0


----------------------
2008-10-01 PyWPS 3.0.0rc3
----------------------

    PyWPS Development team announces next release candidate of new PyWPS[1] version with number 3.0.0 (3.0.0rc3).

    Features of this release candidate:

        * Updated setup script
            * Templates are compiled during installation automatically
            * pywps.cfg is not installed to /etc/ by default
        * Added example for custom CGI wrapper in doc/ directory
        * Support for PYWPS_CFG environment variable - put your configuration
        * file anywhere in the system Example processes moved from pywps/processes to doc/examples/processes

    For more details, see original announcement of PyWPS 3.0.0. rc1 [1] and rc2 [2]

    For download and testing this new release candidate, please follow the link below [2] or download the RC from subversion directly [4].

    Please download & test!

    Happy GISing!

    Jachym & PyWPS Development team

    [1] http://lists.wald.intevation.org/pipermail/pywps-devel/2008-September/000365.html
    [2] http://lists.wald.intevation.org/pipermail/pywps-devel/2008-September/000369.html
    [3] http://wald.intevation.org/frs/download.php/495/pywps-3.0.0rc2.tar.gz
    [4] svn checkout https://svn.wald.intevation.org/svn/pywps/tags/pywps-3.0.0rc3


----------------------
2008-10-01 French translation of the documentation
----------------------

    I made the translation in french of the PyWPS .txt docs. (Here : http://geotribu.net/?q=node/45) I should start the pdf translation during this week.

    Arnaud

----------------------
2008-10-01 PyWPS 3.0.0rc2
----------------------

    PyWPS Development team announces next release candidate of new PyWPS[1] version with number 3.0.0 (3.0.0rc2).

    Features of this release candidate:

        * Fixed DescribeProcess template
        * Fixed some missing python packages
        * Fixed versions parameter in GetCapabilities

    For more details, see original announcement of PyWPS 3.0.0. rc1 [1]

    For download and testing this new release candidate, please follow the link below [2] or download the RC from subversion directly [3].

    For testing purposes, public PyWPS-3.0.0 server was setuped [4].

    Please download & test!

    Happy GISing!

    Jachym & PyWPS Development team

    [1] http://lists.wald.intevation.org/pipermail/pywps-devel/2008-September/000365.html
    [2] http://wald.intevation.org/frs/download.php/495/pywps-3.0.0rc2.tar.gz
    [3] svn checkout https://svn.wald.intevation.org/svn/pywps/tags/pywps-3.0.0rc2
    [4] http://apps.esdi-humboldt.cz/cgi-bin/pywps_3_0?service=wps&request=getcapabilities


----------------------
2008-10-01 PyWPS 3.0.0rc1
----------------------

    PyWPS Development team announces first release candidate of new PyWPS[1] version with number 3.0.0 (3.0.0rc1).

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

    For download and testing this new release candidate, please follow the link below [2] or download the RC from subversion directly [3].

    NOTE: This version processes are note fully compatible with previous versions of PyWPS. However, the upgrade should note be complicated, please follow examples from pywps/processes/ directory.
    What is PyWPS:

    PyWPS (Python Web Processing Service) is implementation of Web Processing Service standard from Open Geospatial Consortium. The main advantage of PyWPS is, that it has been written with native support for GRASS GIS. Access GRASS modules via web interace should be as easy as possible. Processes can be written using GRASS GIS, but usage of other programs is also possible. Usage together with R package or GDAL or PROJ tools.

    Please download & test!

    Happy GISing!

    Jachym & PyWPS Development team


----------------------
2008-10-01 PyWPS 2.0.1
----------------------

    Today, PyWPS 2.0.1 was released. It is a bugfix release, which fixes the "PyWPSdebug" issue, which was reported by several people.

    Have fun!

    Jachym


----------------------
2008-10-01 PyWPS 2.0.0
----------------------

    http://pywps.wald.intevation.org

    After a year of development, Python Web Processing Service (PyWPS) 2.0.0 is new stable release, which fixes number of bugs and instabilities in previous 1.0.0 version, as well as adds new functionality.

    PyWPS implements OGC Web Processing Service 0.4.0 standard [1]. It is developed with native support for GRASS GIS [2], however, it can be used with other GIS command line tools too (PROJ, GDAL/OGR, ...), as well as with the R Project for Statistical Computing.

    OGC Web Processing Service specification provides client access across a network to pre-programmed calculations and/or computation models that operate on spatially referenced data. The calculation can be extremely simple or highly complex, with any number of data inputs and outputs. It does not specify the specific processes that could be implemented by a WPS. Instead, it specifies a generic mechanism that can be used to describe and web-enable any sort of geospatial process.

    Several client applications can be used with PyWPS, e.g. Embrio project [3] and there is also plugin for OpenLayers [4][5].

    Major changes:

    * New Process interface for easier coding
    * More stable, temporary files should be deleted in any case
    * More verbose, better debugging output
    * OGC WPS 0.4.0 still not fully implemented, but much more
    * ...

    New development should be focused at implementation of the OGC WPS 1.0.0 specification.

    Jachym & PyWPS Development Team

