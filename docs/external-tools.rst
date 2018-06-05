PyWPS and external tools
========================

GRASS GIS
---------

PyWPS can handle all the management needed to setup temporal GRASS GIS
environemtn (GRASS DBASE, Location and Mapset) for you. You just need to
configure it in the :class:`pywps.Process`, using the parameter
``grass_location``, which can have 2 possible values:

``epsg:[EPSG_CODE]``
    New temporal location is created using the EPSG code given. PyWPS will
    create temporal directory as GRASS Location and remove it after the WPS
    Execute response is constructed.

``/path/to/grassdbase/location/``
    Existing absolute path to GRASS Location directory. PyWPS will create
    temporal GRASS Mapset direcetory and remove it after the WPS Exceute
    response is constructed.

Then you can use Python - GRASS interfaces in the execute method, to make the
work.

.. note:: Even PyWPS supports GRASS integration, the data still need to be
        imported using GRASS modules ``v.in.*`` or ``r.in.*`` and also they have
        to be exported manually at the end.

.. code-block:: python

    def execute(request, response):
            from grass.script import core as grass
            grass.run_command('v.in.ogr', input=request.inputs["input"][0].file,
            ...)
            ...
            grass.run_command('v.out.ogr', input="myvector", ...)

Also do not forget to set ``gisbase`` :ref:`configuration` option.

OpenLayers WPS client
---------------------

ZOO-Project
-----------

`ZOO-Project <http://www.zoo-project.org>`_ provides both a server (C) and
client (JavaScript) framework.

QGIS WPS Client
---------------

The `QGIS WPS <https://plugins.qgis.org/plugins/wps/>`_ client provides a
plugin with WPS support for the QGIS Desktop GIS.
