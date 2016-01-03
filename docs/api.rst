===
API
===

.. module:: pywps


Defining processes
------------------

.. autoclass:: Process

.. autoclass:: Service

.. autoclass:: LiteralInput

.. autoclass:: ComplexInput

.. autoclass:: LiteralOutput

.. autoclass:: ComplexOutput

.. autoclass:: Format


Request and response objects
----------------------------

.. autoclass:: WPSRequest
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

.. autoclass:: WPSResponse

