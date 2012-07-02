Process Inputs and Outputs
==========================
Process inputs and outputs are of three types:

    ComplexValue 
        Usually used for raster or vector data

    LiteralValue 
        Used for simple text strings

    BoundingBoxValue 
        Two coordinate pairs of lower-left and upper-right corners in
        defined coordinate sytem.

Inputs and outputs should usually be defined in the `__init__` method of
the process.

ComplexValue input and Output
-----------------------------
ComplexValue inputs and outputs are used in WPS to send larger sets of data (usually raster or vector data) into the process or from the process back to the user. The :meth:`pywps.Process.WPSProcess.addComplexInput` method returns an instance of :class:`pywps.Process.InAndOutputs.ComplexInput` for inputs. For outputs, they are called with :meth:`pywps.Process.WPSProcess.addComplexOutput`, which returns :class:`pywps.Process.InAndOutputs.ComplexOutput`.

The :attr:`pywps.Process.InAndOutputs.ComplexInput.value` and :attr:`pywps.Process.InAndOutputs.ComplexOutput.value`
attributes contain the *file name* of the raster or vector file.

For inputs, consider using the
:meth:`pywps.Process.InAndOutputs.ComplexInput.getValue` method, for getting
the value of the input, which can be returned as file object or file name.

For outputs, you should definitely use the
:meth:`pywps.Process.InAndOutputs.ComplexOutput.setValue` method for setting the
results file name. The method accepts a file object as well as a file name.

Sometimes, users are sending the data *as reference* to some URL (e.g. OGC
WFS or WCS service). PyWPS downloads the data for you and stores them to a
local file. If the client requires reference to the output data, PyWPS will
create this for you. PyWPS is able to setup a `MapServer <http://mapserver.org>`_ instance for you, and return OGC WFS or WCS URLs back to the client. For more on this topic, see :ref:`using-mapserver`.

Even you can (and should) define support data mimetypes
(:attr:`pywps.Process.InAndOutputs.ComplexInput.formats`), mimetype only is
checked. PyWPS does not care about valid schemas or anything else. This should
be handled by Your process.

Vector data values
..................
Vectors are usually handled as `GML <http://www.opengeospatial.org/standards/gml>`_ files. You can send any other file format as well, such as `GeoJSON <http://geojson.org/>`_, `KML <http://opengeospatial.org/standards/kml>`_ or any other vector data. Only condition is: the file should be in text form (so it can fit into XML correctly), if you want to append it as part of the input XML request and everything should be stored in *one* file. 

Vectors are the default
:attr:`pywps.Process.InAndOutputs.ComplexInput.format` of ComplexValue input or output -- `text/xml`  (GML) is expected.

.. note:: Some users do want to send `ESRI Shapfiles <http://en.wikipedia.org/wiki/Shapefile>`_. This is in general not to advisable.  Shapefiles are a binary format, which is hard to be used with XML, and it consists out of at least three files shp, shx and dbf.
    
    If you still want to handle shapefiles, you have either to zip
    everything in one file or define three separate complex inputs.

Example of simple input vector data::

    self.inputVector = self.addComplexOutput(identifier="in",title="Input file")

Example of more complex input vector data::

    self.gmlOrSimilarIn = self.addComplexInput(identifier="input",
                            title="Input file",
                            abstract="Input vector file, usually in GML format",
                            formats = [
                                        # gml
                                        {mimeType: 'text/xml',
                                        encoding:'utf-8',
                                        schema:'http://schemas.opengis.net/gml/3.2.1/gml.xsd'},
                                        # json
                                        {mimeType: 'text/plain',
                                        encoding: 'iso-8859-2',
                                        schema: None
                                        },
                                            
                                        # kml
                                        {mimeType: 'text/xml',
                                        encoding: 'windows-1250',
                                        schema: 'http://schemas.opengis.net/kml/2.2.0/ogckml22.xsd'}
                                        ],
                            # we need at least TWO input files, maximal 5
                            minOccurs: 2, 
                            maxOccurs: 5,
                            metadata: {'foo':'bar','spam':'eggs'}
                        )

Raster data values
..................
Sometimes, you need to work with raster data. You have to set the proper
:attr:`pywps.Process.InAndOutputs.ComplexInput.formats` attribute of
supported raster file format. Since rasters are usually in *binary* format, you
would usually have to send the data always *as reference*. Fortunately, this is not
the case. PyWPS can handle the input data, encoded in `Base64 format
<http://en.wikipedia.org/wiki/Base64>`_ and once PyWPS needs to send
raster data out as part of Execute response XML, they are encoded with
Base64 as well.

Example of simple output raster data::

    self.dataIn = self.addComplexOutput(identifier="raster",
                        title="Raster out",
                        formats=[{"mimeType":"image/tiff"}])
 
LiteralValue input and Output
-----------------------------
With literal input, you can obtain or send any type of character string. You will
obtain an instance of :class:`pywps.Process.InAndOutputs.LiteralInput` or :class:`pywps.Process.InAndOutputs.LiteralOutput`.

Literal value Inputs can be more complex. You can define a list of allowed
values, type of the literal input, spacing and so on.

.. note:: Spacing is not supported, so you can not currently define the
    step in allowed values row.

Type
....
For type settings, you can either use the :mod:`types` module, or the Python
:func:`type()` function. The default type is `type(0)` -- Integer.
PyWPS will check if the input value type matches allowed type.

.. note:: If you need the String type of literal input, PyWPS will always
    remove everything behind "#", ";", "!", "&" and similar characters.
    Try to avoid usage of LiteralValue input directly as input for e.g.
    SQL database or command line programs. This could cause a serious system
    compromise.

Allowed Values
..............
PyWPS lets you define a list of allowed input values. These can be string,
integer or float types. Default values are defined in the list. Ranges are
defined as two-items filed in form of `(minimum,maximum)`. For example, we
would like to allow values 1,2,3, 5 to 7, and 'spam', the
:attr:`pywps.Process.InAndOutputs.LiteralInput.values` value would look
like::

    [1,2,3,[5,7],'spam']

Default is "*", which means *all values*.


Simple example of LiteralValue output::

         self.widthOut = self.addLiteralOutput(identifier = "width",
                              title = "Width")

Complex example of LiteralValue input::

        self.litIn = self.addLiteralInput(identifier = "eggs",
                        title = "Eggs",
                        abstract = "Eggs with spam and sausages",
                        minOccurs = 0,
                        maxOccurs = 1,
                        uoms = "m",
                        dataType=type(0.0),
                        default=1.1,
                        values=[(0.0,10.1)])

BoundingBoxValue input and Output
---------------------------------
BoundingBox are two pairs of coordinates, defined in some coordinate
system (2D or 3D). In PyWPS, they are defined in
:class:`pywps.Process.InAndOutputs.BoundingBoxInput` and
:class:`pywps.Process.InAndOutputs.BoundingBoxOutput`. For getting them,
use :meth:`pywps.Process.WPSProcess.addBBoxInput` 
and :meth:`pywps.Process.WPSProcess.addBBoxOutput` respectively.

The value is a list of four coordinates in `(minx, miny, maxx, maxy)` format.

Example of BoundingBoxValue input::

    self.bbox = self.addBBoxOutput(identifier = "bbox",
                              title = "BBox")
