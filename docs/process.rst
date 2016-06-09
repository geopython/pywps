.. currentmodule:: pywps

.. _process:

=========
Processes
=========

PyWPS-4 works with processes and services. A process is a class containing an handler method
and specifying inputs and outputs. A service is a collection of processes.


Writing a process class
~~~~~~~~~~~~~~~~~~~~~~~
A processes is coded as a class inheriting from :class:`Process`.
In the *demo* server they are kept inside the *processes* folder.
Here is a very basic example::

    from pywps import Process, LiteralInput, LiteralOutput

    class HelloWorld(Process):
        def __init__(self):
            inputs = [LiteralInput('name', 'Name of a person', data_type='string')]
            outputs = [LiteralOutput('output', 'HelloWorld Output', data_type='string')]

            super(HelloWorld, self).__init__(
                self._handler,
                identifier='hello_world',
                version='0.1',
                title='My very first process!',
                abstract='This process takes the name of a person and displays Hello World with it.',
                inputs=inputs,
                outputs=outputs
            )
            
The first argument to the super class *__init__* method is the handler method. 
The second is the process identifier, that is used to distinguish this from 
other processes. Both these arguments are mandatory.

The handler is a class method (or any callable object), that takes a request and a response
object as arguments, and returns a response object. Like so::

    @staticmethod
    def _handler(request, response):
        response.outputs['output'].data = 'Hello world!'
        return response

request is an instance of :class:`WPSRequest`.
response is an instance of :class:`WPSResponse`.

These classes accept :class:`LiteralInput`
values. The values can be strings (that become literal outputs) or
:class:`FileReference` objects (that become complex outputs).


Declaring inputs and outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Clients need to know which inputs the processes expects. They can be declared
as :class:`Input` objects in the :class:`Process` class declaration::


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

:class:`LiteralInput`
    A simple value embedded in the request. The first argument is a
    name. The second argument is the type, one of `string`, `float`,
    `integer` or `boolean`.

:class:`ComplexInput`
    A large data object, for example a layer. The first argument is a
    name. The second argument is a list of one or more formats, e.g.
    ``text/xml`` for GML files or ``application/json`` for GeoJSON
    files.

:class:`LiteralOutput`
    A simple value embedded in the response. The first argument is a
    name. The second argument is the type, one of `string`, `float`,
    `integer` or `boolean`.

:class:`ComplexOutput`
    Same as :class:`ComplexInput`. The first argument is a
    name. The second argument is a list of one or more formats, e.g.
    ``text/xml`` for GML files or ``application/json`` for GeoJSON
    files.


Reading input
~~~~~~~~~~~~~
Handlers receive an input argument, a :class:`WPSRequest` object. Input
values are found in the `inputs` dictionary::

    @staticmethod
    def _handler(request, response):
        name = request.inputs['name'][0].data
        response.outputs['output'].data = 'Hello world %s!' % name
        return response

`inputs` is a plain Python dictionary.
Input can be set and read in different ways including as a file, as data
- like string or numbers - or as a stream::

    request.inputs['file_input'][0].file
    request.inputs['data_input'][0].data
    request.inputs['stream_input'][0].stream

Because there could be multiple input values with the same identifier, the inputs are accessed with an index.
For `LiteralInput`, the value is a string. For `ComplexInput`, the value
is an open file object, with a `mime_type` attribute::

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
~~~~~~~~~~~~~~~~~~~~
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


Publishing a process
~~~~~~~~~~~~~~~~~~~~
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

    ...
    processes = [ HelloWorld() ]

    server = Server(processes=processes)
    ...

The *demo* application is a `WSGI application`_ that accepts incoming `Execute`
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


