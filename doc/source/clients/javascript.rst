PyWPS JavaScript client
=======================
Part of PyWPS distribution is also generic WPS client, which is based on
`OpenLayers <http://openlayers.org>`_. The client *does not show any
results in the map*, but it enables you, as client coder, to program the
client in hopefully easy way. The client is located in
:file:`pywps-source/webclient/WPS.js`. Beside this file, OpenLayers have to
be included in the web page.

Initialization and GetCapabilities request
------------------------------------------
To initialize the WPS object, the service URL have to be known. This
example can be found in :file:`wpsclient/01-init.html`.

.. code-block:: javascript

    // set the proxy
    OpenLayers.ProxyHost = "/cgi-bin/proxy.cgi?url=";
    
    // set the url
    var url = "http://foo/bar/wps.py";

    // init the client
    wps = new OpenLayers.WPS(url);

    // run get capabilities
    wps.getCapabilities(url);

Parsing GetCapabilities response
--------------------------------
You have to define the function, which will be called, after
GetCapabilities response arrived and was parsed.

.. code-block:: javascript

    wps = new OpenLayers.WPS(url, {onGotCapabilities: onGetCapabilities}); 

    /**
     * This function is called, when GetCapabilities response
     * arrived and was parsed
     **/
    function onGetCapabilities() {

        var capabilities = "<h3>"+wps.title+"</h3>";
        capabilities += "<h3>Abstract</h3>"+wps.abstract;
        capabilities += "<h3>Processes</h3><dl>";

        // for each process, get identifier, title and abstract
        for (var i = 0; i < wps.processes.length; i++) {
            var process = wps.processes[i];

            capabilities += "<dt>"+process.identifier+"</dt>";
            capabilities += "<dd>"+"<strong>"+process.title+"</strong><br />"+
                            process.abstract+"</dd>";
        }

        capabilities += "</dl>";

        document.getElementById("wps-result").innerHTML = capabilities;
    };

Parsing DescribeProcess response
--------------------------------
For calling DescribeProcess request, identifier of the process has to be
known to you. You can obtain available processes from the GetCapabilities
response (described previously). Anyway, :func:`onDescribedProcess` has to
be defined.
This example can be found in :file:`wpsclient/02-describe.html`.

.. code-block:: javascript

    wps = new OpenLayers.WPS(url, {onDescribedProcess: onDescribeProcess}); 

    // run get capabilities
    wps.describeProcess("dummyprocess");

    /**
     * This function is called, when DescribeProcess response
     * arrived and was parsed
     **/
    function onDescribeProcess(process) {

        var description = "<h3>"+process.title+"</h3>";
        description += "<h3>Abstract</h3>"+process.abstract;
        description += "<h3>Inputs</h3><dl>";

        // for each input
        for (var i = 0; i < process.inputs.length; i++) {
            var input = process.inputs[i];
            description += "<dt>"+input.identifier+"</dt>";
            description += "<dd>"+"<strong>"+input.title+"</strong><br />"+
                            input.abstract+"</dd>";
        }
        description += "</dl>";
        description += "<h3>Outputs</h3><dl>";

        // for each input
        for (var i = 0; i < process.outputs.length; i++) {
            var output = process.outputs[i];
            description += "<dt>"+output.identifier+"</dt>";
            description += "<dd>"+"<strong>"+output.title+"</strong><br />"+
                            output.abstract+"</dd>";
        }
        description += "</dl>";

        document.getElementById("wps-result").innerHTML = description;
    };


Calling Execute request
-----------------------
For calling Execute request, identifier, inputs and outputs of the process has to be
known to you. You can obtain available processes and their inputs and
outputs from the GetCapabilities and DescribeProcessj
response (described previously). Anyway, :func:`onSucceeded` has to
be defined.

Defining In- and Outputs for the process 'by hand'
..................................................
In this example, we will define In- and Outputs of the process "by hand",
so we will not use the automatic way, via GetCapabilities and
DescribeProcess.
This example can be found in :file:`wpsclient/03-execute.html`.

.. code-block:: javascript

    // WPS object
    wps = new OWS.WPS(url,{onSucceeded: onExecuted});

    // define inputs of the 'dummyprocess'

FIXME to be continued
    
