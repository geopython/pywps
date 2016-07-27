.. _wps:

====================================
OGC Web Processing Service (OGC WPS)
====================================

`OGC Web Processing Service <http://opengeospatial.org/standards>`_ standard
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

WPS is intented to be state-less protocol (like any OGC services). For every
request-response action, the negotiation between the server and the client has
to start. There is no official way, how to make the server "remember", what was
before, there is no communication history between the server and the client.

.. todo::
    * KVP vs XML encoding
    * GET vs POST request

Process
-------

A process `p` is a function that for each input returns a corresponding output

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

Every process has

Identifier
    Unique process identifier

Title
    Human readable title

Abstract
    Longer description of the process, what it does, how is it supposed to be
    used

And list of in- and outputs.

Data in- and outputs
--------------------
OGC WPS defines 3 types of data inputs and data outputs *LiteralData*,
*ComplexData* and *BoundingBoxData*.

All data types do need to have following attributes:

Identifier
    Unique input identifier

Title
    Human readable title

Abstract
    Longer description of data input or output, so that the user could get
    oriented.

minOccurs
    Minimal occurence of the input (e.g. there can be more bands of raster file
    and they all can be passed as input using the same identifier)

maxOccurs
    Maxium number of times, the input or output is present

Depending on the data type (Literal, Complex, BoundingBox), other attributes
might occure too.

LiteralData
~~~~~~~~~~~
Literal data is any text string, usually short. It's used for passing single
parameters like numbers or text parameters. WPS enables to the server, to define
`allowedValues` - list or intervals of allowed values, as well as data type
(integer, float, string).  Aditional attributes can be set, such as `units` or
`encoding`.

ComplexData
~~~~~~~~~~~
Complex data are usually raster or vector files, but basically any (usually
file based) data, which are usually processed (or result of the process). The
input can be specified more using `mimeType`, xml `schema` or `encoding` (such
as `base64` for raster data.

.. note:: PyWPS (like every server) supports limited list `mimeTypes`. In case
        you need some new format, just create pull request in our repository.
        Refer :const:`pywps.inout.formats.FORMATS` for more details.

Usually, the minimum requirement for input data identification is `mimeType`.
That usually is `application/gml+xml` for `GML
<http://opengeospatial.org/standards/gml>`_-encoded vector files, `image/tiff;
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
There are 3 typical ways, how to pass the input data from the client to the
server:

**Data are on the server already**
    In the first case, the data are already stored on the server (from the point
    of view of the client). This is the simpliest case.

**Data are send to the server along with the request**
    In this case, the data are directly part of the XML encoded document send via
    HTTP POST. Some clients/servers are expecting the dat to be inserted in
    `CDATA` section. The data can be text based (JSON), XML based (GML) or even
    raster based - in this case, they are usually encoded using `base64
    <https://docs.python.org/3/library/base64.html>`_.

**Reference link to target service is passed**
    Client does not have to pass the data itself, client can just send reference
    link to target data service (or file). In such case, for example OGC WFS
    `GetFeatureType` URL can be passed and server will dowload the data
    automatically.

    Altough this is usually used for `ComplexData` input type, it can be used
    for literal and bouding box data too.

