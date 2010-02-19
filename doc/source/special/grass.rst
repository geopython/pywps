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

You have two possibilities: either to run GRASS modules as you would do in
shell script (running the modules directly) or access GRASS-python
interface.

Running GRASS command line modules
----------------------------------
Once :meth:`pywps.Process.WPSProcess.execute` method is executed, you
can use  :meth:`pywps.Process.WPSProcess.cmd` for calling GRASS
modules.

Using GRASS-Python interface
----------------------------
Since GRASS 6.4, Python interface is developed. There are both - `swig <http://www.swig.org/>`_
interface and GRASS Modules-Python iterface. There are both described in
`GRASS Wiki <http://grass.osgeo.org/wiki/GRASS_and_Python>`_ . There are
:meth:`grass.run_command`, :meth:`grass.mapcalc` and other useful methods.
For the swig interface, have a look in the GRASS-Wiki - it is perfectly
documented.

GRASS-Python interface example
..............................
::

    from grass.script import core as grass
    from pywps.Process import WPSProcess

    process =  WPSProcess(identifier="grassprocess",
                        title="GRASS Process")

    def execute():
        ret = grass.run_command("d.his", h_map = "drap_map", 
                                         i_map = "relief_map",
                                         brighten = 0)
        return

    process.execute = execute


