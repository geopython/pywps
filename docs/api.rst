#############
PyWPS API Doc
#############

.. module:: pywps


Process
=======

.. autoclass:: Process

Inputs and outputs
==================

.. autoclass:: pywps.validator.mode.MODE
    :members:
    :undoc-members:


LiteralData
-----------

.. autoclass:: LiteralInput

.. autoclass:: LiteralOutput

.. autoclass:: pywps.inout.literaltypes.AnyValue

.. autoclass:: pywps.inout.literaltypes.AllowedValue

.. autodata:: pywps.inout.literaltypes.LITERAL_DATA_TYPES


ComplexData
-----------

.. autoclass:: ComplexInput

.. autoclass:: ComplexOutput

.. autoclass:: Format
    
.. autodata:: pywps.inout.formats.FORMATS

BoundingBoxData
---------------

.. autoclass:: BoundingBoxInput

.. autoclass:: BoundingBoxOutput

Request and response objects
----------------------------

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

.. autoclass:: pywps.app.WPSResponse

Refer :ref:`exceptions` for their description.
