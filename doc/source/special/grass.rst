PyWPS and GRASS GIS
*******************
PyWPS was originally written with support for `GRASS GIS
<http://grass.osgeo.org>`_. The processes can be executed within a temporary
created GRASS Location or within an existing GRASS Location, within temporary
created Mapset. If you are not familiar with this concepts, please review
the GRASS documentation.

Configuring PyWPS
=================
First you have to configure PyWPS configuration file, as described in
:ref:`configuration`.

Allowing Process to be executed in the GRASS environment
========================================================
When you are initializing a new process (see :ref:`process-initialization`),
you can add a :attr:`pywps.Process.WPSProcess.grassLocation` attribute to it.

The attribute can have the following values:

    None
        GRASS Location is not created, GRASS environment is not started
        (default)::

            WPSProcess.__init__(self, identifier = "foo)

    True
        Temporary GRASS Location is created in XY coordinate system. 
        .. note:: In the future, GRASS Location will probably have a
            coordinate system token from the input raster or vector file.::

            WPSProcess.__init__(self, identifier = "foo",
                                ...,
                                grassLocation = True)
    String
        Name of the GRASS Location within the configured grassdbase. If the
        name starts with "/", the full path to the location is taken, without
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

You have two options: either run GRASS modules as you would do in
shell script (running the modules directly) or access the GRASS-python
interface.

Running GRASS command line modules
----------------------------------
Once the :meth:`pywps.Process.WPSProcess.execute` method is executed, you
can use the :meth:`pywps.Process.WPSProcess.cmd` method for calling GRASS
modules.

Using GRASS-Python interface
----------------------------
Since GRASS 6.4, Python bindings are supported. There are both a ctypes
interface and GRASS Modules-Python interface. They are both described in
the `GRASS Wiki <http://grass.osgeo.org/wiki/GRASS_and_Python>`_ . There are
:meth:`grass.run_command`, :meth:`grass.mapcalc` and other useful methods.

GRASS-Python interface example
..............................
::

    from pywps.Process import WPSProcess

    process =  WPSProcess(identifier="grassprocess",
                        title="GRASS Process")

    def execute():
        from grass.script import core as grass 

        ret = grass.run_command("d.his", h_map = "drap_map", 
                                         i_map = "relief_map",
                                         brighten = 0)
        return

    process.execute = execute


