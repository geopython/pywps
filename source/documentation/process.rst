*************
The Processes
*************
The default location for processes is :envvar:`PYWPS_INSTALLATION_PATH`:file:`/pywps/processes`. You can
create custom directory anywhere in your system and set
:envvar:`PYWPS_PROCESSES` environmental variable (on how to do this for the web
server, refer to your Server documentation, see sections
:role:`Wrapper script` and :role:`Customising PyWPS Installation` for details).

Alternatively you can set the `processesPath` variable in the configuration file.
Following example will describe buffering process. Several example processes are 
distributed along with PyWPS source code (they are in the
:file:`doc/examples/processes` directory) -- feel free to get inspired by
them.

===================================================================
Process initialization and configuration -- the :meth:`init` method
===================================================================
#. Create file :file:`foo.py` in :envvar:`PYWPS_PROCESSES` directory.
#. Add `'foo'` to `__all__` list in the :file:`__init__.py` file.
    
Each process is stand-alone python script with one class :class:Process,
which has two methods: :meth:`__init__`, :meth:`execute`. It is possible also to add as 
many your functions/methods, as you wish.::

    from pywps.Process.Process import WPSProcess                                
    class Process(WPSProcess):
        """Main process class"""
        def __init__(self):
            """Process initialization"""
            # init process
            WPSProcess.__init__(self,
                identifier = "foo", # must be same, as filename
                title="Buffer",
                version = "0.2",
                storeSupported = "true",
                statusSupported = "true",
                abstract="Create a buffer around an input vector file",

We defined new process called `foo`. The process is allowed to
store it's output data on the server (``storeSupported``) and it is also possible to run it in
asynchronous mode (``statusSupported``). The process will run within
GRASS GIS environment (``grassLocation = True``) -- temporary location
will be created and deleted again, after the processes is done.

---------------------------------------------------
Mandatory parameters of the :meth:`__init__` method
---------------------------------------------------
``identifier``
    `{String}` process identifier
``title`` 
    `{String}` process title

--------------------------------------------------
Optional parameters of the :meth:`__init__` method
--------------------------------------------------
``abstract`` 
    `{String}` process description

    **default:** None
``metadata``
    List of additional metadata.  See http://www.opengeospatial.org/standards/common, table 32 on page 65

    **example** ``{"foo":"bar"}``

    **default** None
``profile``
    `{String}` URL

    **default:** None
``version``
    `{String}` process version
    **default:** None

``statusSupported``
    `{Boolean}` this process can be run asynchronously

    **default:** True
``storeSupported``
    `{Boolean}` outputs from this process can be stored for later download

    **default:** True
``grassLocation`` 
    `{String}` or `{Boolean}` name of GRASS Location within
    :file:`gisdbase` directory (from :file:`pywps.cfg` configuration file).
    If set to True, temporary GRASS Location will be created
    and grass environment will be started. If None or False, no
    GRASS environment will be started.

    **default:** None

-----------
Data Inputs
-----------

Three types of data inputs are defined:

Literal Input 
    Basic literal input -- single number or text value
ComplexValue Input  
    Mostly vector file will be included in input XML
    request. It can be also only referenced (only URL will be send).
BoundingBox Input 
    Coordinates for lower-left and upper-right corner.

^^^^^^^^^^^^
ComplexInput
^^^^^^^^^^^^
Complex input can be raster or vector file, to be processed. ::

         self.dataIn = self.addComplexInput(identifier="data",
                              title = "Input data")
 
""""""""""""""""""""
Mandatory parameters
""""""""""""""""""""
``identifier`` 
    `String` input identifier
``title`` 
    `String` input title

"""""""""""""""""""
Optional parameters
"""""""""""""""""""
``abstract`` 
    `String` input description.

   default: None
``metadata``
    List of `Dict` ``{key:value}`` pairs.

   default: None
``minOccurs`` 
    `Integer` minimum number of occurrences.

    default: 1
``maxOccurs`` 
    `Integer` maximum number of occurrences.

    default: 1
``formats`` 
    List of `Dict` according to table 23 (page 25) in WPS 1.0.0 spec.

    Example::
            [
                {"mimeType": "image/tiff"},
                {
                    "mimeType": "text/xml",
                    "encoding": "utf-8",
                    "schema":"http://foo/bar"
                }
            ]

    default: ``[{"mimeType":"text/xml"}]``
``maxmegabites`` 
    `Float` Maximum input file size. Can not be bigger, as
    defined in global configuration file.

    default: 5

^^^^^^^^^^^^
LiteralInput
^^^^^^^^^^^^
With literal input, you can obtain any type of character string. You will
obtain instance of :class:`LiteralInput` class using
:meth:`addLiteralInput`::

         self.widthIn = self.addLiteralInput(identifier = "width",
                              title = "Width")

""""""""""""""""""""
Mandatory parameters
""""""""""""""""""""

``identifier``
    `String` input identifier
``title``
    `String` input title

"""""""""""""""""""
Optional parameters
"""""""""""""""""""
``abstract``
    `String` input description.
    
    Default: None
``uoms``
    List of `String` value units

    Default: ()
``minOccurs``
    `Integer` minimum number of occurrences.

    Default: 1
``maxOccurs``
    `Integer` maximum number of occurrences.

    Default: 1
``allowedValues``
    List of `String` or other allowed values,
      which can be used with this input. You can set interval
      using list with two items, like::

        (1,2,3,(5,9),10,"a",("d","g"))

      This will produce allowed values 1,2,3,10, "a" and
      any value between 5 and 9 or "d" and "g".

      If ``"*"`` is used, it means "any value"

      default: ("*")
``type``
    `types.TypeType` value type, e.g. Integer, String, etc. you
      can uses the :mod:`types` module of python.

      default: types.IntType
``default``
    `Any` default value.

    default: None
``metadata``
    List of `Dict` Additional metadata. 
    
    example::

        {"foo":"bar"}

    default: None

^^^^^^^^^^^^^^^^^
BoundingBox Input
^^^^^^^^^^^^^^^^^
The input is added to the process using :meth:`addBBoxInput`.

""""""""""""""""""""
Mandatory parameters
""""""""""""""""""""
identifier 
    `String` input identifier
title
    `String` input title

"""""""""""""""""""
Optional parameters
"""""""""""""""""""
``abstract``
   `String` input description.

  default: None
``metadata``
    List of `Dict` ``{key:value}`` pairs.

    default: None
``minOccurs``
    `Integer` minimum number of occurrences.

    default: 1
``maxOccurs``
    `Integer` maximum number of occurrences.

    default: 1
``crss``
    List of `String`s supported coordinate systems.

    default: ``["EPSG:4326"]``

For further documentation, refer to example processes distributed with the
source code as well as :command:`pydoc pywps/Wps/Process/Process.py`.  

.. FIXME::
    This should be part of this documentation.

------------
Data Outputs
------------
Data outputs can be defined in similar way.
* Literal Output
* ComplexValue Output
* BoundingBox Output
    
^^^^^^^^^^^^^^^^^^^
ComplexValue Output
^^^^^^^^^^^^^^^^^^^
The complex value can be raster or vector file (or any other binary or text
file).::

        self.bufferOut = self.addComplexOutput(identifier="buffer",
                                title="Output buffer file")

""""""""""""""""""""
Mandatory parameters
""""""""""""""""""""
``identifier`` 
    `String` input identifier
``title`` 
    `String` input title

"""""""""""""""""""
Optional parameters
"""""""""""""""""""
``abstract`` 
    `String` input description.

   default: None
``metadata``
    List of `Dict` ``{key:value}`` pairs.

   default: None
``formats`` 
    List of `Dict` according to table 23 (page 25) in WPS 1.0.0 spec.

    Example::
            [
                {"mimeType": "image/tiff"},
                {
                    "mimeType": "text/xml",
                    "encoding": "utf-8",
                    "schema":"http://foo/bar"
                }
            ]

    default: ``[{"mimeType":"text/xml"}]``


^^^^^^^^^^^^^^
Literal Output
^^^^^^^^^^^^^^
If you want to output any text string.::

          self.textOut = self.addLiteralOutput(identifier="text",
                               title="just some text")

""""""""""""""""""""
Mandatory parameters
""""""""""""""""""""

``identifier``
    `String` input identifier
``title``
    `String` input title

"""""""""""""""""""
Optional parameters
"""""""""""""""""""
``abstract``
    `String` input description.
    
    Default: None
``uoms``
    List of `String` value units

    Default: ()
``type``
    `types.TypeType` value type, e.g. Integer, String, etc. you
      can uses the :mod:`types` module of python.

      default: types.IntType
``default``
    `Any` default value.

    default: None

^^^^^^^^^^^^^^^^^^
BoundingBox Output
^^^^^^^^^^^^^^^^^^
BoundingBox output is added with the :meth:`addBBoxOutput` method

""""""""""""""""""""
Mandatory parameters
""""""""""""""""""""
identifier 
    `String` input identifier
title
    `String` input title

"""""""""""""""""""
Optional parameters
"""""""""""""""""""
``abstract``
   `String` input description.

  default: None
``crss``
    List of `String`s supported coordinate systems.

    default: ``["EPSG:4326"]``
``dimensions``
    `Integer` number of dimensions

    default: 2

For further documentation, refer to example processes distributed with the
source code as well as :command:`pydoc pywps/Wps/Process/Process.py`.  

.. FIXME::
    This should be part of this documentation.

===================================================================
Process Programming -- the :meth:`execute` method
===================================================================
    
The process must be defined in the :meth:`execute` method. 
Basically, you want to get input values and set output values. For this
purpose, you can use :meth:`getInputValue` and
:meth:`setOutputValue` methods of the :class:`Process` or
:meth:`getValue` and :meth:`setValue` of the input/output
objects (see below).

If you need to execute some shell command, you should use
:meth:`cmd` instead of e.g.
 ``os.system()`` or ``os.popen`` functions.

Calculation progress can be set using ``self.status.set(string message,
number percent)`` method.

Example follows::

    def execute(self):
            """Execute process.
            
            Each command will be executed and output values will be set
            """
     
             # run some command from the command line
             self.cmd("g.region -d")
     
             # set status value
             self.status.set("Importing data",20)
             self.cmd("v.in.ogr dsn=%s output=data" %\
                     (self.getInputValue('data')))
                 
             self.status.set("Buffering",50)
             self.cmd("v.buffer input=data output=data_buff buffer=%s scale=1.0 tolerance=0.01" %\
                     (self.getInputValue('width')))
     
             self.status.set("Exporting data",90)
     
             self.cmd("v.out.ogr type=area format=GML input=data_buff dsn=out.xml olayer=path.xml")
             
             self.bufferOut.setValue("out.xml")
             self.textOut.setValue("hallo, world")
             return

--------------
Error handling
--------------
    
At the end of the :meth:`execute` function, `None` value should be returned. Any other 
value means, that the calculation will be stopped and error report will be
returned back to the client, example::

        def execute(self):
            ...
            return "Ups, something failed!"
    
---------------
Using GRASS GIS
---------------

Configuration is done using standard pywps configuration file 
see :ref:`Configuration <configuration>`).


If you want to use GRASS GIS commands in your process, and there is no
GRASS Location to be used, you have to set ``grassLocation=True`` in
process definition::

         WPSProcess.__init__(self, identifier = "foo",
             ...
             grassLocation = True)

In this case, temporary GRASS Location will be created and after the
process is done, it will be deleted again. By default, no GRASS Location is
created.

You can also work in existing GRASS Location, then just set only the location
name. The gisdbase should be set in the configuration
file :ref:`Configuration <configuration>`::

         WPSProcess.__init__(self, identifier = "foo",
             ...
             grassLocation = "spearfish60")

In this case, you had to specify `gisdbase` option in
`[grass]` section of the configuration file. Otherwise, you have to
specify full path to existing location, e.g.::

         WPSProcess.__init__(self,
             identifier = "foo",
             ...
             grassLocation = "/foo/bar/grassdata/spearfish60")

========================
Testing your new process
========================

To test your PyWPS installation, you run it either as Webserver
cgi-application or in the command line directly. It is always good to start
with the command line test, so do not have to check :file:`error.log` of
the web server or the file, you set as `logFile` in the configuration file.

`GetCapabilities` request::
    $ wps.py "service=wps&request=getcapabilities"

    $ wget -nv -q -O - "http://localhost/cgi-bin/wps.py?\
                        service=Wps&request=getcapabilities"
        
`DescribeProcess` request::

    $ wps.py "version=1.0.0&service=Wps&\
                request=DescribeProcess&\
                Identifier=bufferExampleProcess"

    $ wget -nv -q -O - "http://localhost/cgi-bin/wps.py?\
                        version=0.4.0&service=Wps&\
                        request=DescribeProcess&Identifier=foo"
        
`Execute` request:
    For data inputs encoding, using HTTP Get method, see
    WPS 1.0.0 specification,  page 38 *Execute HTTP GET request KVP
    encoding*::

    ./wps.py "version=1.0.0&service=Wps&request=Execute&\
            Identifier=foo&\
            datainputs=data=http://foo/bar/roads.gml;width=0.5"
        
Some examples of XML request econding are available in :file:`doc/examples` directory.

Before testing WPS via HTTP POST, you have to set :envvar:`REQUEST_METHOD`
environment variable, then you can redirect input XML into :file:`wps.py`
script via standard input::

    $ export REQUEST_METHOD=POST
    $ cat doc/wps_execute_request-responsedocument.xml| wps.py
