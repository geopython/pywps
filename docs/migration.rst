.. _migration:

Migrating from PyWPS 3.x to 4.x
===============================

The basic concept of PyWPS 3.x and 4.x remains the same: You deploy PyWPS once
and can have many instances with set of processes. It's good practice to store
processes in single files, although it's not required. 

.. note:: Unluckily, there is not automatic tool for conversion of processes nor
        compatibility module. If you would like to sponsor development of such
        module, please contact Project Steering Committee via PyWPS mailing list
        or members of PSC directly.

Configuration file
-------------------
Configuration file format remains the same (it's the one used by `configparser <https://docs.python.org/3.6/library/configparser.html>`_ module). The sections are shift a bit, so they
are more alike another GeoPython project - `pycsw <https://pycsw.org>`_.

See section :ref:`configuration`.

Single process definition
-------------------------
The main principle remains the same between 3.x and 4.x branches: You have to
define process class `class` and it's `__init__` method with inputs and outputs.

The former `execute()` method can now be any function and is assigned as
`handler` attribute.

`handler` function get's two arguments: `request` and `response`. In `requests`,
all input data are stored, `response` will have output data assinged.

The main difference between 3.x and 4.x is, *every input is list of inputs*. The
reason for such behaviour is, that you, as user of PyWPS define input defined by
type and identifier. When PyWPS process is turned to running job, there can be
usually *more then one input with same identifier* defined. Therefore instead of
calling::

    def execute(self):

            ...

            # 3.x inputs
            input = self.my_input.getValue()

you shall use first index of an input list::

    def handler(request, response):

            ... 

            # 4.X inputs
            input = request.inputs['my_input'][0].file

Inputs and outputs data manipulation
------------------------------------
Btw, PyWPS Inputs do now have `file`, `data`, `url` and `stream` attributes. They are
transparently converting one data-representation-type to another. You can read
input data from file-like object using `stream` or get directly the data into
variable with `input.data`. You can also save output data directly using
`output.data = { ..... }`.

See more in :ref:`process`

Deployment
==========
While PyWPS 3.x was usually deployed as CGI application, PyWPS 4.x is configured
as `WSGI` application. PyWPS 4.x is distributed without any processes or sample
deploy script. We provide such example in our `pywps-flask
<https://github.com/geopython/pywps-flask>`_ project.

.. note:: PYWPS_PROCESSES environment variable is gone, you have to assing
        processes to deploy script manually (or semi-automatically).

For deployment script, standard WSGI application as used by `flask
microframework <http://flask.pocoo.org/>`_ has to be defined, which get's
two parameters: list of processes and configuration files::

    from pywps.app.Service import Service
    from processes.buffer import Buffer

    processes = [Buffer()]

    application = Service(processes, ['wps.cfg'])

Those 4 lines of code do deploy PyWPS with Buffer process. This gives you more
flexible way, how to define processes, since you can pass new variables and
config values to each process class instance during it's definition.

Sample processes
================
For sample processes, please refer to `pywps-flask
<https://github.com/geopython/pywps-flask>`_ project on GITHub.

Needed steps summarization
==========================

#. Fix configuration file
#. Every processes needs new class and inputs and outputs definition
#. In `execute` method, you just need to review inputs and outputs data
   assignment, but the core of the method should remain the same.
#. Replace shell or python-based CGI script with Flask-based WSGI script
