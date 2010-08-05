.. _configuration :

*************
Configuration
*************

.. note:: Before you start to tune your PyWPS installation, you should get your copy of
    OpenGIS(R) Web Processing Service document (OGC  05-007r7) version
    1.0.0 http://www.opengeospatial.org/standards/wps or later.

Setuping the PyWPS instance
===========================
PyWPS can be installed once on your server, but it be configured for many
WPS servers (instances). Each WPS server needs set of processes (stored in
one directory) and configuration file.
Processes are stored together as python programs in one directory. To setup
this, you have to:

1 - create processes directory -- directory, where you store all
    processes for particular PyWPS instance::

    $ mkdir -p /usr/local/wps/processes

2 - copy template of the configuration file to some location, and
    configure you PyWPS installation (see below)::

    $ cp pywps-VERSION/pywps/default.cfg /usr/local/wps/pywps.cfg
    $ $EDITOR /usr/locap/wps/pywps.cfg

3 - create any process(es) in the processes directory. You can start with
    the example processes, stored in `pywps-VERSION/examples/processes`
    directory. See :ref:`how-to-write-custom-process` for how to write
    custom processes.::

    $ cp pywps-VERSION/examples/ultimatequestionprocess.py /usr/local/wps/processes/

6 - Every process, you have in the processes directory, needs to be
    registered in the `__init__.py` file. The file has to contain at
    least::

        __all__ = ["ultimatequestionprocess"]

    Where __all___ represents list of processes (file names) within the
    processes directory.

Accepted environment variables
------------------------------
Following environemnt variables are accepted by PyWPS instance:

    PYWPS_CFG 
        Configuration file location
    PYWPS_PROCESSES
        Directory, where the processes are stored
    PYWPS_TEMPLATES
        Templates directory (structure should be similar to
        file:`pywps/Templates`)

Setuping the Web Server
-----------------------
PyWPS can run as `CGI <http://www.w3.org/CGI/>`_ application or in
`mod_python <http://www.modpython.org/>`_ mode. CGI is easier to setup,
where mod_python is less demanding on server resources, since after first
run, PyWPS and Python itself are loaded into memory.

PyWPS as CGI
............
It is simplier method, without any additional server configuration.

To configure PyWPS via CGI, copy the PyWPS cgi wrapper script to 
your cgi-bin directory and edit the variables, which are set there::

    $ cp pywps/resources/pywps.cgi /usr/lib/cgi-bin
    $ $EDITOR /usr/lib/cgi-bin/pywps.cgi

.. note:: Windows users, you have to script some similar script as .bat
    file or in python. This example is written as SHELL script.

.. note:: This script is to be used with combination of Apache only. If you
    want to run `wps.py` from command line, use not this script, but the
    program itself.

The file can look like this::

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

You can also configure this environment variables using standard Apache
server configuration file (see :ref:`mod_python`) for example.
    
.. _mod_python :

PyWPS in mod_python
...................

It is in general better, to run PyWPS in mod_python, because all necessary
libraries are pre-loaded into memory and so the response times should be
faster in some cases. 

    1 - Install necessary packages, on debian, it is `libapache2-mod-python`
    2 - Congfigure Apache HTTPD server (see `Mod Python documentation <http://www.modpython.org/live/mod_python-2.7.8/doc-html/inst-apacheconfig.html>`_).


1 - Create python directory, it should be outside htdocs directory,
    however, (yes, you can) create in in htdocs directory::

    $ mkdir /var/www/wps/

2 - Add this to your site configuration file::

            <Directory /var/www/wps>
                SetEnv PYWPS_PROCESSES /usr/local/wps/processes
                SetEnv PYWPS_CFG /usr/local/wps/pywps.cfg
                SetHandler python-program
                PythonHandler pywps
                PythonDebug On
                PythonPath "sys.path+['/usr/local/pywps-VERSION/']"
                PythonAutoReload On
            </Directory>

or you can copy :file:`resources/.htaccess` file to `/var/www/wps` --
depends, what you prefer or the system administrator allows you to do.

3 - Copy :file:`resources/pywps.py` to :file:`/var/www/wps`

PyWPS configuration files
=========================
Configuration file for PyWPS can be located on several places. There are
global and local PyWPS configuration files. The locals do rewrite values
stored in global files.

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

    .. note:: Never rewrite or remove this file. Use it onlyas template for
        your custom configuration files.

Local PyWPS configuration file
------------------------------
The configuration file is used for the particular PyWPS instance only. It
is the file, stored in :envvar:`PYWPS_CFG` environment variable. This can
be set either via web server configuration or with help of any warper
script (see :file:`resources/pywps.cgi` for example).

Make a copy of :file:`pywps/default.cfg` to
:file:`/usr/local/wps/pywps.cfg` and customize the file with help of
following documentation.

Configuration of PyWPS instance
===============================
Several sections are in the configuration file.  The sections are then
containing `key value` pairs of configuration options. See example at the
end of this section. If you would not fill some of tis options, they will
be taken from default configuration file.

WPS
---
[wps] section contains general WPS instance settings, which are:

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
provider section contains informations about you, your institution and so on

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
        
    country
        
    electronicMailAddress 
        E-mail address
    providerSite 
        Web site or your institution

    phoneVoice
        
    phoneFacsimile
        
    administrativeArea

    hoursofservice
        When you are at work
    contactinstructions
        For example secret password, to pass through door-man to you.

Server
------
server contains server settings, constrains, safety configuration and so on.

    maxoperations 
        Maximal number of parallel running processes. If set to 0, then there is no limit.
    maxinputparamlength 
        Maximal length of string input parameter (number of characters). 
    maxfilesize 
        Maximal input file size (raster or vector). The size can be determined as follows: 1GB, 5MB, 3kB, 1000b.
    tempPath 
        Directory for temporary files, I use :file:`/tmp/pywps`. PyWPS will
        create temporary directories in this dir, and after the calculation
        is performed, they *should* be deleted again.
    outputPath 
        Path. where output files are stored, from the server point of view.
        This should point to `outputUrl` parameter (described below). For
        example http://foo/bar/wpsputputs
    outputUrl 
        Url where the outputs are stored, from the client point of view. On
        Debian, it would be for example :file:`/var/www/wpsoutputs`
    debug 
        true/false - makes the logs for verbose
        
        .. note:: This option is not used so wildly, as it should maybe be. 

        .. note:: Deprecated since 3.2. Use logLevel instead

    processesPath 
        path to your processes. Default is pywps/processes.

        .. note::
            You can set also :envvar:`PYWPS_PROCESSES` environment
            variable with same result, as described earlier on this page.

    logFile
        (since 3.0.1) File, where all logs from PyWPS are going to. If not
        set, default error.log from Web Server configuration is used.
        Sometimes, this can cause problem for the asynchronous calls.

    logLevel
        (since 3.2) one of DEBUG, INFO, WARNING, ERROR and CRITICAL,
        default is INFO

GRASS
-----
GRASS GIS settings, if you want ot use it

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
