PyWPS and GRASS GIS
*******************
PyWPS was originaly written with the support for `GRASS GIS
<http://grass.osgeo.org>`_. The processes can be executed within temporary
created GRASS Location or within existing GRASS Location, within temporary
created Mapset. If you are not familiar with this therms, consider to start
with GRASS first and understand this concept.

Configuring PyWPS
=================
First you have to configure PyWPS configuration file, as described in
:ref:`configuration`.

Allowing Process to be executed in GRASS environment
====================================================
When you are initializing new process (see :ref:`process-initialization`),
you can add :attr:`pywps.Process.WPSProcess.grassLocation` attribute to it.

The attribute can have following values:

    None
        GRASS Location is not created, GRASS environment is not started
        (default)::

            WPSProcess.__init__(self, identifier = "foo)

    True
        Temporary GRASS Location is created in XY coordinate system. 
        .. note:: In the future, GRASS Location will probably have
            coordinate system token from the input raster or vector file.::

            WPSProcess.__init__(self, identifier = "foo",
                                ...,
                                grassLocation = True)
    String
        Name of the GRASS Location within configured grassdbase. If the
        name starts with "/", full path to the location is taken, without
        any other configuration.::

            WPSProcess.__init__(self, identifier = "foo",
                ...
                grassLocation = "spearfish60")

        or::

            WPSProcess.__init__(self,
                identifier = "foo",
                ...
                grassLocation = "/foo/bar/grassdata/spearfish60")

Running GRASS modules from PyWPS
================================
