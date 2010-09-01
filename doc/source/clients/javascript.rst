PyWPS JavaScript client
=======================
Part of PyWPS distribution is also generic WPS client, which is based on
`OpenLayers <http://openlayers.org>`_. The client *does not show any
results in the map*, but it enables you, as client coder, to program the
client in hopefully easy way. The client is located in
:file:`PyWPS-source/webclient/WPS.js`. Beside this file, OpenLayers have to
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

The 'by hand' process initialization consists out of three steps:

    1. Definition of process In- and Outputs

    2. Definition of the Process itself

    3. Adding process to WPS instance

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

Defining In- and Outputs for the process automatically
......................................................
In this example, we will define In- and Outputs of the process
automatically, using the  GetCapabilities and
DescribeProcess requests.

This example can be found in :file:`wpsclient/04-execute-automatic.html`.

Just call DescribeProcess first:

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

Handling vector data 
......................................................
A typical operation performed using OpenLayers and a WPS service,
is to send data to the server and display the results directly over the map.
For example consider a process that allows to generate a buffer starting from
vector data and a number to use as buffer's value. From the DescribeProcess we 
see that those two inputs must be passed as "data" and "buffer".
At this point we start with the configuration of OpenLayers:

Add vector layer used for editing and the editing toolbar control:

.. code-block:: javascript

    vlayer = new OpenLayers.Layer.Vector("Editable");
    edit = new OpenLayers.Control.EditingToolbar(vlayer);
    map.addControl(edit);

Now create the WPS object as defined before;a bit of attention to input/output parameters
because we're going to use the featues drawn by the user (vlayer) and a literaldata inserted 
in a HTML text box with buffer as id.

Input:
.. code-block:: javascript

    var dataInput = new OpenLayers.WPS.ComplexPut({
        identifier:"data",
        value:  OpenLayers.Format.GML.prototype.write(vlayer.features)
    });

    var literalInput = new OpenLayers.WPS.LiteralPut({
        identifier:"buffer",
        value: document.getElementById("buffer").value
    });

Ouput:

..code-block:: javascript
    var complexOutput = new OpenLayers.WPS.ComplexPut({
        identifier: "output",
        asReference: "true"
    });
    
Now move to the onSuceedeed function, the one executed once the process has successfully run.
Basically we need to add the output file to the list of layers in the map object. OpenLayers 
allows to add GML directly on the map, but watch out for file too big:

..code-block:: javascript
    var onWPSSussceeded = function(process) {
		//We need to remove the layer generated by previous instance of the script
	    try {
		    map.removeLayer(rlayer);
	        rlayer.destroy();
		} catch(e) {}
	    	url = process.getOutput("output").value;
		    rlayer = new OpenLayers.Layer.GML("Result",url);
	    	Pap.addLayer(rlayer);
