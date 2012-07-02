PyWPS and UMN MapServer
-----------------------
PyWPS can integrate `MapServer <http://mapserver.org>`_ to return results of ComplexData back
to the client.

The idea is as follows: if the client requires
:class:`pywps.Process.InAndOutputs.ComplexOutput` to be returned, `as
reference`, usually, a direct link to the produced file is returned. But with
MapServer, a WFS, WMS or WCS URL could be returned.

The client can later parse the URL of the resulting `ComplexValue` file and
e.g. instead of having a GeoTIFF file (result of the calculation), obtained
from the WCS, it can request a PNG file via WMS.

Requirements
............
To support MapServer for ComplexOutputs in your PyWPS
installation, the following packages have to be installed:

    * python-mapscript
    * python-gdal
    * python-pyproj

Usage
.....
When you are initializing a new process (see :ref:`process-initialization`),
you can set the :attr:`pywps.Process.InAndOutputs.ComplexOutput.useMapscript` attribute to `True` to get it run.
Have a look at the :class:`pywps.Process.InAndOutputs.ComplexOutput`
documentation, also for other attributes, like projection or bbox (can be set
automatically from georeferenced file). Required format
(:attr:`pywps.Process.InAndOutputs.ComplexOutput.format` decides on the output
service type (WCS for GeoTIFF and similar, WFS for xml or text, WMS for PNG, JPEG, GIF).::


    self.outputMap = self.addComplexOutput(identifier = "map",
                    title = "Resulting output map",
                    formats = [
                            {"mimeType":"image/tiff"},
                            {"mimeType":"image/png"}
                    ],
                    useMapscript=True)
