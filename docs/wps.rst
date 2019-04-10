.. _wps:

OGC Web Processing Service (OGC WPS)
====================================

`OGC Web Processing Service <https://opengeospatial.org/standards>`_ standard
provides rules for standardizing how inputs and outputs (requests and
responses) for geospatial processing services. The standard also defines how a
client can request the execution of a process, and how the output from the
process is handled. It defines an interface that facilitates the publishing of
geospatial processes and clients discovery of and binding to those processes.
The data required by the WPS can be delivered across a network or they can be
available at the server.

.. note:: This description is mainly refering to 1.0.0 version standard, since
        PyWPS implements this version only. There is also 2.0.0 version, which
        we are about to implement in near future.

WPS is intended to be state-less protocol (like any OGC services). For every
request-response action, the negotiation between the server and the client has
to start. There is no official way, how to make the server "remember", what was
before, there is no communication history between the server and the client.

Process
-------

A process `p` is a function that for each input returns a corresponding output:

.. math::

        p: X \rightarrow Y

where `X` denotes the domain of arguments `x` and `Y` denotes the co-domain of values `y`.

Within the specification, process arguments are referred to as *process inputs* and result
values are referred to as *process outputs*. Processes that have no process inputs represent
value generators that deliver constant or random process outputs.

*Process* is just some geospatial operation, which has it's in- and outputs and
which is deployed on the server. It can be something relatively simple (adding
two raster maps together) or very complicated (climate change model). It can
take short time (seconds) or long (days) to be calculated. Process is, what you,
as PyWPS user, want to expose to other people and let their data processed.

Every process has the following properties:

Identifier
    Unique process identifier

Title
    Human readable title

Abstract
    Longer description of the process, what it does, how is it supposed to be
    used

And a list of inputs and outputs.

Data inputs and outputs
-----------------------

OGC WPS defines 3 types of data inputs and outputs: *LiteralData*,
*ComplexData* and *BoundingBoxData*.

All data types do need to have following properties:

Identifier
    Unique input identifier

Title
    Human readable title

Abstract
    Longer description of data input or output, so that the user could get
    oriented.

minOccurs
    Minimal occurrence of the input (e.g. there can be more bands of raster file
    and they all can be passed as input using the same identifier)

maxOccurs
    Maxium number of times, the input or output is present

Depending on the data type (Literal, Complex, BoundingBox), other attributes
might occur too.

LiteralData
~~~~~~~~~~~
Literal data is any text string, usually short. It's used for passing single
parameters like numbers or text parameters. WPS enables to the server, to define
`allowedValues` - list or intervals of allowed values, as well as data type
(integer, float, string).  Additional attributes can be set, such as `units` or
`encoding`.

ComplexData
~~~~~~~~~~~
Complex data are usually raster or vector files, but basically any (usually
file based) data, which are usually processed (or result of the process). The
input can be specified more using `mimeType`, XML `schema` or `encoding` (such
as `base64` for raster data.

.. note:: PyWPS (like every server) supports limited list `mimeTypes`. In case
        you need some new format, just create pull request in our repository.
        Refer :const:`pywps.inout.formats.FORMATS` for more details.

Usually, the minimum requirement for input data identification is `mimeType`.
That usually is `application/gml+xml` for `GML
<https://opengeospatial.org/standards/gml>`_-encoded vector files, `image/tiff;
subtype=geotiff` for raster files. The input or output can also be result of any
OGC OWS service.

BoundingBoxData
~~~~~~~~~~~~~~~
.. todo:: add reference to OGC OWS Common spec

BoundingBox data are specified in OGC OWS Common specification as two pairs of
coordinate (for 2D and 3D space). They can either be encoded in WGS84 or EPSG
code can be passed too. They are intended to be used as definition of the target
region.

.. note:: In real life, BoundingBox data are not that commonly used

Passing data to process instance
--------------------------------
There are typically 3 approaches to pass the input data from the client to the
server:

**Data are on the server already**
    In the first case, the data are already stored on the server (from the point
    of view of the client). This is the simplest case.

**Data are send to the server along with the request**
    In this case, the data are directly part of the XML encoded document send via
    HTTP POST. Some clients/servers are expecting the data to be inserted in
    `CDATA` section. The data can be text based (JSON), XML based (GML) or even
    raster based - in this case, they are usually encoded using `base64
    <https://docs.python.org/3/library/base64.html>`_.

**Reference link to target service is passed**
    Client does not have to pass the data itself, client can just send reference
    link to target data service (or file). In such case, for example OGC WFS
    `GetFeatureType` URL can be passed and server will download the data
    automatically.

    Although this is usually used for `ComplexData` input type, it can be used
    for literal and bounding box data too.

Synchronous versus asynchronous process request
-----------------------------------------------

There are two modes of process instance execution: Synchronous and asynchronous.

Synchronous mode
    The client sends the `Execute` request to the server and waits with open
    server connection, till the process is calculated and final response is
    returned back. This is useful for fast calculations which do not take
    longer then a couple of seconds (`Apache2 httpd server uses 300 seconds <https://httpd.apache.org/docs/2.4/mod/core.html#timeout>`_ as default value for ConnectionTimeout).

Asynchronous mode
    Client sends the `Execute` request with explicit request for asynchronous
    mode. If supported by the process (in PyWPS, we have a configuration for
    that), the server returns back `ProcessAccepted` response immediately with
    URL, where the client can regularly check for *process execution status*. 

    .. note:: As you see, using WPS, the client has to apply *pull* method for
        the communication with the server. Client has to be the active element
        in the communication - server is just responding to clients request and
        is not actively *pushing* any information (like it would if e.g. web
        sockets would be implemented).

Process status
--------------
`Process status` is generic status of the process instance, reporting to the
client, how does the calculation go. There are 4 types of process statuses

ProcessAccepted
    Process was accepted by the server and the process execution will start
    soon.

ProcessStarted
    Process calculation has started. The status also contains report about
    `percentDone` - calculation progress and `statusMessage` - text reporting
    current calculation state (example: *"Caculationg buffer"* - 33%).

ProcessFinished
    Process instance performed the calculation successfully and the final
    `Execute` response is returned to the client and/or stored on final location

ProcessFailed
    There was something wrong with the process instance and the server reports
    `server exception` (see :py:mod:`pywps.exceptions`) along with the message,
    what could possibly go wrong.

Request encoding, HTTP GET and POST
-----------------------------------

The request can be encoded either using key-value pairs (KVP) or an XML payload.

Key-value pairs
    is usually sent via `HTTP GET request method
    <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods>`_
    encoded directly in the URL. The keys and values are separated with `=` sign and
    each pair is separated with `&` sign (with `?` at the beginning of the request.
    Example could be the *get capabilities reques*::

            http://server.domain/wps?service=WPS&request=GetCapabilities&version=1.0.0

    In this example, there are 3 pairs of input parameter: `service`, `request` and
    `version` with values `WPS`, `GetCapabilities` and `1.0.0` respectively.

XML payload
    is XML data sent via `HTTP POST request method
    <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods>`_.
    The XML document can be more rich, having more parameters, better to be
    parsed in complex structures. The Client can also encode entire datasets to the
    request, including raster (encoded using base64) or vector data (usually as GML file).::

        <?xml version="1.0" encoding="UTF-8"?>
        <wps:GetCapabilities language="cz" service="WPS" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_request.xsd">
          <wps:AcceptVersions>
            <ows:Version>1.0.0</ows:Version>
          </wps:AcceptVersions>
        </wps:GetCapabilities>

.. note:: Even it might be looking more complicated to use XML over KVP, for
        some complex request it usually is more safe and efficient to use XML
        encoding. The KVP way, especially for WPS Execute request can be tricky
        and lead to unpredictable errors.
