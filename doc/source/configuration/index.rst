.. _configuration :

*************
Configuration
*************

.. note:: Before you start to tune your PyWPS installation, you can download 
    OpenGIS(R) Web Processing Service document (OGC  05-007r7) version
    1.0.0 http://www.opengeospatial.org/standards/wps or later, for reference.

Setting up the PyWPS instance
=============================
PyWPS can be installed once on your server, but it be configured for many
WPS servers (instances). Each WPS server needs a set of processes (stored in
one directory) and a configuration file.
Processes are stored together as python programs in one directory as follows:

1 - create ``processes`` directory -- directory, where you store all
    processes for particular PyWPS instance::

    $ mkdir -p /usr/local/wps/processes

2 - copy template of the configuration file to some location, and
    configure your PyWPS installation (see below)::

    $ cp pywps-VERSION/pywps/default.cfg /usr/local/wps/pywps.cfg
    $ $EDITOR /usr/locap/wps/pywps.cfg

3 - create any process(es) in the ``processes`` directory. You can start with
    the example processes, stored in `pywps-VERSION/examples/processes`
    directory. See :ref:`how-to-write-custom-process` for how to write
    custom processes.::

    $ cp pywps-VERSION/examples/ultimatequestionprocess.py /usr/local/wps/processes/

6 - Each process in the ``processes`` directory must be
    registered in the `__init__.py` file. The file has to contain at
    least::

        __all__ = ["ultimatequestionprocess"]

    Where ``__all__`` represents list of processes (file names) within the
    ``processes`` directory.

Accepted environment variables
------------------------------
The following environment variables are accepted by a PyWPS instance:

    PYWPS_CFG 
        Configuration file location
    PYWPS_PROCESSES
        Directory, where the processes are stored
    PYWPS_TEMPLATES
        Templates directory (structure should be similar to
        file:`pywps/Templates`)

Setting up the Web Server
-------------------------
PyWPS can run as `CGI <http://www.w3.org/CGI/>`_ application or in
`mod_python <http://www.modpython.org/>`_ mode. CGI is easier to setup,
where mod_python is less demanding on server resources, since after the first
run, PyWPS and Python itself are loaded into memory.

PyWPS as CGI
............
CGI configuration is a simple appraoch, without any additional server configuration.

To configure PyWPS via CGI, copy the PyWPS CGI wrapper script to 
your ``cgi-bin`` directory and edit the variables::

    $ cp pywps/resources/pywps.cgi /usr/lib/cgi-bin
    $ $EDITOR /usr/lib/cgi-bin/pywps.cgi

.. note:: Windows users must create a either a .bat file or Python wrapper.
    This example is written as UNIX shell script.

.. note:: This script is to be used only via HTTP (with e.g. Apache). If you
    want to run PyWPS from the command line, use `wps.py` directly.

Below is a sample wrapper::

    #!/bin/sh

    # Author: Jachym Cepicky
    # Purpose: CGI script for wrapping PyWPS script
    # Licence: GNU/GPL
    # Usage: Put this script to your web server cgi-bin directory, e.g.
    # /usr/lib/cgi-bin/ and make it executable (chmod 755 pywps.cgi)

    # NOTE: tested on linux/apache

    export PYWPS_CFG=/usr/local/wps/pywps.cfg
    export PYWPS_PROCESSES=/usr/local/wps/processes/

    /usr/local/pywps-VERSION/cgiwps.py

You can also configure HTTP environment variables using standard Apache
server configuration file (see :ref:`mod_python`) for example.
    
.. _mod_python :

PyWPS in mod_python
...................

Overall, PyWPS has better performance via mod_python.  All necessary
libraries are pre-loaded into memory and response times should be
faster in some cases. 

    1 - Install necessary packages, on debian, it is `libapache2-mod-python`
    2 - Configure Apache HTTP server (see `Mod Python documentation <http://www.modpython.org/live/mod_python-2.7.8/doc-html/inst-apacheconfig.html>`_).


1 - Create python directory (preferably outside ``htdocs`` directory)::

    $ mkdir /var/www/wps/

2 - Add this to your HTTP configuration file::

            <Directory /var/www/wps>
                SetEnv PYWPS_PROCESSES /usr/local/wps/processes
                SetEnv PYWPS_CFG /usr/local/wps/pywps.cfg
                SetHandler python-program
                PythonHandler pywps
                PythonDebug On
                PythonPath "sys.path+['/usr/local/pywps-VERSION/']"
                PythonAutoReload On
            </Directory>

or you can copy :file:`resources/.htaccess` to `/var/www/wps` --
depending on what level of access you are provided by your
system administrator.

3 - Copy :file:`resources/pywps.py` to :file:`/var/www/wps`

PyWPS configuration files
=========================
Configuration file for PyWPS can be located in several places. There are
global and local PyWPS configuration files. Local configurations override
global configurations.

Global PyWPS configuration files
--------------------------------
1. File :file:`/etc/pywps.cfg` (on Linux/Unix)
2. File :file:`/usr/local/pywps-VERSION/etc/pywps.cfg`, which means the
   file :file:`pywps.cfg` in directory :file:`etc`, located in PyWPS
   install location.

And one special file:

    File :file:`/usr/local/pywps-VERSION/pywps/default.cfg`, which means the
    file :file:`default.cfg` in directory :file:`pywps`, located in PyWPS
    install location. This is the default configuration file.

    .. note:: Never rewrite or remove this file. Use it only as template for
        your custom configuration files.

Local PyWPS configuration file
------------------------------
The local configuration file is used for the particular PyWPS instance only. It
is the file, stored in :envvar:`PYWPS_CFG` environment variable. This can
be set either via web server configuration or with any wrapper
script (see :file:`resources/pywps.cgi` for example).

Make a copy of :file:`pywps/default.cfg` to
:file:`/usr/local/wps/pywps.cfg` and customize the file as per below.

Configuration of PyWPS instance
===============================
Several sections are in the configuration file.  The sections
contain `key value` pairs of configuration options (see the example at the
end of this section). If you do not set these options, they will
be taken from the default configuration file.

WPS
---
The [wps] section contains general WPS instance settings, which are:

    encoding 
        Language encoding (utf-8, iso-8859-2, windows-1250, \dots)
    title 
        Server title 
    version 
        WPS version (1.0.0)
    abstract 
        Server abstract
    fees 
        Possible fees
    constraints 
        Possible constraints
    serveraddress 
        WPS script address: http://foo/bar/pywps.py or http://foo/bar/cgi-bin/pywps.cgi
    keywords 
        Comma-separated list of keywords realted to this server instance
    lang 
        Comma-separated list of supported server languages. Default is
        'eng'.

Provider
--------
The [provider] section contains information about you, your organization and so on:

    providerName 
        Name of your company
    individualName 
        Your name
    positionName
        At which position you are working
    role 
        What your role is
    deliveryPoint 
        Street
    city
        City
    postalCode
        Postal code or Zip code        
    country
        Country name 
    electronicMailAddress 
        E-mail address
    providerSite 
        Web site of your organization
    phoneVoice
        Telephone number
    phoneFacsimile
        Fax number
    administrativeArea
        State, province, territory or administrative area
    hoursofservice
        Hours of service to contact the provider
    contactinstructions
        Instructions on how to contact the provider

Server
------
The [server] section contains server settings, constraints, safety configuration and so on:

    maxoperations 
        Maximum number of parallel running processes. If set to 0, then there is no limit.
    maxinputparamlength 
        Maximum length of string input parameter (number of characters). 
    maxfilesize 
        Maximum input file size (raster or vector). The size can be determined as follows: 1GB, 5MB, 3kB, 1000b.
    tempPath 
        Directory for temporary files (e.g. :file:`/tmp/pywps`). PyWPS will
        create temporary directories in this directory, and after the calculation
        is performed, they *should* be deleted again.
    outputPath 
        Path where output files are stored on the server.
        This should point to the `outputUrl` parameter (described below). For
        example http://foo/bar/wpsputputs. If outputPath starts with ftp:// it's assumed that FTP support shall be used.
    outputUrl 
        Url where the outputs are stored for client access. On
        Debian, it would be for example :file:`/var/www/wpsoutputs`
    ftplogin
    	FTP user login, if empty, anonymous login is used. 
    	
    	.. note:: FTP support is activated by ftp:// in outputPath
    
    ftppasswd
    	FTP user password
    ftpport
    	Default FTP port 21 is used if variable not defined.
    
    debug 
        true/false - makes the logs for verbose
        
        .. note:: This option is not used so wildly, as it should maybe be. 

        .. note:: Deprecated since 3.2. Use logLevel instead

    processesPath 
        path to your processes. Default is pywps/processes.

        .. note::
            You can also set the :envvar:`PYWPS_PROCESSES` environment
            variable with the same result, as described earlier on this page.

    logFile
        (since 3.0.1) File where all PyWPS logs go to. If not
        set, default error.log from Web Server configuration is used.
        Sometimes, this can cause problem for the asynchronous calls.

    logLevel
        (since 3.2) one of DEBUG, INFO, WARNING, ERROR and CRITICAL,
        default is INFO

GRASS
-----
The [grass] section is specifically for GRASS GIS settings (optional):

    path 
        :envvar:`PATH` environment variable, e.g. :file:`/usr/lib/grass/bin:/usr/lib/grass/scripts`
    addonPath 
        :envvar:`GRASS_ADDONS` environment variable
    version 
        GRASS version
    gui 
        Should be "text"
    gisbase 
        Path to GRASS :envvar:`GIS_BASE` directory (:file:`/usr/lib/grass`)
    ldLibraryPath 
        Path of GRASS Libs (:file:`/usr/lib/grass/lib`)
    gisdbase 
        Full path to GRASS database directory, where *Locations* are stored (:file:`/home/foo/grassdata`) 

        .. note::You do not have to setup
            this variable in the configuration file globaly. You can use
            `grassLocation` attribute while calling the
            `__init__` method of Process class, while process
            initialization. See section :role:`Processesprocesses for more details.

Configuration file example
==========================
::

    [wps]
    encoding=utf-8
    title=PyWPS Server
    version=1.0.0
    abstract=See http://pywps.wald.intevation.org and http://www.opengeospatial.org/standards/wps
    fees=None
    constraints=none
    serveraddress=http://localhost/cgi-bin/wps
    keywords=GRASS,GIS,WPS
    lang=eng

    [provider]
    providerName=Your Company Name
    individualName=Your Name
    positionName=Your Position
    role=Your role
    deliveryPoint=Street
    city=City
    postalCode=000 00
    country=eu
    electronicMailAddress=login@server.org
    providerSite=http://foo.bar
    phoneVoice=False
    phoneFacsimile=False
    administrativeArea=False

    [server]
    maxoperations=3
    maxinputparamlength=1024
    maxfilesize=3mb
    tempPath=/tmp
    processesPath=
    outputUrl=http://localhost/wps/wpsoutputs
    outputPath=/var/www/wps/wpsoutputs
    debug=true
    logFile=/var/log/pywps.log

    [grass]
    path=/usr/lib/grass/bin/:/usr/lib/grass/scripts/
    addonPath=
    version=6.2.1
    gui=text
    gisbase=/usr/lib/grass/
    ldLibraryPath=/usr/lib/grass/lib
    gisdbase=/home/foo/datagrass



Notes for Windows users
=======================
Windows users do have to adjust their paths to what is standard on this
platform. E.g. instead of using ":" as delemiter ";" is supposed to be used.
Also usage of slash "/" and backslash "\\" can be tricky.

Generally speaking, it's good to start by installing GRASS (if needed) and all
the required geospatial packages using `OSGeo4W tool <http://trac.osgeo.org/osgeo4w/>`_.

Having GRASS and PyWPS is possible and was successfuly tested. You have to
adjust especially PATH variable. Example of relevant configuration parts
follows: ::

    [server]
    maxoperations=30
    maxinputparamlength=1024
    maxfilesize=10mb
    tempPath=c:\\\\tmp
    processesPath=
    outputUrl=http://localhost/tmp/wpsoutputs
    outputPath=c:\OSGeo4W\apache\htdocs\tmp\wpsoutputs\
    debug=true # deprecated since 3.2, use logLevel instead
    logFile=
    logLevel=INFO

    [grass]
    path=c:\\\\osgeo4w/apps/grass/grass-7.0.0/lib;c:\\\\osgeo4w/apps/grass/grass-7.0.0/bin;c:\\\\c/Users/jachym/AppData/Roaming/GRASS7/addons/bin;c:\\\\usr/bin;c:\\\\osgeo4w/bin;c:\\\\c/Windows/system32;c:\\\\c/Windows;c:\\\\c/Windows/WBem;c:\\\\usr/bin;c:\\\\osgeo4w/apps/Python27/Scripts
    addonPath=
    version=7.0.0
    gui=text
    gisbase=c:\\\\OSGeo4W\\\\apps\\\\grass\\\\grass-7.0.0
    ldLibraryPath=c:\OSGeo4W\apps\grass\grass-7.0.0\lib
    gisdbase=c:\Users\jachym\src\vugtk\grassdata\
    home=c:\Users\jachym

FOr the configuration of Apache web server, you can directly use `wps.py` binary
from the root of PyWPS source code and use it. Example of relevant httpd.conf
file follows (it can of course be used on Unix as well)::

    
    # wps.py was copied from pywps-source/wps.py
    Alias /wps C:\OSGeo4W/bin/wps.py
    <Location /wps
            SetHandler cgi-script
            Options ExecCGI
            SetEnv PYWPS_CFG C:\path/to/your/configuration/pywps.cfg
            SetEnv PYWPS_PROCESSES C:\path/to/your/processes
    </Location>
