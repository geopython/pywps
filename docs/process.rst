.. currentmodule:: pywps

.. _process:

#########
Processes
#########

.. versionadded:: 4.0.0

.. todo::
    * Input validation
    * IOHandler

PyWPS works with processes and services. A process is a Python `Class` object
containing an `handler` method and list of inputs and outputs. PyWPS service
instance is then collection of selected processes. 

PyWPS does not ship with any processes predefined - it's on you, as user of
PyWPS to setup processes of your choice. PyWPS is here to help you to publish
your awesome geospatial operation on the web - we take care about the
communication and security, you have to add the content.

.. note:: There are some example processes in the `PyWPS-Demo`_ project.

Writing a Process
=================

.. note:: At this place, you should preare your environment for final
        :ref:`deployment`. At least, you should create single directory with
        your processes, which is typically named `processes`::

        $ mkdir processes

        In this directory, we will create single python scripts containing
        processes.

        The processes can be located *anywhere in the system* as long as they
        are located in the :envvar:`PYTHON_PATH` environment variable, and can
        be imported in final server instance.

A processes is coded as a class inheriting from :class:`Process`.
In the `PyWPS-Demo`_ server they are
kept inside the *processes* folder, usually in separated files.

The instance of an *Process* need following attributes to get configured:

:identifier:
    unique identifier of the process
:title:
    corresponding title
:inputs:
    list of process inputs
:outputs:
    list of process outputs
:handler:
    function, which gets :class:`pywps.app.WPSRequest` and :class:`pywps.app.WPSResponse` as inputs.

Example vector buffer process
=============================

As an example, we will create *buffer* process - process which will take vector
file at the input, create specified buffer around the data (using `Shapely
<http://toblerity.org/shapely/>`_),  and return back the result.

Therefore, it's clear, the process will have 2 inputs: 

* `ComplexData` input - the vector file
* `LiteralData` input - the buffer size

And it will have one output

* `ComplexData` output - the final buffer

The process can be called `demobuffer` and we can now start coding it::

    $ cd processes
    $ $EDITOR demobuffer.py

At the beginning, we have to import needed classes and modules
    
Here is a very basic example:

.. literalinclude:: demobuffer.py
   :language: python
   :lines: 10-12
   :linenos:
   :lineno-start: 10

As next step, we will define list of inputs. First input is
:class:`pywps.ComplexInput` with identifier `vector`, title `Vector map`
and there is only one allowed format of GML.

The next input is :class:`pywps.LiteralInput` with identifier `size` and
data type set to `float`:

.. literalinclude:: demobuffer.py
   :language: python
   :lines: 14-21
   :linenos:
   :lineno-start: 14

Next we define output `output` as :class:`pywps.ComplexOutput`. This
output supports GML format only.

.. literalinclude:: demobuffer.py
   :language: python
   :lines: 23-27
   :linenos:
   :lineno-start: 23

Next we create new list variables for inputs and outputs.

.. literalinclude:: demobuffer.py
   :language: python
   :lines: 29-30
   :linenos:
   :lineno-start: 29

Next we define the *handler* function. In this function, *geospatial analysis
may happen*. The function gets :class:`pywps.app.WPSRequest` and
:class:`pywps.app.WPSResponse` objects as parameters. In our case, we let
calculate the buffer around each vector feature using 
`GDAL/OGR library <http://gdal.org>`_. We will not got much into detail, what
you should note is the way, how to get data from inputs from the WPSRequest
object and how to set data to outputs in the WPSResponse object.

.. literalinclude:: demobuffer.py
   :language: python
   :pyobject: _handler
   :emphasize-lines: 8-12, 50-54
   :linenos:
   :lineno-start: 45

At the end, we put everything together and create new `DemoBuffer` class with
handler, inputs and outputs. It's based on :class:`pywps.Process`:

.. literalinclude:: demobuffer.py
   :pyobject: DemoBuffer
   :language: python
   :linenos:
   :lineno-start: 32


Declaring inputs and outputs
============================

Clients need to know which inputs the processes expects. They can be declared
as :class:`pywps.Input` objects in the :class:`Process` class declaration::


    from pywps import Process, LiteralInput, LiteralOutput

    class FooProcess(Process):
        def __init__(self):
            inputs = [
                LiteralInput('foo', data_type='string'),
                ComplexInput('bar', [Format('text/xml')])
            ]
            outputs = [
                LiteralOutput('foo_output', data_type='string'),
                ComplexOutput('bar_output', [Format('JSON')])
            ]

            super(FooProcess, self).__init__(
                ...
                inputs=inputs,
                outputs=outputs
            )
            ...

.. note:: More generic description can be found in :ref:`wps` chapter.

LiteralData
-----------

* :class:`LiteralInput` 
* :class:`LiteralOutput`

A simple value embedded in the request. The first argument is a
name. The second argument is the type, one of `string`, `float`,
`integer` or `boolean`.

ComplexData
-----------

* :class:`ComplexInput`
* :class:`ComplexOutput`

A large data object, for example a layer. ComplexData do have `format` attribute
as one of their key property. It's either list of supported formats or single
(already selected) format. It shall be instance of
:class:`pywps.inout.formats.Format` class

ComplexData :class:`Format`
---------------------------
asdfjlk alsjf jasfk jaslf kja

.. todo:: TODO

BoundingBoxData
---------------

* :class:`BoundingBoxInput`
* :class:`BoundingBoxOutput`

Accessing the inputs and outputs in the `handler`
=================================================

Handlers receive an input argument, a :class:`WPSRequest` object. Input
values are found in the `inputs` dictionary::

    @staticmethod
    def _handler(request, response):
        name = request.inputs['name'][0].data
        response.outputs['output'].data = 'Hello world %s!' % name
        return response

`inputs` is a plain Python dictionary.
Most of the inputs and outputs are derived from :class:`IOHandler`. This enables
the user to access the data in 3 different ways: As `file name`, using `file`
attribute, as direct data object using `data` attribute and as IOStream object,
using `stream` attribute::

    request.inputs['file_input'][0].file
    request.inputs['data_input'][0].data
    request.inputs['stream_input'][0].stream

Because there could be multiple input values with the same identifier, the
inputs are accessed with an index.  For `LiteralInput`, the value is a string.
For `ComplexInput`, the value is an open file object, with a `mime_type`
attribute::

    @staticmethod
    def handler(request, response):
        layer_file = request.inputs['layer'][0].file
        mime_type = layer_file.mime_type
        bytes = layer_file.read()
        msg = ("You gave me a file of type %s and size %d"
               % (mime_type, len(bytes)))
        response.outputs['output'].data = msg
        return response


Returning large data
====================
WPS allows for a clever method of returning a large data file: instead
of embedding the data in the response, it can be saved separately, and
a URL returned from where the data can be downloaded. In the current
implementation, the PyWPS-4 core will save the file in a folder specified
in the configuration passed by the service (or in a default location).
The URL returned is embedded in the XML response.

This behaviour can be requested either by using a GET::

    ...ResponseDocument=output=@asReference=true...

Or a POST request::

    ...
    <wps:ResponseForm>
        <wps:ResponseDocument>
            <wps:Output asReference="true">
                <ows:Identifier>output</ows:Identifier>
                <ows:Title>Some Output</ows:Title>
            </wps:Output>
        </wps:ResponseDocument>
    </wps:ResponseForm>
    ...

**output** is the identifier of the output the user wishes to have be stored
and accessible from a URL. The user may request as many outputs by reference
as need, but only *one* may be requested in RAW format.


Process deployment
==================
In order for clients to invoke processes, a PyWPS
:class:`Service` class must be present with the ability to listen for requests. 
An instance of this class must created, receiving instances of
all the desired processes classes.

In the *demo* application the :class:`Service` class instance is created in 
:class:`Server` class. :class:`Server` is a development server that relies 
on `Flask`_. The publication
of processes is encapsulated in *demo.py*, where a main method
passes a list of processes instances to the :class:`Server` class::

    from pywps import Service
    from processes.helloworld import HelloWorld
    from processes.demobuffer import DemoBuffer

    ...
    processes = [ DemoBuffer(), ... ]

    server = Server(processes=processes)

    ...

Running the dev server
======================

The :ref:`demo` application is a `WSGI application`_ that accepts incoming `Execute`
requests and calls the appropriate process to handle them. It also
answers `GetCapabilities` and `DescribeProcess` requests based on the
process identifier and their inputs and outputs.

.. _WSGI application: http://werkzeug.pocoo.org/docs/terms/#wsgi


A host, a port, a config file and the processes can be passed as arguments to the 
:class:`Server` constructor.
**host** and **port** will be **prioritized** if passed to the constructor, 
otherwise the contents of the config file (*pywps.cfg*) are used. 


Use `run` method start the server::

    ...
    s = Server(host='0.0.0.0', processes=processes, config_file=config_file)

    s.run()
    ...
    

To make the server visible from another computer, replace ``localhost`` with ``0.0.0.0``.
    
.. _Flask: http://flask.pocoo.org
.. _PyWPS-Demo: http://github.com/geopython/pywps-demo


