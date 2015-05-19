.. currentmodule:: pywps

=========
Processes
=========

PyWPS-4 works with processes and services. A process is a class with a handler function
and some input specification. A service is a collection of processes.


Writing a process class
~~~~~~~~~~~~~~~~~~~~~~~

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

The handler is a function (or any callable object), that takes a request and a response
object as argument, and returns a response object. Like so::

    @staticmethod
    def _handler(request, response):
        response.outputs['output'].data = 'Hello world!'
        return response

request is an instance of :class:`WPSRequest`.
response is an instance of :class:`WPSResponse`.

These classes accept :class:`LiteralInput`
values. The values can be strings (that become literal outputs) or
:class:`FileReference` objects (that become complex outputs).


Reading input
~~~~~~~~~~~~~
Handlers receive an input argument, a :class:`WPSRequest` object. Input
values are found in the `inputs` dictionary::

    @staticmethod
    def _handler(request, response):
        name = request.inputs['name'].data
        response.outputs['output'].data = 'Hello world %s!' % name
        return response

`inputs` is a plain Python dictionary.
Input can be set and read in different ways including as a file, as data
like string or numbers or as a stream::

    request.inputs['file_input'].file
    request.inputs['data_input'].data
    request.inputs['stream_input'].stream

For `LiteralInput`, the value is a string. For `ComplexInput`, the value
is an open file object, with a `mime_type` attribute::

    @staticmethod
    def handler(request, response):
        layer_file = request.inputs['layer'].file
        mime_type = layer_file.mime_type
        bytes = layer_file.read()
        msg = ("You gave me a file of type %s and size %d"
               % (mime_type, len(bytes)))
        response.outputs['output'].data = msg
        return response


Returning large data
~~~~~~~~~~~~~~~~~~~~
WPS allows for a clever method of returning a large data file: instead
of embedding the data in the response, we can save it separately, and
return a URL where the data can be downloaded. In the current
implementation, PyWPS-4 core will save the file in a folder specified
in the configuration passed by the server application or in a default location
and return the URL embedded in the XML response.

This behaviour can be requested either by using GET::

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

**output** is the identifier of the output you wish to have it stored
and accessible from a URL. Only *one output can be requested as reference.


Publishing a process
~~~~~~~~~~~~~~~~~~~~
In order to let clients call our process, we need to build a PyWPS
:class:`Service` and have it listen for requests. Firstly we build a
:class:`Process` object which will be located in our demo application
in ``demo/processes/``. This process will know about our handler.

By default the process has its **Identifier** set to the function's name,
but we can override it. In the process constructor::

    class HelloWorld(Process):
        def __init__(self):
            ...
            super(HelloWorld, self).__init__(
                self._handler,
                identifier='magic_process',
                ...
            )

When making a request we need to specify nw **magic_process** as identifier instead.

Then we build a :class:`Service` object that knows about any number of
processes::

    from pywps import Service
    from processes.helloworld import HelloWorld

    ...
    processes = [ HelloWorld() ]

    service = Service(processes=processes)
    ...

The service is a `WSGI application`_ that accepts incoming `Execute`
requests and calls the appropriate process to handle them. It also
answers `GetCapabilities` and `DescribeProcess` requests based on the
process identifier and their inputs and outputs.

.. _WSGI application: http://werkzeug.pocoo.org/docs/terms/#wsgi

For testing purposes we can easily publish our service using the :class:`Server`
using the development server in Flask. Replace ``localhost`` with ``0.0.0.0``
if you want the server to be visible from another computer.
In the demo application we have the demo.py which creates a server
of :class:`Server` inheriting from :class:`PyWPSAbstract`.
We can pass a host, a port, a config file and the processes.
**host** and **port** will be **prioritized** if passed to the constructor then
it takes the config file and if no file is passed the server will use default values.
Use `run` method start the server::


    ...
    s = Server(host='0.0.0.0', processes=processes, config_file=config_file)

    s.run()
    ...


Declaring inputs and outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Clients need to know what our processes expect as input. We can declare
the expected input when creating a :class:`Process` object::


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

Currently, incoming requests are not checked against the declared
inputs, the declaration only serves to inform clients about the service,
if they send a `DescribeProcess` request.
