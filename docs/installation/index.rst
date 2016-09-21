.. _installation:
*********************
Installation of PyWPS
*********************

===============
Prerequirements
===============
    
* python  -- currently 2.5, 2.6 are supported, 2.4 is deprecated
* python-xml 

====================
Recommended packages
====================
    
Web Server 
    (e.g. Apache) - http://httpd.apache.org -  You
    will need a web server to be able to execute processes from remote
    clients over the Internet. PyWPS was tested with Apache 1.1 and 2.x versions.

GIS GRASS  
    http://grass.osgeo.it - Geographical Resources
    Analysis Support System (GRASS) is an Open Source GIS, which provides more
    then 350 modules for raster and vector (2D, 3D) data analysis. PyWPS is
    written with native support for GRASS and it's functions. GRASS also
    has Python bindings, so you can run the modules directly.

PROJ.4  
    http://proj.maptools.org - Cartographic
    Projections library used in various Open Source projects, such as
    GRASS, MapServer, QGIS and others. It can be used e.g. for coordinate
    transformation. Proj4 is required if you want to integrate
    MapServer as well, using the `python-pyproj` package.

GDAL/OGR  
    http://gdal.org - translator library for
    raster geospatial data formats.  GDAL/OGR is used in various projects for
    importing, exporting and transformation between various raster and vector
    data formats. GDAL and OGR are also required if you want to integrate
    MapServer, using the `python-gdal` package.

MapServer
    http://mapserver.org - If you want to access ComplexValue outputs using
    OGC OWS (WMS, WFS, WCS) services, MapServer is required.
    PyWPS will generate a MapServer mapfile for you automatically.  The
    `python-mapscript` package is required.

R
    http://www.r-project.org - is a language and environment
    for statistical computing and graphics.

.. quick-and-dirty:
====================================
Installation the quick 'n' dirty way
====================================
For installing PyWPS to your server quickly, simply unpack the archive to some
directory. You can also use current repository version.::

1 - cd to target directory::

    $ cd /usr/local/

2 -  unpack pywps::

    $ tar xvzf /tmp/pywps-VERSION.tar.gz

-----------------------
Post-installation steps
-----------------------
You have to change the write access of ``pywps/Templates/*WPS_VERSION*/`` directory,
so the web server can compile the templates::

    chmod 777 /usr/local/pywps-VERSION/pywps/Templates/1_0_0

============================
Installation the 'clean' way
============================

Unpack the package ::

    $ tar -xzf pywps-VERSION.tar.gz

and run ::

    $ python setup.py install

=================================================
Installation using prebuild distribution packages
=================================================
PyWPS provides `packages <http://pywps.wald.intevation.org/download/index.html>`_ for
Debian and RPM based Linux Distributions.

.. note:: The packages are not maintained properly and until we don't find
    packagers, we recommend to use any other approach, described earlier in
    this section.

========================
Testing the installation
========================
If PyWPS has been successfully installed, you can test this with running it
without any input or further configuration.

First you need to find the `cgiwps.py` script, which is in the root of pywps
installation directory (if you used the :ref:`Quick and dirty way`), or it
should be located in :file:`/usr/bin` directory, if you used the clean way
of installation. 

Run `cgiwps.py` on the command line::
    
    $ ./cgiwps.py

And you should get result like this (which is a mixture of standard output
and standard error):

.. code-block:: xml


    PyWPS NoApplicableCode: Locator: None; Value: No query string found.
    Content-type: text/xml

    <?xml version="1.0" encoding="utf-8"?>
    <ExceptionReport version="1.0.0" xmlns="http://www.opengis.net/ows" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <Exception exceptionCode="NoApplicableCode">
                    <ExceptionText>
                            No query string found.
                    </ExceptionText>
            </Exception>
    </ExceptionReport>

In this case, you have installed PyWPS correctly and you are ready to
proceed to configuration.
