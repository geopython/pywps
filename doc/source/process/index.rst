.. _process:

PyWPS Process
*************

Processes directory
===================

A PyWPS process can be thought of as a
`Python module <http://docs.python.org/tutorial/modules.html>`_.  All
PyWPS processes are stored in one directory `Python Package <http://docs.python.org/tutorial/modules.html#packages>`_.  The :file:`__init__.py` file
must contain the list of processes in `__all__` array.

Default location for processes
------------------------------
The default location of PyWPS processes is located in the
:file:`pywps/processes` directory, in the installation location of PyWPS.

Configuration via :envvar:`PYWPS_PROCESSES` environment variable
----------------------------------------------------------------
Usually, you will overwrite this with the :envvar:`PYWPS_PROCESSES` environment
variable in the :ref:`configuration`. 

Configuration via configuration file
------------------------------------
Alternatively you can set the `processesPath` variable in the configuration file.

Logging
=======
PyWPS uses Python module :mod:`logging` for logging purposes. If there is
something you need to log (activity, variable content for debug or
anything else), just import the module and use accordingly::

    import logging
    ...

    logging.info("Just information message")
    logging.debug("Variable content: %s" % variable)
    logging.error("Error occured: %s" % e)

The logs are printed to standard error, or to a file set in the configuration
file :ref:`configuration`. Log level is set with `logLevel` option, also in
the configuration file.

.. toctree::
    :maxdepth: 1

    structure
    puts
    execute
