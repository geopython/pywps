PyWPS and UMN MapServer
-----------------------
There is little but maybe interesting possibility, how to use `UMN
MapServer <http://mapserver.org>`_ for returning resuls of ComplexData back
to the client.

The idea is following: if the client requires
:class:`pywps.Process.InAndOutputs.ComplexOutput` to be returned, `as
reference`, usually, direct link to the produced file is returned. But with
MapServer, WFS, WMS or WCS URL could be returned.

The client, can later parse the URL of resulting `ComplexValue` file and
e.g. instead of having GeoTIFF file (result of the calculation), obtained
from the WCS, it can request PNG file, via WMS.

Requirements
............
For having support for UMN MapServer for ComplexOutputs in your PyWPS
installation, following packages have to be installed:

    * python-mapscript
    * python-gdal
    * python-pyproj

Usage
.....
When you are initializing new process (see :ref:`process-initialization`),
you can add :attr:`pywps.Process.InAndOutputs.ComplexOutput.useMapscript` attribute to `True` do get it run.
Have a look at the :class:`pywps.Process.InAndOutputs.ComplexOutput`
documentation, also for other attributes, like projection or bbox (can be set
automatically from georeferenced file). Required format
(:attr:`pywps.Process.InAndOutputs.ComplexOutput.format`  decides, if WCS
(GeoTIFF and similar), WFS (format contains "xml" or "text") or WMS (PNG,
JPEG, GIF) is returned.::

    
    self.outputMap = self.addComplexOutput(identifier = "map",
                    title = "Resulting output map",
                    formats = [
                            {"mimeType":"image/tiff"},
                            {"mimeType":"image/png"}
                    ],
                    useMapscript=True)
