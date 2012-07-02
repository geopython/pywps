Testing PyWPS
*************
Testing PyWPS can be done on the command line -- it is the easier way, how
to get both -- standard error and standard output -- at once. Testing in
the web server environment can be done later.

Before we start to test, be aware that we assume the following:

    1 - PyWPS is installed properly, see :ref:`installation`
    2 - Configuration file is stored in :file:`/usr/local/wps/pywps.cfg`,
        see :ref:`configuration`
    3 - At least one process is stored in the
        :file:`/usr/local/wps/processes` directory.
    4 - There is a :file:`/usr/local/wps/processes/__init__.py` file, with at
        least::

            __all__ = ['yourProcess']

        text in it. For testing purposes, we assume that `yourProcess`
        is `ultimatequestionprocess`. For further reading about how to setup
        custom processes, see :ref:`custom-processes`.

For testing, we are using HTTP GET KVP encoding of OGC WPS request
parameters. If you require clarification of WPS request parameters,
please consult the `OGC WPS 1.0.0 <http://opengeospatial.org/standards/wps>`_ standard.

.. note:: Be aware that this document describes PyWPS, which is a *server*
    implementation of OGC WPS. There is some graphical user interface to
    the server (WPS Clients), but for testing purposes, they are not
    suitable. That is the reason, why following section will use command
    line tools and direct XML outputs.

Testing PyWPS installation
==========================
Find the location of :file:`cgiwps.py` and run it without any further
configuration.::

    $ ./cgiwps.py

And you should get result like this (which is a mixture of standard output
and standard error)::

    Content-type: text/xml

    PyWPS NoApplicableCode: Locator: None; Value: No query string found.
    <?xml version="1.0" encoding="utf-8"?>
    <ExceptionReport version="1.0.0" xmlns="http://www.opengis.net/ows" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <Exception exceptionCode="NoApplicableCode">
                    <ExceptionText>
                            No query string found.
                    </ExceptionText>
            </Exception>
    </ExceptionReport>


Testing PyWPS configuration
===========================
Now we have to export two environment variables: location of the
configuration file and location of processes directory::
    
    $ export PYWPS_CFG=/usr/local/wps/pywps.cfg
    $ export PYWPS_PROCESSES=/usr/local/wps/processes

Afterwards, you can run the PyWPS CGI script. We will use HTTP GET requests,
because they are easy to follow and faster to construct.

GetCapabilities
---------------
On the command line::

    $ ./cgiwps.py "service=wps&request=getcapabilities"

You should obtain a Capabilities response::

    Content-Type: text/xml

    <?xml version="1.0" encoding="utf-8"?>
    <wps:Capabilities service="WPS" version="1.0.0" xml:lang="eng" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd" updateSequence="1">                                                                 
            <ows:ServiceIdentification>            
            [...]

.. note:: Have a more detailed look at the `<wps:ProcessOfferings>...</wps:ProcessOfferings> part of the output XML. There should be at least `Process`


DescribeProcess
---------------
On the command line::

    $ ./cgiwps.py "service=wps&version=1.0.0&request=describeprocess&identifier=Process"

You should obtain a ProcessDescriptions response::

    <?xml version="1.0" encoding="utf-8"?>
    <wps:ProcessDescriptions xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd" service="WPS" version="1.0.0" xml:lang="eng">                                                                             
        <ProcessDescription wps:processVersion="0.2" storeSupported="True" statusSupported="True">                                                                                        
            <ows:Identifier>ultimatequestionprocess</ows:Identifier>                                 
            <ows:Title>The numerical answer to Life, Universe and Everything</ows:Title>                                              
            [...]

Execute
-------
On the command line::
    
    $ ./cgiwps.py "service=wps&version=1.0.0&request=execute&identifier=ultimatequestionprocess"

You should obtain an ExecuteResponse response (this may take some time)::

    <?xml version="1.0" encoding="utf-8"?>
    <wps:ExecuteResponse xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd" service="WPS" version="1.0.0" xml:lang="eng" serviceInstance="http://78.156.32.132/cgi-bin/wps?service=WPS&amp;request=GetCapabilities&amp;version=1.0.0" statusLocation="http://78.156.32.132/tmp/pywps/pywps-126450573849.xml">
        <wps:Process wps:processVersion="2.0">
            <ows:Identifier>ultimatequestionprocess</ows:Identifier>
            <ows:Title>Answer to Life, the Universe and Everything</ows:Title>
            <ows:Abstract>Numerical solution that is the answer to Life, Universe and Everything. The process is an improvement to Deep Tought computer (therefore version 2.0) since it no longer takes 7.5 milion years, but only a few seconds to give a response, with an update of status every 10 seconds.</ows:Abstract>
        </wps:Process>
        <wps:Status creationTime="Tue Jan 26 12:37:18 2010">
            <wps:ProcessSucceeded>PyWPS Process ultimatequestionprocess successfully calculated</wps:ProcessSucceeded>
        </wps:Status>
        <wps:ProcessOutputs>
            <wps:Output>
                <ows:Identifier>answer</ows:Identifier>
                <ows:Title>The numerical answer to Life, Universe and Everything</ows:Title>
                <wps:Data>
                    <wps:LiteralData dataType="integer">42</wps:LiteralData>
                </wps:Data>
            </wps:Output>
        </wps:ProcessOutputs>
    </wps:ExecuteResponse>

Issues
======
.. note:: A list of known problems follows. If you have seen something
    different, please let us know via the mailing list.

.. note:: Every error you get, should have standard error and standard
    output part, but they are mixed together. We describe here the most
    important part, the general error description.

*Could not store file in compiled form: [Errno 13] Permission denied: 'pywps/Templates/1_0_0/GetCapabilities.tmplc'*
    PyWPS tries to store precompiled templates to Templates directory and
    does not have rights for it (or the user, under which PyWPS is running,
    does not have the rights, e.g. www-data). Change permissions of the
    directory, so that other users can write in it as well.

*Process executed. Failed to build final response for output [los]: [Errno 13] Permission denied: '/var/tmp/pywps/los-6165.tif'*
*Process executed. Failed to build final response for output [los]: [Errno 2] No such file or directory: '/var/tmp/pywpsx/los-6217.tif'*
    PyWPS probably successfully calculated the process, but when it tried
    to store result file to output directory, it failed. Try to set
    read-write access to directory with output files or create the output
    directory.

*[Errno 2] No such file or directory: '/tmp/'*
*[Errno 13] Permission denied: '/tmp/'*
    PyWPS did not find some directory or file, configured in the
    configuration file, or the appropriate permissions are not set.
    
*No process in ProcessOfferings listed*
    The :envvar:`PYWPS_PROCESSES` is not set properly or there is no::

        __all__ = ['ultimatequestionprocess']

    in the :file:`__init__.py` in the :envvar:`PYWPS_PROCESSES` directory.
