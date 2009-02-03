.. _configuration:
*************
Configuration
*************
    
Before you start to tune your PyWPS installation, you should get your copy of
OpenGIS(R) Web Processing Service document (OGC  05-007r7) version
1.0.0 http://www.opengeospatial.org/standards/wps or later.
    
.. note::
    Note, that the configuration option are **CASE SENSITIVE**
    
Pywps configuration takes place in :file:`pywps.cfg` file located in
:file:`/etc/pywps.cfg` or :file:`pywps/etc/pywps.cfg`. Path to the
configuration file can be also set by the :envvar:`PYWPS_CFG` environment
variable (see :role:`Customising PyWPS Installation`), see
:ref:`Wrapper script <wrapper-script>` for example usage.

Default configuration file is located in :file:`pywps/default.cfg`, you
can always make a copy of this file and start the configuration from
scratch.

.. note::
    Never make changes to  :file:`default.cfg` file.
    
Several sections are in the file. 

[wps] 
    contains general WPS settings, which are:

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
        WPS script address: http://foo/bar/wps.py
    keywords 
        Comma-separated list of keywords
    lang 
        Default language (eng)

[provider]
    contains informations about you

    providerName 
        Name of your company
    individualName 
        Your name
    positionName
        
    role 
        
    deliveryPoint 
        Street
    city
        
    postalCode
        
    country
        
    electronicMailAddress 
        foo@bar
    providerSite 
        http://foo.bar
    phoneVoice
        
    phoneFacsimile
        
    administrativeArea

[server]
    contains server settings

    maxoperations 
        Maximal number of parallel running processes. If set to 0, then there is no limit.
    maxinputparamlength 
        Maximal length of string input parameter (number of characters)
    maxfilesize 
        Maximal input file size (raster or vector). The size can be determined as follows: 1GB, 5MB, 3kB, 1000b.
    tempPath 
        Directory for temporary files (mostly temporary GRASS locations).
    outputUrl 
        Url where the outputs are stored.
    outputPath 
        Path. where output files are stored.
    debug 
        true/false - makes the logs for verbose
    processesPath 
        path to your processes. Default is pywps/processes.

        .. note::
            You can set also \texttt{PYWPS\_PROCESSES} environment
            variable with same result (section \ref{environment_variables}).

    logFile
        (since 3.0.1) File, where all logs from PyWPS are going to. If not
        set, default error.log from Web Server configuration is used.
        Somethimes, this can cause problem for the asynchronous calls.

[grass] 
    GRASS GIS settings

    path 
        $PATH variable, e.g. /usr/lib/grass/bin
    addonPath 
        $GRASS\_ADDONS variable
    version 
        GRASS version
    gui 
        Should be "text"
    gisbase 
        Path to GRASS GIS\_BASE directory (/usr/lib/grass)
    ldLibraryPath 
        Path of GRASS Libs (/usr/lib/grass/lib)
    gisdbase 
        Full path to location directory (/home/foo/grassdata) 

        .. note::
            You do not have to setup
            this variable in the configuration file globaly. You can use
            `grassLocation` attribute while calling the
            `__init__` method of Process class, while process
            initialization. See section :role:`Processesprocesses for more details.

File example follows::

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

===============================
Configuration of the Web Server
===============================
-------
Symlink
-------
If you did not installed PyWPS to :file:`cgi-bin` directory of your
server, you can create the symlink in :file:`cgi-bin` to :file:`wps.py`::

    ln -s /usr/bin/wps.py /usr/lib/cgi-bin/wps.py

In this case, options *+ExecCGI +FollowSymLinks* must be enabled for
:file:`cgi-bin` directory in the web server configuration file. Example::

    # /etc/apache2/sites-enabled/000-default
    # ...
            ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
            <Directory "/usr/lib/cgi-bin">
                    AllowOverride None
                    Options +ExecCGI -MultiViews +FollowSymLinks
                    Order allow,deny
                    Allow from all
            </Directory>
    # ...
    
*******
Testing
*******
For test, just run wps.py in the shell. The WPS options can be written as
parameter::
    
    $ wps.py "service=wps&request=getcapabilities"

    INIT DONE
    LOADING PRECOMPILED
    TEMPLATE: UPTODATE
    PRECOMPILED: UPTODATE
    Content-type: text/xml

    <?xml version="1.0" encoding="utf-8"?>
    <wps:Capabilities service="WPS" version="1.0.0" xml:lang="eng,ger"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        xmlns:wps="http://www.opengis.net/wps/1.0.0"
        xmlns:ows="http://www.opengis.net/ows/1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance
        xsi:schemaLocation="http://www.opengis.net/wps/1.0.0
        http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd"
        updateSequence="1">
            <ows:ServiceIdentification>
                    <ows:Title>PyWPS Development Server</ows:Title>
        ...
    </wps:Capabilities>

If you got something like this, (Capabilities response), everything looks
fine.
     
If you got some other message, like e.g.::
     
    Traceback (most recent call last):
    File "/usr/bin/wps.py", line 221, in <module>
        wps = WPS()
    File "/usr/bin/wps.py", line 140, in __init__
        self.performRequest()
    File "/usr/bin/wps.py", line 188, in performRequest
        from pywps.WPS.GetCapabilities import GetCapabilities
    File "/usr/lib/python2.5/site-packages/pywps/WPS/GetCapabilities.py", line 26, in <module>
        from Response import Response
    File "/usr/lib/python2.5/site-packages/pywps/WPS/Response.py", line 28, in <module>
        from htmltmpl import TemplateManager, TemplateProcessor
    ImportError: No module named htmltmpl

     
Than something is wrong with your Python installation or with the program.
This message means, that the `python-htmltmpl` package is not installed in
your system.
