PyWPS and Java
**************
.. note:: Very important source for this section was `Jython Webapp
    Tutorial
    <http://seanmcgrath.blogspot.com/JythonWebAppTutorialPart1.html>`_ by
    Sean McGrath.  And
    `Distributing Jython Scripts <http://wiki.python.org/jython/JythonFaq/DistributingJythonScripts>`_ page.

Since 3.2x version, PyWPS is able to run in Java environment, using Python interpreter in Java - 
`Jython <http://jython.org>`_ .

With Jython it is possible to access Java classes from Python code, as well
as acces Python classes from Java code. So, it is no big problem to setup
PyWPS, so it runs as Java servlet under Apache `Tomcat
<http://tomcat.apache.org>`_ server and so, being able to access all the
mighty Java tools for geodata processing.

.. note:: One big note must be remarked on this place: Current version of
    Jython (2.5.1) does NOT support `os.fork()` [#f1]_ calls, which is the way,
    PyWPS is able to perform request assynchronously (which is the case, if
    you are requesting `status=true`). So currently, it is NOT possible to
    use assynchronous calls on PyWPS Execute request, if running within
    Jython. There are techniques, which do enable overcome this issue, but
    currently, they are not implemented in PyWPS yet. 

.. note:: We are using Tomcate 6.x. If you test PyWPS on 7.x, please let us
    know.

.. note:: You should work with distribution of Java from Sun (now Oracle).
    Other JVMs are not tested (and usually, their usage is problematic).
    You can test, which interpreter you are using by running::

        java -version

        java version "1.6.0_20"
        Java(TM) SE Runtime Environment (build 1.6.0_20-b02)
        Java HotSpot(TM) 64-Bit Server VM (build 16.3-b01, mixed mode)

Before running PyWPS as Java servlet, several steps have to be performed. 

#. Install Apache Tomcat server [#f2]_
#. Configure Apache Tomcat 
#. Prepare the Jython-lib package
#. Write the PyWPS-Servlet wrapper (similar to CGI wrapper)
#. Run the server

It is assumed, you have downloaded and installed the Tomcat server in your
system.

Configure Tomcat
================
Create `wps` directory within the `webapps` directory of Tomcat.::

    cd apache-tomcat-6.0.29/wps
    mkdir wps 

Create also the configuration directory within new `wps` directory and
location for used Java lib::

    mkdir wps/WEB-INF
    mkdir wps/lib

Configuration in Tomcat happens in :file:`web.xml` file, located in the
`WEB-INF` directory. There is example of such configuration file, which you
can simply copy from PyWPS source ::

    cp $PYWPS_SOURCE/webservices/tomcat/web.xml wps/WEB-INF/

As second, copy the content of `pywps` module to `wps` directory::

    cp -r $PYWPS_SOURCE/pywps wps/

(You should now have directories like `wps/pywps/default.py,
wps/pywps/Exceptions.py, wps/pywps/Parser.py` and others.) 

Prepare the jython-lib package
==============================
Download and install Jython. Once, you download it, you have to run the
install script::
    
    java -jar jython_installer-2.5.1.jar

Once it is installed, you have to crate Java archive, with all necessary
Python modules and copy it to `wps` directory of Tomcat server::

    cd $JYTHON_HOME
    cp jython.jar jythonlib.jar
    zip -r jythonlib.jar Lib
    cp jythonlib.jar $CATALINA_HOME/webapps/wps/lib/
    
Now you should be able to configure PyWPS wrapper script

Prepare the PyWPS-Servlet wrapper
=================================
Take the :file:`webservices/tomcat/PywpsServlet.py` file and store it to
`webapps/wps/` directory.::

    cp $PYWPS_SOURCE/webservices/tomcat/PywpsServlet.py wps/`

Let's edit it

.. literalinclude:: ../../../webservices/tomcat/PywpsServlet.py
   :language: python

Note the `getProcesses()` method, which creating one process on-the-fly. 

.. centered:: That is the way, how you can create custom Java-based processes
    and make them accessable via PyWPS.

You can also set some environment variables, as you are probably used to:

.. code-block:: python

    import os
    os.environ["PYWPS_PROCESSES"] = "/path/to/processes"

the complete script looks like follows

.. code-block:: python
    
        
    from java.io import *
    from javax.servlet.http import HttpServlet 

    import pywps
    from pywps.Exceptions import *
    import traceback
    import os

    class PywpsServlet(HttpServlet):

        def doGet(self,request,response):

            inputQuery = request.getQueryString()
            if not inputQuery:
                e = NoApplicableCode("Missing request value")
                pywps.response.response(e,response)
            self.doPywps(request, response, inputQuery, pywps.METHOD_GET)

        def doPost(self,request,response):

            inputQuery = request.getQueryString()
            self.doPywps(request, response, inputQuery, pywps.METHOD_POST)

        def doPywps(self,request, response, inputQuery,method):

            os.environ["PYWPS_PROCESSES"] = "/usr/local/src/pywps/trunk/tests/processes/"
            # create the WPS object
            try:
                wps = pywps.Pywps(method)
                if wps.parseRequest(inputQuery):
                    pywps.debug(wps.inputs)
                    wpsresponse = wps.performRequest()
                    if wpsresponse:
                        pywps.response.response(wps.response, response, wps.parser.isSoap)
            except WPSException,e:
                pywps.response.response(e, response)


Run the server
==============
... and see, what happens.::

    bin/startup.sh

        Using CATALINA_BASE:   /tmp/apache-tomcat-6.0.29
        Using CATALINA_HOME:   /tmp/apache-tomcat-6.0.29
        Using CATALINA_TMPDIR: /tmp/apache-tomcat-6.0.29/temp
        Using JRE_HOME:        /usr/lib/jvm/java-6-sun/
        Using CLASSPATH:       /tmp/apache-tomcat-6.0.29/bin/bootstrap.jar


Test the PyWPS, to to url http://localhost:8080/wps/PywpsServlet?service=wps&request=getcapabilities

And let us execute something as well: http://localhost:8080/wps/PywpsServlet.py?service=wps&request=execute&version=1.0.0&identifier=dummyprocess

Conclusion
==========
This chapter describes the basics, how to setup Apache Tomcat server
together with PyWPS. Advanced users will probably skip the configuration
part and go directly to PyWPS part. 

It shows, how easy it is to connect two worlds: Python and Java. It makes
it easy to access Java-based analytical tools being exposed to the outside
world via OGC WPS.

.. [#f1] http://wiki.python.org/jython/JythonFaq/ProgrammingJython#TheJython.27sosmoduleismissingsomefunctions.2Cwhy.3F
.. [#f2] Ubuntu users: better use the version from Apache side, rather then
        package from ubuntu repository.

