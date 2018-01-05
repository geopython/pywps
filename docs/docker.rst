.. _docker:

Docker Container Extension
==========================

To isolate each process execution it is possible to enable docker extension.

.. note:: The PyWPS process implementations are not changed by using the
  scheduler extension.

First of all install Docker from `website <https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/>`_.

Clone ``pywps-demo``::

  $ git clone https://github.com/lazaa32/pywps-flask.git

Install demo requirements from ``requirement.txt``. It will download all required packages including
``pywps`` core package::

  $ cd pywps-flask
  $ pip install -r requirements.txt

``pywps`` package was downloaded to ``src`` directory. Let's set the ``PYTHONPATH`` so ``pywps-demo`` knows
where to find::

  $ EXPORT PYTHONPATH=$PYTHONPATH:$PWD/src/pywps-develop

If everything went OK, it should be now possible to run::

  $ python3 demo.py

However the demo still runs without Docker extension. First of all it is necessary to build an image from Dockerfile.
From the image all containers will be created::

  $ cd docker/isolation
  $ docker build -t container .

.. note:: The **-t** flag sets a name and optionally a tag in the **name:tag** format. The name of the image
   will be one of the parameter value in configuration file.
.. warning:: The image build can take up to several tens of minutes since some manual installation run on the
   background.

You can check the image was built by::

  $ docker images

To activate this extension you need to edit the ``pywps.cfg`` configuration file and make the following changes::

  [processing]
  mode=docker
  port_min=5050
  port_max=5070
  docker_img=container
  dckr_inp_dir=/pywps-flask/data
  dckr_out_dir=/pywps-flask/outputs

``mode`` must be set to ``docker``. ``port_min`` and ``port_max`` define the range of ports which can be
assigned to containers. ``docker_img`` must match to name of the image given by -t flag during the image build.

The docker extension is now enabled and every asynchronous request will be executed separately in a Docker
container.