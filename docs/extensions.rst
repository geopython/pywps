.. _extensions:

Extensions
==========

PyWPS has extensions to enhance its usability in special uses cases, for example
to run Web Processing Services at High Performance Compute (HPC) centers. These
extension are disabled by default. They need a modified configuration and have
additional software packages. Some extensions are:

* Using batch job schedulers (distributed resource management) at HPC compute
  centers.
* Using container solutions like `Docker <https://www.docker.com/>`_ in a cloud
  computing infrastructure.


PyWPS Scheduler Extension
-------------------------

By default PyWPS executes all processes on the same machine as the PyWPS service
is running on. Using the PyWPS scheduler extension it becomes possible to
delegate the execution of asynchronous processes to a scheduler system like
`Slurm <https://slurm.schedmd.com/>`_,
`Grid Engine <https://en.wikipedia.org/wiki/Univa_Grid_Engine>`_ and
`TORQUE <https://en.wikipedia.org/wiki/TORQUE>`_. By enabling this extension one
can handle the processing workload using an existing scheduler system commonly
found at High Performance Compute (HPC) centers.

.. note:: The PyWPS process implementations are not changed by using the
  scheduler extension.


To activate this extension you need to edit the ``pywps.cfg`` configuration file
and make the following changes::

  [processing]
  mode = scheduler

The scheduler extension uses the `DRMAA`_
library to talk to the different scheduler systems. Install the additional
Python dependencies using pip::

  $ pip install -r requirements-processing.txt  # drmaa

If you are using the `conda package manager <https://conda.io/docs/>`_ you can
install the dependencies with::

  $ conda install drmaa dill

.. warning:: In addition you need to install and configure the drmaa modules for
  your scheduler system on the machine PyWPS is running on. Follow the
  instructions given in the `DRMAA`_ documentation and by your scheduler system
  installation guide.

.. _DRMAA: https://github.com/pygridtools/drmaa-python
