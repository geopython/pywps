.. _pywps:

PyWPS
=====

.. todo:: 

  * how are things organised
  * storage
  * dblog
  * relationship to grass gis

PyWPS philosophy
----------------

PyWPS is simple, fast to run, has low requirements on system resources, is
modular. PyWPS solves the problem of exposing geospatial calculations to the
web, taking care of security, data download, request acceptance, process running
and final response construction. Therefore PyWPS has a bicycle in its logo.

Why is PyWPS there
------------------

Many scientific researchers and geospatial services provider need to setup
system, where the geospatial operations would be calculated on the server, while
the system resources could be exposed to clients. PyWPS is here, so that you
could set up the server fast, deploy your awesome geospatial calculation and
expose it to the world. PyWPS is written in Python with support for many
geospatial tools out there, like GRASS GIS, R-Project or GDAL. Python is the
most geo-positive scripting language out there, therefore all the best tools
have their bindings to Python in their pocket.

PyWPS History
-------------

PyWPS started in 2006 as scholarship funded by `German Foundation for
Environment <http://dbu.de>`_. During the years, it grow to version 4.0.x. In
2015, we officially entered to `OSGeo <https://osgeo.org>`_ incubation process.
In 2016, `Project Steering Committee <https://pywps.org/development/psc.html>`_ has started.
PyWPS was originally hosted by the `Wald server <http://wald.intevation.org>`_,
nowadays, we moved to `GeoPython group on GitHub
<https://gitub.com/geopython/>`_. Since 2016, we also have new domain `PyWPS.org
<https://pywps.org>`_.

You can find more at `history page <https://pywps.org/history>`_.
