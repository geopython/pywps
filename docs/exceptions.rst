.. _exceptions:

Exceptions
==========

.. module:: pywps.exceptions

PyWPS will throw exceptions based on the error occurred.
The exceptions will point out what is missing or what went wrong
as accurately as possible.

Here is the list of Exceptions and HTTP error codes associated with them:

.. autoclass:: NoApplicableCode

.. autoclass:: InvalidParameterValue

.. autoclass:: MissingParameterValue

.. autoclass:: FileSizeExceeded

.. autoclass:: VersionNegotiationFailed

.. autoclass:: OperationNotSupported

.. autoclass:: StorageNotSupported

.. autoclass:: NotEnoughStorage
