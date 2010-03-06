.. _process:

PyWPS Process
*************

Processes directory
===================

PyWPS process is to be understand as
`Python module <http://docs.python.org/tutorial/modules.html>`_. Set of
PyWPS processes are stored in one directory `Python Package <http://docs.python.org/tutorial/modules.html#packages>`_ with :file:`__init__.py` file, containing the list of processes in `__all__` array.

Default location for processes
------------------------------
As already metioned, PyWPS processes directory is actualy Ptyhon
Package. PyWPS default location of processes is located in the
:file:`pywps/processes` directory, in the installation location of PyWPS.

Configuration via :envvar:`PYWPS_PROCESSES` environment variable
----------------------------------------------------------------
Usually, you will overwrite this with :envvar:`PYWPS_PROCESSES` environment
variable in the :ref:`configuration`. 

Configuration via configuration file
------------------------------------
Alternatively you can set the `processesPath` variable in the configuration file.

Logging
=======
PyWPS uses Python module :mod:`logging` for logging purposes. If there is
something, you need to log (activity, variable content for debug or
anything else), just import the module and use it::

    import logging
    ...

    logging.info("Just information message")
    logging.debug("Variable content: %s" % variable)
    logging.error("Error occured: %s" % e)

The logs are printed to standard error, or to file set in the configuration
file :ref:`configuration`. Log level is set with `logLevel` option, also in
thte configuration file.

.. toctree::
    :maxdepth: 1

    structure
    puts
    execute
