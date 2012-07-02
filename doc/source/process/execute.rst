Execution of the process
========================
Each process has to define a :meth:`pywps.Process.WPSProcess.execute` method,
which makes the calculation and sets the output values. This method is
called via a WPS Execute request. 

In principle, you can do what ever you need within this method. It is
advised, to use python bindings to popular GIS packages, like `GRASS GIS
<http://grass.osgeo.org>`_, `GDAL/OGR <http://gdal.org>`_, `PROJ4
<http://proj.remotesensing.org>`_, or any other 
`Python-GIS package <http://pypi.python.org/pypi?:action=browse&show=all&c=391>`_.

In the :ref:`special` chapter, we give you a quick intro to some of
these packages. Some examples are also distributed along with the PyWPS source.

If you need to run some shell programs, you should use the
:meth:`pywps.Process.WPSProcess.cmd` method.

Below is an example of a simple execute method which transforms a raster file from
one coordinate system to another, using Python bindings to GDAL.::

    from osgeo import gdal
    from osgeo.gdalconst import *

    ...

    def execute(self):
        """Convert input raster file to PNG using GDAL"""
      
        # create gdal input dataset 
        indataset = gdal.Open( self.inputRaster.getValue())
        
        # get output driver for PNG format
        pngDriver = gdal.GetDriverByName("png")
        
        # define output gdal dataset
        outfile = "output.png"
        outdataset = pngDriver.CreateCopy(outfile, indataset)

        self.outputRaster.setValue(outfile)
        self.outputRaster.format = {'mimeType':"image/png"}
        
        return
