.. currentmodule:: pywps

=========
Processes
=========

PyWPS works with processes and services. A process is a handler function
and some input specification. A service is a collection of processes.


Writing a handler
~~~~~~~~~~~~~~~~~
The handler is a function (or any callable object), that takes a request
object as argument, and returns a response object. Like so::

    from pywps import WPSResponse

    def handler(request):
        return WPSResponse({'msg': "Hello world!"})

The :class:`WPSResponse` class accepts a dictionary of output names and
values. The values can be strings (that become literal outputs) or
:class:`FileReference` objects (that become complex outputs).


Reading input
~~~~~~~~~~~~~
Handlers receive a single argument, a :class:`WPSRequest` object. Input
values are found in the `inputs` dictionary::

    def handler(request):
        name = request.inputs['name']
        return WPSResponse({'message': "Hello %s!" % name})

Actually, `inputs` is not a plain Python dictionary, but a
`MultiDict`_ object, that can store multiple values for a single key.

.. _MultiDict: http://werkzeug.pocoo.org/docs/datastructures/#werkzeug.datastructures.MultiDict

For `LiteralInput`, the value is a string. For `ComplexInput`, the value
is an open file object, with a `mime_type` attribute::

    def handler(request):
        layer_file = request.inputs['layer']
        mime_type = layer_file.mime_type
        bytes = layer_file.read()
        msg = ("You gave me a file of type %s and size %d"
               % (mime_type, len(bytes)))
        return WPSResponse({'message': msg})


Returning large data
~~~~~~~~~~~~~~~~~~~~
WPS allows for a clever method of returning a large data file: instead
of embedding the data in the response, we can save it separately, and
return a URL where the data can be downloaded. In the current
implementation, it's up to you to figure out how to save the data so
it's accessible at a URL, but if you have such a URL, you can
communicate it to the client, by wrapping it in a
:class:`FileReference`::

    from pywps import FileReference

    def handler(request):
        # ... do some computation and save the output
        # as GeoJSON at the address `url` ...
        ref = FileReference(url, 'application/json')
        return WPSResponse({'layer': ref})


Publishing a process
~~~~~~~~~~~~~~~~~~~~
In order to let clients call our process, we need to build a PyWPS
:class:`Service` and have it listen for requests. Firstly we build a
:class:`Process` object that knows about our handler::

    from pywps import Process

    process = Process(handler)

By default the process has its `Identifier` set to the function's name,
but we can override it::

    process = Process(handler, identifier='magic_process')

Then we build a :class:`Service` object that knows about any number of
processes::

    from pywps import Service

    service = Service([process])

The service is a `WSGI application`_ that accepts incoming `Execute`
requests and calls the appropriate process to handle them. It also
answers `GetCapabilities` and `DescribeProcess` requests based on the
process names and their inputs and outputs.

.. _WSGI application: http://werkzeug.pocoo.org/docs/terms/#wsgi

For testing purposes we can easily publish our service using the
development server in Werkzeug. Replace ``localhost`` with ``0.0.0.0``
if you want the server to be visible from another computer. Also, since
we specify ``use_reloader=True``, the server will restart itself if any
of the Python source files are changed::

    from werkzeug.serving import run_simple

    run_simple('localhost', 5000, service, use_reloader=True)


Declaring inputs and outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Clients need to know what our processes expect as input. We can declare
the expected input when creating a :class:`Process` object::

    from pywps import LiteralInput, ComplexInput

    process = Process(handler, inputs=[
        LiteralInput('foo', 'string'),
        ComplexInput('bar', [Format('text/xml')]),
    ])

:class:`LiteralInput`
    A simple value embedded in the request. The first argument is a
    name. The second argument is the type, one of `string`, `float`,
    `integer` or `boolean`.

:class:`ComplexInput`
    A large data object, for example a layer. The first argument is a
    name. The second argument is a list of one or more formats, e.g.
    ``text/xml`` for GML files or ``application/json`` for GeoJSON
    files.

Currently, incoming requests are not checked against the declared
inputs, the declaration only serves to inform clients about the service,
if they send a `DescribeProcess` request. There is no way to declare
outputs yet, but QGIS doesn't seem to mind.
