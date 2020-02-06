.. _configuration:

Configuration
=============

PyWPS is configured using a configuration file. The file uses the
`ConfigParser <https://wiki.python.org/moin/ConfigParserExamples>`_ format, with
interpolation initialised using `os.environ`.

.. versionadded:: 4.0.0
.. warning:: Compatibility with PyWPS 3.x: major changes have been made
  to the config file in order to allow for shared configurations with `PyCSW
  <https://pycsw.org/>`_ and other projects.

The configuration file has several sections:

    * `metadata:main` for the server metadata inputs
    * `server` for server configuration
    * `processing` for processing backend configuration
    * `logging` for logging configuration
    * `grass` for *optional* configuration to support `GRASS GIS
      <https://grass.osgeo.org>`_
    * `s3` for *optional* configuration to support AWS S3 storage

PyWPS ships with a sample configuration file (``default-sample.cfg``).
A similar file is also available in the `flask` service as
described in :ref:`flask` section.

Copy the file to ``default.cfg`` and edit the following:

[metadata:main]
---------------

The `[metadata:main]` section was designed according to the `PyCSW project
configuration file <https://docs.pycsw.org/en/latest/configuration.html>`_.

:identification_title:
    the title of the service
:identification_abstract:
    some descriptive text about the service
:identification_keywords:
    comma delimited list of keywords about the service
:identification_keywords_type:
    keyword type as per the `ISO 19115 MD_KeywordTypeCode codelist
    <http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode>`_).
    Accepted values are ``discipline``, ``temporal``, ``place``, ``theme``,
    ``stratum``
:identification_fees:
    fees associated with the service
:identification_accessconstraints:
    access constraints associated with the service
:provider_name:
    the name of the service provider
:provider_url:
    the URL of the service provider
:contact_name:
    the name of the provider contact
:contact_position:
    the position title of the provider contact
:contact_address:
    the address of the provider contact
:contact_city:
    the city of the provider contact
:contact_stateorprovince:
    the province or territory of the provider contact
:contact_postalcode:
    the postal code of the provider contact
:contact_country:
    the country of the provider contact
:contact_phone:
    the phone number of the provider contact
:contact_fax:
    the facsimile number of the provider contact
:contact_email:
    the email address of the provider contact
:contact_url:
    the URL to more information about the provider contact
:contact_hours:
    the hours of service to contact the provider
:contact_instructions:
    the how to contact the provider contact
:contact_role:
    the role of the provider contact as per the `ISO 19115 CI_RoleCode codelist
    <http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode>`_).
    Accepted values are ``author``, ``processor``, ``publisher``, ``custodian``,
    ``pointOfContact``, ``distributor``, ``user``, ``resourceProvider``,
    ``originator``, ``owner``, ``principalInvestigator``

.. _server-configuration:

[server]
--------

:url:
    the URL of the WPS service endpoint

:language:
    a comma-separated list of ISO 639-1 language and ISO 3166-1 alpha2 country 
    code of the service
    (e.g. ``en-CA``, ``fr-CA``, ``en-US``)

:encoding:
    the content type encoding (e.g. ``ISO-8859-1``, see
    https://docs.python.org/2/library/codecs.html#standard-encodings).  Default
    value is 'UTF-8'

:parallelprocesses:
    maximum number of parallel running processes - set this number carefully.
    The effective number of parallel running processes is limited by the number
    of cores  in the processor of the hosting machine. As well, speed and
    response time of hard drives impact ultimate processing performance. A
    reasonable number of parallel running processes is not higher than the
    number of processor cores.

:maxrequestsize:
    maximal request size. 0 for no limit

:maxprocesses:
    maximal number of requests being stored in queue, waiting till they can be
    processed (see ``parallelprocesses`` configuration option).

:workdir:
    a directory to store all temporary files (which should be always deleted,
    once the process is finished).

:outputpath:
    server path where to store output files.

:outputurl:
    corresponding URL

:allowedinputpaths:
     server paths which are allowed to be used by file URLs. A list of paths
     must be seperated by `:`.

     Example: `/var/lib/pywps/downloads:/var/lib/pywps/public`

     By default no input paths are allowed.

:cleantempdir:
    flag to enable removal of process temporary workdir after process has finished.

    Default = `true`.

.. note:: `outputpath` and `outputurl` must correspond. `outputpath` is the name
        of the resulting target directory, where all output data files are
        stored (with unique names). `outputurl` is the corresponding full URL,
        which is targeting to `outputpath` directory.

        Example: `outputpath=/var/www/wps/outputs` shall correspond with
        `outputurl=http://foo.bar/wps/outputs`

:storagetype:
    The type of storage to use when storing status and results. Possible values are: ``file``, ``s3``. Defaults to ``file``.

[processing]
------------

:mode:
    the mode/backend used for processing. Possible values are:
    `default`, `multiprocessing` and `scheduler`. `default` is the same as
    `multiprocessing` and is the default value ... all processes are executed
    using the Python multiprocessing module on the same machine as the PyWPS
    service. `scheduler` is used to enable the job scheduler extension and
    process execution is delegated to a configured scheduler system like Slurm
    and Grid Engine.

:path:
    path to the PyWPS `joblauncher` executable. This option is only used for
    the `scheduler` backend and is by default set automatically:
    `os.path.dirname(os.path.realpath(sys.argv[0]))`

[logging]
---------

:level:
    the logging level (see
    https://docs.python.org/3/library/logging.html#logging-levels)

:format:
    the format string used by the logging `:Formatter:` (see
    https://docs.python.org/3/library/logging.html#logging.Formatter).
    For example: ``%(asctime)s] [%(levelname)s] %(message)s``.

:file:
    the full file path to the log file for being able to see possible error
    messages.

:database:
    Connection string to database where the login about requests/responses is to be stored. We are using `SQLAlchemy <https://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls>`_
    please use the configuration string. The default is SQLite3 `:memory:` object, however this has `known issues <https://github.com/geopython/pywps/issues?utf8=%E2%9C%93&q=is%3Aissue+async+sqlite>`_ with async processing and should be avoided.


[grass]
-------

:gisbase:
  directory of the GRASS GIS instalation, refered as `GISBASE
  <https://grass.osgeo.org/grass73/manuals/variables.html>`_


[s3]
----

:bucket:
  Name of the bucket to store files in. e.g. ``my-wps-results``

:region:
  Region in which the bucket refered to above exists. e.g. ``us-east-1``

:public:
  Set this to ``true`` if public access to status and result files is desired. Defaults to ``false``.

:prefix:
  Prefix to prepend to all file paths written to the S3 bucket by PyWPS. e.g. ``wps/results``

:encrypt:
  Set this to ``true`` if encryption at rest is desired. Defaults to ``false``

-----------
Sample file
-----------
::

  [server]
  encoding=utf-8
  language=en-US
  url=http://localhost/wps
  maxoperations=30
  maxinputparamlength=1024
  maxsingleinputsize=
  maxrequestsize=3mb
  temp_path=/tmp/pywps/
  processes_path=
  outputurl=/data/
  outputpath=/tmp/outputs/
  workdir=
  allowedinputpaths=/tmp
  storagetype=file

  [metadata:main]
  identification_title=PyWPS Processing Service
  identification_abstract=PyWPS is an implementation of the Web Processing Service standard from the Open Geospatial Consortium. PyWPS is written in Python.
  identification_keywords=PyWPS,WPS,OGC,processing
  identification_keywords_type=theme
  identification_fees=NONE
  identification_accessconstraints=NONE
  provider_name=Organization Name
  provider_url=https://pywps.org/
  contact_name=Lastname, Firstname
  contact_position=Position Title
  contact_address=Mailing Address
  contact_city=City
  contact_stateorprovince=Administrative Area
  contact_postalcode=Zip or Postal Code
  contact_country=Country
  contact_phone=+xx-xxx-xxx-xxxx
  contact_fax=+xx-xxx-xxx-xxxx
  contact_email=Email Address
  contact_url=Contact URL
  contact_hours=Hours of Service
  contact_instructions=During hours of service.  Off on weekends.
  contact_role=pointOfContact

  [processing]
  mode=default

  [logging]
  level=INFO
  file=logs/pywps.log
  database=sqlite:///logs/pywps-logs.sqlite3
  format=%(asctime)s] [%(levelname)s] file=%(pathname)s line=%(lineno)s module=%(module)s function=%(funcName)s %(message)s

  [grass]
  gisbase=/usr/local/grass-7.3.svn/

  [s3]
  bucket=my-org-wps
  region=us-east-1
  prefix=appname/coolapp/
  public=true
  encrypt=false

