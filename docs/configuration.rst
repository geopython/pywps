=============
Configuration
=============

PyWPS is configured using a configuration file. The file uses
`ConfigParser <https://wiki.python.org/moin/ConfigParserExamples>`_ format. The
file can be stored anywhere or can be set using `PYWPS_CFG` environment
variable.

.. versionadded:: 4.0.0
.. warning:: Compatibility with PyWPS 3.x: major changes have been made
  to the config file in order to allow for shared configurations with pycsw
  and other projects.

The configuration file has 2 sections.

PyWPS ships with a sample configuration (``default-sample.cfg``).  Copy the file to ``default.cfg`` and edit the following: 

**[server]**

- **url**: the URL of the resulting service
- **language**: the ISO 639-1 language and ISO 3166-1 alpha2 country code of the service (e.g. ``en-CA``, ``fr-CA``, ``en-US``)
- **encoding**: the content type encoding (e.g. ``ISO-8859-1``, see https://docs.python.org/2/library/codecs.html#standard-encodings).  Default value is 'UTF-8'
- **loglevel**: the logging level (see http://docs.python.org/library/logging.html#logging-levels)
- **logfile**: the full file path to the logfile
- **maxoperations**: maximum number of parallel running operations
- **logdatabase**: SQLite3 file, where the login about requests/responses will be provided. You can set this to `":memory:"` for having the database in memory
- **maxrequestsize**: maximal request size. 0 for no limit
- **workdir**: temporary directory for all temporary files (which should be always deleted, once the process is finished
- **outputpath**: server path for storing output files
- **outputurl**: corresponding URL

.. note:: `outputpath` and `outputurl` must corespond 

**[metadata:main]**

- **identification_title**: the title of the service
- **identification_abstract**: some descriptive text about the service
- **identification_keywords**: comma delimited list of keywords about the service
- **identification_keywords_type**: keyword type as per the `ISO 19115 MD_KeywordTypeCode codelist <http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode>`_).  Accepted values are ``discipline``, ``temporal``, ``place``, ``theme``, ``stratum``
- **identification_fees**: fees associated with the service
- **identification_accessconstraints**: access constraints associated with the service
- **provider_name**: the name of the service provider
- **provider_url**: the URL of the service provider
- **contact_name**: the name of the provider contact
- **contact_position**: the position title of the provider contact
- **contact_address**: the address of the provider contact
- **contact_city**: the city of the provider contact
- **contact_stateorprovince**: the province or territory of the provider contact
- **contact_postalcode**: the postal code of the provider contact
- **contact_country**: the country of the provider contact
- **contact_phone**: the phone number of the provider contact
- **contact_fax**: the facsimile number of the provider contact
- **contact_email**: the email address of the provider contact
- **contact_url**: the URL to more information about the provider contact
- **contact_hours**: the hours of service to contact the provider
- **contact_instructions**: the how to contact the provider contact
- **contact_role**: the role of the provider contact as per the `ISO 19115 CI_RoleCode codelist <http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode>`_).  Accepted values are ``author``, ``processor``, ``publisher``, ``custodian``, ``pointOfContact``, ``distributor``, ``user``, ``resourceProvider``, ``originator``, ``owner``, ``principalInvestigator``

**[grass]**
- **gisbase**: directory of GRASS GIS instalation, refered as `GISBASE <https://grass.osgeo.org/grass73/manuals/variables.html>`_

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
  logfile=
  loglevel=INFO
  logdatabase=
  workdir=
  
  [metadata:main]
  identification_title=PyWPS Processing Service
  identification_abstract=PyWPS is an implementation of the Web Processing Service standard from the Open Geospatial Consortium. PyWPS is written in Python.
  identification_keywords=PyWPS,WPS,OGC,processing
  identification_keywords_type=theme
  identification_fees=NONE
  identification_accessconstraints=NONE
  provider_name=Organization Name
  provider_url=http://pywps.org/
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

  [grass]
  gisbase=/usr/local/grass-7.3.svn/
