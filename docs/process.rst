.. currentmodule:: pywps

.. _process:

Processes
#########

.. versionadded:: 4.0.0

.. todo::
    * Input validation
    * IOHandler

PyWPS works with processes and services. A process is a Python `Class`
containing an `handler` method and a list of inputs and outputs. A PyWPS
service instance is then a collection of selected processes.

PyWPS does not ship with any processes predefined - it's on you, as user of
PyWPS to set up the processes of your choice. PyWPS is here to help you
publishing your awesome geospatial operation on the web - it takes care of
communication and security, you then have to add the content.

.. note:: There are some example processes in the `PyWPS-Flask`_ project.

Writing a Process
=================

.. note:: At this place, you should prepare your environment for final
        :ref:`deployment`. At least, you should create a single directory with
        your processes, which is typically named `processes`::

        $ mkdir processes

        In this directory, we will create single python scripts containing
        processes.

        Processes can be located *anywhere in the system* as long as their
        location is identified in the :envvar:`PYTHONPATH` environment
        variable, and can be imported in the final server instance.

A processes is coded as a class inheriting from :class:`Process`.
In the `PyWPS-Flask`_ server they are
kept inside the *processes* folder, usually in separated files.

The instance of a *Process* needs following attributes to be configured:

:identifier:
    unique identifier of the process
:title:
    corresponding title
:inputs:
    list of process inputs
:outputs:
    list of process outputs
:handler:
    method which recieves :class:`pywps.app.WPSRequest` and :class:`pywps.response.WPSResponse` as inputs.

Example vector buffer process
=============================

As an example, we will create a *buffer* process - which will take a vector
file as the input, create specified the buffer around the data (using `Shapely
<https://shapely.readthedocs.io>`_),  and return back the result.

Therefore, the process will have two inputs:

* `ComplexData` input - the vector file
* `LiteralData` input - the buffer size

And it will have one output:

* `ComplexData` output - the final buffer

The process can be called `demobuffer` and we can now start coding it::

    $ cd processes
    $ $EDITOR demobuffer.py

At the beginning, we have to import the required classes and modules

Here is a very basic example:

.. literalinclude:: demobuffer.py
   :language: python
   :lines: 28-31
   :linenos:
   :lineno-start: 28

As the next step, we define a list of inputs. The first input is
:class:`pywps.ComplexInput` with the identifier `vector`, title `Vector map`
and there is only one allowed format: GML.

The next input is :class:`pywps.LiteralInput`, with the identifier `size` and
the data type set to `float`:

.. literalinclude:: demobuffer.py
   :language: python
   :lines: 33-40
   :linenos:
   :lineno-start: 33

Next we define the output `output` as :class:`pywps.ComplexOutput`. This
output supports GML format only.

.. literalinclude:: demobuffer.py
   :language: python
   :lines: 42-46
   :linenos:
   :lineno-start: 42

Next we create a new list variables for inputs and outputs.

.. literalinclude:: demobuffer.py
   :language: python
   :lines: 48-49
   :linenos:
   :lineno-start: 48

Next we define the *handler* method. In it, *geospatial analysis
may happen*. The method gets a :class:`pywps.app.WPSRequest` and a
:class:`pywps.response.WPSResponse` object as parameters. In our case, we
calculate the buffer around each vector feature using
`GDAL/OGR library <https://gdal.org>`_. We will not got much into the details,
what you should note is how to get input data from the
:class:`pywps.app.WPSRequest` object and how to set data as outputs in the
:class:`pywps.response.WPSResponse` object.

.. literalinclude:: demobuffer.py
   :language: python
   :pyobject: _handler
   :emphasize-lines: 8-12, 50-54
   :linenos:
   :lineno-start: 68

At the end, we put everything together and create new a `DemoBuffer` class with
handler, inputs and outputs. It's based on :class:`pywps.Process`:

.. literalinclude:: demobuffer.py
   :pyobject: DemoBuffer
   :language: python
   :linenos:
   :lineno-start: 51


Declaring inputs and outputs
============================

Clients need to know which inputs the processes expects. They can be declared
as :class:`pywps.Input` objects in the :class:`Process` class declaration:

.. code-block:: python

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

.. note:: A more generic description can be found in :ref:`wps` chapter.

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

A large data object, for example a layer. ComplexData do have a `format`
attribute as one of their key properties. It's either a list of supported
formats or a single (already selected) format. It shall be an instance of
the :class:`pywps.inout.formats.Format` class.

ComplexData :class:`Format` and input validation
------------------------------------------------
The ComplexData needs as one of its parameters a list of supported data
formats. They are derived from the :class:`Format` class. A :class:`Format`
instance needs, among others, a `mime_type` parameter, a `validate`
method -- which is used for input data validation -- and also a `mode`
parameter -- defining how strict the validation should be (see
:class:`pywps.validator.mode.MODE`).

The `Validate` method is up to you, the user, to code. It requires two input
paramers - `data_input` (a :class:`ComplexInput` object), and `mode`. This
methid must return a `boolean` value indicating whether the input data are
considered valid or not for given `mode`. You can draw inspiration from the
:py:func:`pywps.validator.complexvalidator.validategml` method.

The good news is: there are already predefined validation methods for the ESRI
Shapefile, GML and GeoJSON formats, using GDAL/OGR. There is also an XML Schema
validaton and a JSON schema validator - you just have to pick the propper
supported formats from the :class:`pywps.inout.formats.FORMATS` list and set
the validation mode to your :class:`ComplexInput` object.

Even better news is: you can define custom validation functions and validate
input data according to your needs.

BoundingBoxData
---------------

* :class:`BoundingBoxInput`
* :class:`BoundingBoxOutput`

BoundingBoxData contain information about the bounding box of the desired area
and coordinate reference system. Interesting attributes of the BoundingBoxData
are:

`crs`
    current coordinate reference system
`dimensions`
    number of dimensions
`ll`
    pair of coordinates (or triplet) of the lower-left corner
`ur`
    pair of coordinates (or triplet) of the upper-right corner


Accessing the inputs and outputs in the `handler` method
========================================================

Handlers receive as input argument a :class:`WPSRequest` object. Input
values are found in the `inputs` dictionary::

    @staticmethod
    def _handler(request, response):
        name = request.inputs['name'][0].data
        response.outputs['output'].data = 'Hello world %s!' % name
        return response

`inputs` is a plain Python dictionary.
Most of the inputs and outputs are derived from the :class:`IOHandler` class.
This enables the user to access the data in four different ways:

`input.file`
    Returns a file name - you can access the data using the name of the file
    stored on the hard drive.
`input.url`
    Return a link to the resource using either the ``file://`` or ``http://`` scheme. The target of the url is not downloaded to the PyWPS server until its content is explicitly accessed through either one of the ``file``, ``data`` or ``stream`` attributes.
`input.data`
    Is the direct link to the data themselves. No need to create a file object
    on the hard drive or opening the file and closing it - PyWPS will do
    everything for you.
`input.stream`
    Provides the IOStream of the data. No need for opening the file, you just
    have to `read()` the data.

Because there could be multiple input values with the same identifier, the
inputs are accessed with an index. For example::

    request.inputs['file_input'][0].file
    request.inputs['data_input'][0].data
    request.inputs['stream_input'][0].stream
    url_input = request.inputs['url_input'][0]

As mentioned, if an input is a link to a remote file (an ``http`` address), accessing the ``url`` attribute simply returns the url's string, but accessing any other attribute triggers the file's download::

    url_input.url # returns the link as a string (no download)
    url_input.file # downloads target and returns the local path
    url_input.data # returns the content of the local copy


PyWPS will persistently transform the input (and output) data to the desired
form. You can also set the data for your `Output` object like `output.data = 1`
or `output.file = "myfile.json"` - it works the same way. However, once the source
type is set, it cannot be changed. That is, a `ComplexOutput` whose ``data``
attribute has been set once has read-only access to the three other attributes
(``file``, ``stream`` and ``url``), while the ``data`` attribute can be freely
modified.


Progress and status report
==========================

OGC WPS standard enables asynchronous process execution call, that is in
particular useful, when the process execution takes longer time - process
instance is set to background and WPS Execute Response document with `ProcessAccepted`
messag is returned immediately to the client. The client has to check
`statusLocation` URL, where the current status report is deployed, say every
n-seconds or n-minutes (depends on calculation time). Content of the response is
usually `percentDone` information about the progress along with `statusMessage`
text information, what is currently happening.

You can set process status any time in the `handler` using the
:py:func:`WPSResponse.update_status` function.


Returning large data
====================
WPS allows for a clever method of returning a large data file: instead
of embedding the data in the response, it can be saved separately, and
a URL is returned from where the data can be downloaded. In the current
implementation, PyWPS saves the file in a folder specified
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

**output** is the identifier of the output the user wishes to have stored
and accessible from a URL. The user may request as many outputs by reference
as needed, but only *one* may be requested in RAW format.

Returning multiple files
========================

When a process accepts a variable number of inputs, it often makes sense to
return a variable number of outputs. The WPS standard does not however readily
accommodate this. One pragmatic solution is to compress the files into a single
output archive (e.g. zip file), but this proves to be awkward when the outputs
are really just references to resources (URLs). In this case, another pragmatic
solution is to return a simple text file storing the list of references. One
issue with this is that it provides clients very little metadata about the file
content.

Although it would be fairly easy to define a json output file storing the
properties and URLs of multiple files, it would require an ad-hoc
implementation on the client side to parse the json and extract the urls
metadata. Fortunately, the `metalink`_ standard already exists precisely to
bundle references to multiples files.

Metalink files are XML documents collecting a set of remote files. It was originally
designed to describe the location of larges files stored on multiple mirrors or
peer-to-peer networks. If one location goes down during download, metalink
clients can switch to another mirror. Also, large files can be split into
segments and downloaded concurrently from different locations, speeding up
downloads. A metalink can also describe the location of files made for different
operating systems and languages, with clients automatically selecting the most
appropriate one.

Metalink support in PyWPS includes:

- `pywps.FORMATS.METALINK` and `pywps.FORMATS.META4`
- helper classes :class:`MetaFile`, :class:`MetaLink` and :class:`MetaLink4`
- validation of generated metalink files using XML schemas
- size (bytes) and checksums (sha-256) for each file in the metalink document

To use metalink in a process, define a :class:`ComplexOutput` with a metalink
mimetype. Then after the handler has generated a list of file, instantiate
one :class:`MetaFile` object for each output file, and append them to a
:class:`MetaLink` or :class:`MetaLink4` instance. Finally, set the data property
of the output to the xml generated by the `xml` property of the :class:`MetaLink`
instance.

.. note::

  :class:`MetaLink` uses metalink standard version 3.0, while :class:`MetaLink4`
  uses version 4.0.

Example process
---------------

.. literalinclude:: metalinkprocess.py
   :language: python

Process Exceptions
==================

Any uncatched exception in the process execution will be handled by PyWPS and reported
to the WPS client using an `ows:Exception`. PyWPS will only log the traceback and report
a common error message like:

    *Process failed, please check server error log.*

This sparse error message is used to avoid security issues by providing internal
service information in an uncontrolled way.

But in some cases you want to provide a user-friendly error message to give the user a hint of
what went wrong with the processing job. In this case you can use the :class:`pywps.app.exceptions.ProcessError`
exception. The error message will be send to the user encapsulated as `ows:Exception`.
The :class:`pywps.app.exceptions.ProcessError` validates the error message to make sure it is not too long
and it does not contain any suspicious characters.

.. note::
    By default a valid error message must have a length between 3 and 144 characters.
    Only alpha-numeric characters and a few special ones are allowed.
    The allowed special characters are: ".", ":", "!", "?", "=", ",", "-".

.. note::
    During the process development you might want to get a traceback shown in `ows:Exception`.
    This is possible by running PyWPS in debug mode. In `pywps.cfg` config file set::

        [logging]
        level=DEBUG

Example process
---------------

.. literalinclude:: show_error.py
   :language: python

Process deployment
==================
In order for clients to invoke processes, a PyWPS
:class:`Service` class must be present with the ability to listen for requests.
An instance of this class must created, receiving instances of
all the desired processes classes.

In the *flask* example service the :class:`Service` class instance is created in the
:class:`Server` class. :class:`Server` is a development server that relies
on `Flask`_. The publication of processes is encapsulated in *demo.py*, where
a main method passes a list of processes instances to the
:class:`Server` class::

    from pywps import Service
    from processes.helloworld import HelloWorld
    from processes.demobuffer import DemoBuffer

    ...
    processes = [ DemoBuffer(), ... ]

    server = Server(processes=processes)

    ...

Running the dev server
======================

The :ref:`flask` server is a `WSGI application`_ that accepts incoming `Execute`
requests and calls the appropriate process to handle them. It also
answers `GetCapabilities` and `DescribeProcess` requests based on the
process identifier and their inputs and outputs.

.. _WSGI application: http://werkzeug.pocoo.org/docs/terms/#wsgi


A host, a port, a config file and the processes can be passed as arguments to the
:class:`Server` constructor.
**host** and **port** will be **prioritised** if passed to the constructor,
otherwise the contents of the config file (`pywps.cfg`) are used.


Use the `run` method to start the server::

    ...
    s = Server(host='localhost', processes=processes, config_file=config_file)
    s.run()
    ...

To make the server visible from another computer, replace ``localhost`` with ``0.0.0.0``.

Supporting multiple languages
=============================

Supporting multiple languages requires:

- Setting the `language` property in the server configuration (see :ref:`server-configuration`)
- Adding translations to :class:`Process`, inputs and outputs objects

The expected translations format is always the same. The first key is the RFC 4646 language code, 
and the nested mapping contains translated strings accessible by a string property::

    from pywps import Process, LiteralInput, LiteralOutput


    class SayHello(Process):
        def __init__(self):
            inputs = [
                LiteralInput(
                    'name',
                    title='Input name',
                    abstract='The name to say hello to.',
                    translations={"fr-CA": {"abstract": "Le nom à saluer."}}
                )
            ],
            outputs=[
                LiteralOutput(
                    'response',
                    title='Output response',
                    abstract='The complete output message.',
                    translations={"fr-CA": {
                        "title": "La réponse", 
                        "abstract": "Le message complet."
                    }}
                )
            ],

            super().__init__(
                self._handler,
                identifier='say_hello',
                title='Process Say Hello',
                abstract='Returns a literal string output with Hello plus the inputed name',
                version='1.0',
                inputs=inputs,
                outputs=outputs,
                store_supported=True,
                status_supported=True,
                translations={"fr-CA": {
                    "title": "Processus Dire Bonjour", 
                    "abstract": "Retourne une chaine de caractères qui dit bonjour au nom fournit en entrée."
                }},
            )

        def _handler(self, request, response):
            ...

The translation will default to the untranslated attribute of the base object if 
the key is not provided in the `translations` dictionnary.

Automated process documentation
===============================

A :class:`Process` can be automatically documented with `Sphinx`_ using the
`autoprocess` directive. The :class:`Process` object is instantiated and its
content examined to create, behind the scenes, a docstring in the Numpy format. This
lets developers embed the documentation directly in the code instead of having to
describe each process manually. For example::

  .. autoprocess:: pywps.tests.DocExampleProcess
     :docstring:
     :skiplines: 1

would yield

.. autoprocess:: pywps.tests.DocExampleProcess
   :docstring:
   :skiplines: 1

The :option:`docstring` option fetches the :class:`Process` docstring and appends it after the
Reference section. The first lines of this docstring can be skipped using the
:option:`skiplines` option.

To use the `autoprocess` directive, first add `'sphinx.ext.napoleon'` and
`'pywps.ext_autodoc'` to the list of extensions in the Sphinx configuration file
:file:`conf.py`. Then, insert `autoprocess` directives in your documentation
source files, just as you would use an `autoclass` directive, and build the
documentation.

Note that for input and output parameters, the `title` is displayed only if no `abstract`
is defined. In other words, if both `title` and `abstract` are given, only the `abstract`
will be included in the documentation to avoid redundancy.

.. _Flask: http://flask.pocoo.org
.. _PyWPS-Flask: https://github.com/geopython/pywps-flask
.. _Sphinx: http://sphinx-doc.org
.. _`metalink`: http://www.metalinker.org/
