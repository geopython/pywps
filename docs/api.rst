#############
PyWPS API Doc
#############

.. module:: pywps


Process
=======

.. autoclass:: Process

Exceptions you can raise in the process implementation to show a user-friendly error message.

.. autoclass:: pywps.app.exceptions.ProcessError

Inputs and outputs
==================

.. autoclass:: pywps.validator.mode.MODE
    :members:
    :undoc-members:

Most of the inputs nad outputs are derived from the `IOHandler` class

.. autoclass:: pywps.inout.basic.IOHandler


LiteralData
-----------

.. autoclass:: LiteralInput

.. autoclass:: LiteralOutput

.. autoclass:: pywps.inout.literaltypes.AnyValue

.. autoclass:: pywps.inout.literaltypes.AllowedValue

.. autoclass:: pywps.inout.literaltypes.ValuesReference

.. autodata:: pywps.inout.literaltypes.LITERAL_DATA_TYPES


ComplexData
-----------

.. autoclass:: ComplexInput

.. autoclass:: ComplexOutput

.. autoclass:: Format

.. autodata:: pywps.inout.formats.FORMATS
    :annotation:

    List of out of the box supported formats. User can add custom formats to the
    array.

.. autofunction:: pywps.validator.complexvalidator.validategml

BoundingBoxData
---------------

.. autoclass:: BoundingBoxInput

.. autoclass:: BoundingBoxOutput

Request and response objects
----------------------------

.. autodata:: pywps.response.status.WPS_STATUS
    :annotation:

    Process status information

.. autoclass:: pywps.app.WPSRequest
   :members:

   .. attribute:: operation

      Type of operation requested by the client. Can be
      `getcapabilities`, `describeprocess` or `execute`.

   .. attribute:: http_request

      .. TODO link to werkzeug docs

      Original Werkzeug HTTPRequest object.

   .. attribute:: inputs

      .. TODO link to werkzeug docs

      A MultiDict object containing input values sent by the client.


.. autoclass:: pywps.response.WPSResponse
    :members:

    .. attribute:: status

        Information about currently running process status
        :class:`pywps.response.status.STATUS`

Processing
----------

.. autofunction:: pywps.processing.Process

.. autoclass:: pywps.processing.Processing
   :members:

.. autoclass:: pywps.processing.Job
   :members:


Refer :ref:`exceptions` for their description.
