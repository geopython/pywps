=============
Configuration
=============

PyWPS is configured busing configuration file. The file uses
`ConfigParser <https://wiki.python.org/moin/ConfigParserExamples>`_ format. The
file can be stored anywhere or can be set using `PYWPS_CFG` environment
variable.

.. note:: Compatibility with PyWPS 3.x: minor changes are just in the `server`
  section. Rest of the configuration file should work as is.

The configuration file has 3 sections: 

**wps** 
    The `wps` section is related to the standard. Some necessary
    attributes are needed, namely:

    **title**
        title of the WPS service
    **abstract**
        abstract of the server
    **fees**
        usually set to `None`
    **contactraints**
        set to `None` as well
    **serveraddress**
        full address to WPS endpoint, like `http://localhost/wps`
    **serverport**
        port, usually set to 80 or just omitted
    **keywords**
        list of keywords of the service

**provider**
    The `provider` section is related to service provider details:

    **providerName**
				name of the institution hosting WPS service
    **individualName**
				your name
    **positionName**
				your position
    **role**
				your role
    **deliveryPoint**
				street, address
    **city**
				city
    **postalCode**
				postal code
    **country**
				country
    **electronicMailAddress**
				e-mail
    **providerSite**
				URL of your homepage
    **phoneVoice**
				phone number
    **phoneFacsimile**
				fax
    **administrativeArea**
			  ...	
    **hoursofservice**
				hours of service
    **contactinstructions**
				any detailed instructions

**server**
    the `server` section is related to instance of the WPS server

    **maxparaleloperations**
				maximum number of parallel running operations
    **logdatabase**
				sqlite3 file, where the login about requests/responses will be provided. You can set this to `":memory:"` for having the database in memory
    **maxrequestsize**
				maximal request size. 0 for no limit
    **workdir**
				temporary directory for all temporary files (which should be always deleted, once the process is finished
    **outputPath**
				server path for storing output files
    **outputUrl**
				corresponding URL
    **logfile**
				alternative file name to write all outputs to
    **loglevel**
				log level according to `logging module <https://docs.python.org/3/library/logging.html#logging-levels>`_ 

    .. note:: `outputPath` and `outputUrl` must corespond 

-----------
Sample file
-----------
::

  [wps]
  title=PyWPS 4 Server
  abstract=See https://github.com/jachym/pywps-4 and http://www.opengeospatial.org/standards/wps
  fees=NONE
  constraints=NONE
  serveraddress=http://localhost:5000/wps
  serverport=5000
  keywords=GRASS,GIS,WPS
  lang=en-US

  [provider]
  providerName=Organisation
  individualName=My Name
  positionName=Intern
  role=Developer
  deliveryPoint=Street
  city=Belval
  postalCode=000 00
  country=LU
  electronicMailAddress=login@server.org
  providerSite=http://foo.bar
  phoneVoice=False
  phoneFacsimile=False
  administrativeArea=False
  hoursofservice=00:00-24:00
  contactinstructions=NONE

  [server]
  maxoperations=30
  maxrequestsize=3mb
  workdir=/tmp/pywps/
  outputUrl=/data/
  outputPath=/tmp/outputs/
  logdatabase=/var/www/wps/wpsserver.db
