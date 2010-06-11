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
    will need an web server, to be able to execute processes from remote
    computers. PyWPS was tested with Apache 1.1 and 2.x versions.

GIS GRASS  
    http://grass.itc.it - Geographical Resources
    Analysis Support System (GRASS) is Open Source GIS, which provides more
    then 350 modules for raster and vector (2D, 3D) data analysis. PyWPS is
    written with native support for GRASS and it's functions. GRASS has
    also Python bindings, so you can run the modules directly.

PROJ.4  
    http://proj.maptools.org - Cartographic
    Projections library used in various Open Source projects, such as
    GRASS, UMN MapServer, QGIS and others. It can be used e.g. for data
    transformation. Proj4 is especially needed, if you want to integrate
    MapServer as well, in that case, you need `python-pyproj` package.

GDAL/OGR  
    http://gdal.org - translator library for
    raster geospatial data formats, is used in various projects for
    importing, exporting and transformation between various raster and vector
    data formats. GDAL and OGR are also needed, if you want to integrate
    MapServer as well. In that case, you need `python-gdal` package.

MapServer
    http://mapserver.org - If you want to access ComplexValue outputs using
    OGC OWS (WMS, WFS, WCS) services, you have to install MapServer as
    well. PyWPS will generate MapFile for you automaticaly. Look after
    `python-mapscript` package.

R  - http://www.r-project.org - is a language and environment
    for statistical computing and graphics.

.. quick-and-dirty:
====================================
Installation the quick 'n' dirty way
====================================
For installing PyWPS to your server simply unpack the archive to some
directory. You can also use current repository version.::

1 - cd to target directory::

    $ cd /usr/local/

2 -  unpack pywps::

    $ tar xvzf /tmp/pywps-VERSION.tar.gz

-----------------------
Post-installation steps
-----------------------
You have to change the write access of pywps/Templates/*WPS_VERSION*/ directory,
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
PyWPS provides packages for DEB and RPM-based Linux Distributions. You can
obtain them in the download section of `PyWPS Homepage <http://pywps.wald.intevation.org>`_

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

Anyway, you have to run it in command line::
    
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
