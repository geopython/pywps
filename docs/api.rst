===
API
===

.. module:: pywps.app


Defining processes
------------------

.. autoclass:: Process

   .. attribute:: handler

      A callable that gets invoked for each incoming request. It should
      accept a single :class:`~WPSRequest` argument and return a
      :class:`~WPSResponse` object.

   .. attribute:: identifier

      Name of this process.

   .. attribute:: inputs

      List of inputs accepted by this process. They should be
      :class:`~LiteralInput` and :class:`~ComplexInput` objects.

.. autoclass:: Service
   :members:

   .. attribute:: processes

      A list of :class:`~Process` objects that are provided by this
      service.

.. autoclass:: LiteralInput

   .. attribute:: identifier

      The name of this input.

   .. attribute:: data_type

      Type of literal input (e.g. `string`, `float`...).

.. autoclass:: ComplexInput

   .. attribute:: identifier

      The name of this input.

   .. attribute:: formats

      Allowed formats for this input. Should be a list of one or more
      :class:`~Format` objects.

.. autoclass:: Format

   .. attribute:: mime_type

      MIME type allowed for a complex input.


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
   :members:

   .. attribute:: outputs

      A dictionary of output values that will be returned to the client.
      The values can be strings or :class:`~FileReference` objects.

.. autoclass:: FileReference

   .. attribute:: url

      URL where the file can be downloaded by the client.

   .. attribute:: mime_type

      MIME type of the file.
