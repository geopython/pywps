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

All data types do need to have

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

LiteralData
~~~~~~~~~~~
Literal data is any text string. They can have 

