PyWPS JavaScript client
=======================
Part of the PyWPS distribution includes a generic WPS client based on
`OpenLayers <http://openlayers.org>`_. The client *does not show any
results in a map*, however it enables you to program the client easily.
The client is located in :file:`pywps-source/webclient/WPS.js`.
In addition, OpenLayers must be included in the web page.

Initialization and GetCapabilities request
------------------------------------------
To initialize the WPS object, the service URL is required. This
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
You must define a function to handle the GetCapabilities response.

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
The DescribeProcess request requires the identifier of the process.
You can obtain available processes from the GetCapabilities
response (described previously). The :func:`onDescribedProcess` must be defined.
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
The Execute request requires the identifier, inputs and outputs parameters.
You can obtain available processes and their inputs and
outputs from the GetCapabilities and DescribeProcessj
response (described previously). The :func:`onSucceeded` must be defined.

Defining Inputs and Outputs for the process 'by hand'
.....................................................
In this example, we will define Inputs and Outputs of the process "by hand",
instead of gathering this information automatically via GetCapabilities and
DescribeProcess.

The 'by hand' process initialization consists of three steps:

    1. Definition of process Inputs and Outputs

    2. Definition of the Process itself

    3. Adding a process to the WPS instance

This example can be found in :file:`wpsclient/03-execute.html`.

.. code-block:: javascript

    // WPS object
    wps = new OpenLayers.WPS(url,{onSucceeded: onExecuted});

    // define inputs of the 'dummyprocess'
    var input1 = new OpenLayers.WPS.LiteralPut({identifier:"input1",value:1});
    var input2 = new OpenLayers.WPS.LiteralPut({identifier:"input2",value:2});

    // define outputs of the 'dummyprocess'
    var output1 = new OpenLayers.WPS.LiteralPut({identifier:"output1"});
    var output2 = new OpenLayers.WPS.LiteralPut({identifier:"output2"});

    // define the process and append it to OpenLayers.WPS instance
    var dummyprocess =  new
    OpenLayers.WPS.Process({identifier:"dummyprocess", 
                             inputs: [input1, input2],
                             outputs: [output1, output2]});

    wps.addProcess(dummyprocess);

    // run Execute
    wps.execute("dummyprocess");

Of course, func:`onExecuted` has to be defined:

.. code-block:: javascript

    /**
     * This function is called, when DescribeProcess response
     * arrived and was parsed
     **/
    function onExecuted(process) {
        var executed = "<h3>"+process.title+"</h3>";
        executed += "<h3>Abstract</h3>"+process.abstract;

        executed += "<h3>Outputs</h3><dl>";

        // for each output
        for (var i = 0; i < process.outputs.length; i++) {
            var output = process.outputs[i];
            executed += "<dt>"+output.identifier+"</dt>";
            executed += "<dd>Title: <strong>"+output.title+"</strong><br />"+
                            "Abstract: "+output.abstract+"</dd>";
            executed += "<dd>"+"<strong>Value:</strong> "+
                            output.getValue()+"</dd>";
        }
        executed += "</dl>";
        document.getElementById("wps-result").innerHTML = executed;

    };

Defining Inputs and Outputs for the process automatically
.........................................................
In this example, we will define Inputs and Outputs of the process
automatically, using the  GetCapabilities and DescribeProcess requests.

This example can be found in :file:`wpsclient/04-execute-automatic.html`.

Call DescribeProcess first:

.. code-block:: javascript

    // init the client
    wps = new OpenLayers.WPS(url,{
                onDescribedProcess: onDescribeProcess,
                onSucceeded: onExecuted
            });

    // run Execute
    wps.describeProcess("dummyprocess");

    /**
     * DescribeProcess and call the Execute response
     **/
    function onDescribeProcess(process) {
        process.inputs[0].setValue(1);
        process.inputs[1].setValue(2);

        wps.execute("dummyprocess");
    };

The rest was already defined before.
