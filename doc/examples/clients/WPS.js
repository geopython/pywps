/**
 * Author:      Jachym Cepicky <jachym les-ejk cz>
 *              http://les-ejk.cz
 * Purpose:     Generic WPS Client for JavaScript programming language
 * Version:     0.0.1
 * Supported WPS Versions: 1.0.0
 *
 * The Library is designed to work mainly with OpenLayers
 * [http://openlayers.org]
 * 
 * Licence:     
 *  Web Processing Service Client implementation
 *  Copyright (C) 2009 Jachym Cepicky
 * 
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 * 
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 * 
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *
 *  TODO:
 *  - a lot
 */

/**
 * Class:   OWS
 * Generic OpenWebServices Class. This could support other W*Ss defined by
 * OGC
 */
var OWS = function() {
    var cls = function() {
        if (this.initialize) {
            this.initialize.apply(this, arguments);
        }
    };

    var extended = {};
    var parent;
    extended = OWS.Utils.extend(this,extended);
    for(var i=0, len=arguments.length; i<len; ++i) {
        if(typeof arguments[i] == "function") {
            // get the prototype of the superclass
            parent = arguments[i].prototype;
        } else {
            // in this case we're extending with the prototype
            parent = arguments[i];
        }
        extended = OWS.Utils.extend(parent,extended);
    }

    cls.prototype = extended;
    return cls;
};

/**
 * Class:    OWS.Utils
 * Some useful functions, which makes life easier
 */
OWS.Utils = {

    /**
     * Function:    extend
     * Extend target object with attributes from the source object
     *
     * Parameters:
     * source   - {Object} 
     * target   - {Object}
     *
     * Returns
     * {Object} extended target object
     */
    extend : function(source,target) {

        for(var property in source) {
            var value = source[property];
            if(value !== undefined) {
                target[property] = value;
            }
        }
        return target;
        
    },

    /**
     * Function: extendUrl
     * Extend URL parameters with newParams object
     *
     * Parameters:
     * source - {String} url
     * newParams - {Object}
     *
     * Returns:
     * {String} new URL
     */
    extendUrl: function(source,newParams) {
        var sourceBase = source.split("?")[0];
        try {
            var sourceParamsList = source.split("?")[1].split("&");
        }
        catch (e) {
            var sourceParamsList = [];
        }
        var sourceParams = {};

        for (var i = 0; i < sourceParamsList.length; i++) {
            var key; var value;
            key = sourceParamsList[i].split('=')[0];
            value = sourceParamsList[i].split('=')[1];
            if (key && value ) {
                sourceParams[key] = value;
            }
        }
        newParams = OWS.Utils.extend(newParams, sourceParams);

        var newParamsString = "";
        for (var key in newParams) {
            newParamsString += "&"+key+"="+newParams[key];
        }
        return sourceBase+"?"+newParamsString;
    },

    /**
     * Method: loadGet
     * Loads the request via HTTP GET method
     *
     * Parameters:
     * uri - {String}
     * params - {Object}
     * success - {Function}
     * failure -  {Function}
     * scope - {Object}
     *
     * Returns:
     * {HTTPRequest}
     */
    loadGet : function (uri,params, success,failure, scope) { 
        var request = null;
        try {
            request =  OpenLayers.Request.GET({
                url: uri, params:{},
                success: success, failure: failure, scope:  scope
            });
        }
        catch(e) {
            throw new Exception("Could not load Ajax: Is OpenLayers available? "+e);
            return;
        }
        return request;
    },

    /**
     * Method: loadPost
     * Loads the request via HTTP POST method
     *
     * Parameters:
     * uri - {String}
     * data - {Object}
     * success - {Function}
     * failure -  {Function}
     * scope - {Object}
     *
     * Returns:
     * {HTTPRequest}
     */
    loadPost : function (uri,data, success,failure, scope) { 
        var request = null;
        try {
            request =  OpenLayers.Request.POST({
                url: uri, 
                data:data,
                success: success,
                failure: failure,
                scope:  scope
            });
        }
        catch(e) {
            throw new Exception("Could not load Ajax: Is OpenLayers available? "+e);
        }
        return request;
    },
    
    /**
     * Function: debug
     * Write somethig to Firebug's console
     *
     */
    debug : function() {
        try {
            for (var i = 0; i < arguments.length; i++) {
                console.log(arguments[i]);
            }
        }
        catch(e) {
        }
    },

    /**
     * Function: getDomFromString
     * Create DOM from String
     *
     * Parameters:
     * str - {String}
     *
     * Returns
     * {DOM}
     */
    getDomFromString : function(str) {
        try {
            return  OpenLayers.parseXMLString(str);
        }
        catch(e)  {
            this.debug("OpenLayers not available, I have to parse the string myself.");

            try {
                var xmldom = new ActiveXObject('Microsoft.XMLDOM');
                xmldom.loadXML(text);
                return xmldom;
            }
            catch(e) {
                try {
                    return new DOMParser().parseFromString(text, 'text/xml');
                }
                catch(e) {
                    try {
                        var req = new XMLHttpRequest();
                        req.open("GET", "data:" + "text/xml" +
                                ";charset=utf-8," + encodeURIComponent(text), false);
                        if (req.overrideMimeType) {
                            req.overrideMimeType("text/xml");
                        }
                        req.send(null);
                        return req.responseXML;
                    }
                    catch(e) {
                        OWS.Utils.debug("Could not parse String to DOM");
                    }
                }
            }
        }
    },

    /**
     * Function:    isIn
     * Check, if some element is in array
     *
     * Parameters:
     * list - {Array}
     * elem - {Object} 
     *
     * Returns:
     * {Boolean} weather the element is in the list or not
     */
    isIn  : function(list, elem) {
        var obj = {};
        for(var i = 0; i <list.length;i++) {
            obj[list[i]] = null;
        }
        return elem in obj;
    }

};

/**
 * Class: OWS.WPS
 * Web Processing Service Client
 */
OWS.WPS = new OWS({
    /**
     * Property: service
     * {String}
     */
    service: "wps",
    /**
     * Property: version
     * {String}
     */
    version: "1.0.0",
    /**
     * Property: getCapabilitiesUrlGet
     * {String}
     */
    getCapabilitiesUrlGet: null,
    /**
     * Property: getCapabilitiesUrlPost
     * {String}
     */
    getCapabilitiesUrlPost: null,
    /**
     * Property: describeProcessUrlGet
     * {String}
     */
    describeProcessUrlGet: null,
    /**
     * Property: describeProcessUrlPost
     * {String}
     */
    describeProcessUrlPost: null,
    /**
     * Property: executeUrlGet
     * {String}
     */
    executeUrlGet: null,
    /**
     * Property: executeUrlPost
     * {String}
     */
    executeUrlPost: null,

    /**
     * Property:  owsNS
     * {String}
     */
    owsNS: "http://www.opengis.net/ows/1.1",

    /**
     * Property:  owsPref
     * {String}
     */
    owsPref: "ows",

    /**
     * Property:  xlinkNS
     * {String}
     */
    xlinkNS: "http://www.w3.org/1999/xlink",

    /**
     * Property:  xlinkPref
     * {String}
     */
    xlinkPref: "xlink",

    /**
     * Property:  wpsNS
     * {String}
     */
    wpsNS: "http://www.opengis.net/wps/",

    /**
     * Property:  wpsPref
     * {String}
     */
    wpsPref: "wps",

    /**
     * Property:  title
     * {String}
     */
    title: null,
    
    /**
     * Property:  abstr
     * {String}
     */
    abstr: null,

    /**
     * Property:  processes
     * {List} Avaliable processes
     */
    processes: [],

    /**
     * Property: timeOut
     * {Integer}, ms
     */
    timeOut: 5000,

    /**
     * Property: statusLocation
     * {String}
     */
    statusLocation: null,

    /**
     * Property: status
     * {String}
     */
    status: null,

    /**
     * Property: assync
     * {Boolean} status = true
     */
    assync: false,

    /**
     * Property: statusMessage
     * {String} 
     */
    statusMessage: null,

    /**
     * Property: statusTime
     * {String} 
     */
    statusTime: null,

    /**
     * Property: percentCompleted
     * {String} 
     */
    percentCompleted: null,

    /**
     * Property: id
     * {Integer}
     */
    id: null,

    /**
     * Property: statusEvents
     * {Object}
     */
    statusEvents : {},

    /**
     * Contructor: initialize
     *
     * Parameters:
     * url - {String} initial url of GetCapabilities request
     * params - {Object}
     */
    initialize: function(url,params) {
        this.getCapabilitiesUrlGet = url;
        this.describeProcessUrlGet = url;
        this.executeUrlGet = url;
        this.getCapabilitiesUrlPost = url;
        this.describeProcessUrlPost = url;
        this.executeUrlPost = url;

        OWS.Utils.extend(params,this);

        /* if (this.getCapabilitiesUrlGet) {
             this.getCapabilitiesGet(this.getCapabilitiesUrlGet);
         }
        */

        this.wpsNS +=this.version;

        OWS.WPS.instances.push(this);
        this.id = OWS.WPS.instances.length-1;

        this.statusEvents = {
                    "ProcessAccepted":this.onAccepted,
                    "ProcessSucceeded":this.onSucceeded,
                    "ProcessFailed":this.onFailed,
                    "ProcessStarted":this.onStarted,
                    "ProcessPaused":this.onPaused};
    },

    /**
     * Method: getCapabilities
     *
     * Parameter:
     * url - {String} if ommited, this.getCapabilitiesUrlGet is taken
     */
    getCapabilities : function(url) {
        this.getCapabilitiesGet(url);
    },

    /**
     * Method: getCapabilitiesGet
     * Call GetCapabilities request via HTTP GET
     *
     * Parameter:
     * url - {String} if ommited, this.getCapabilitiesUrlGet is taken
     */
    getCapabilitiesGet : function(url) {
        if (url) {
            this.getCapabilitiesUrlGet = url;
        }
        var uri = OWS.Utils.extendUrl(url,{service: this.service, version: this.version,request: "GetCapabilities"});

        var request = OWS.Utils.loadGet(uri, {}, this.parseGetCapabilities, this.onException,this);
    },

    /**
     * Method: describeProcess
     *
     * Parameter:
     * identifier
     */
    describeProcess: function(identifier) {
        if(this.describeProcessUrlGet) {
            this.describeProcessGet(identifier);
        }
    },

    /**
     * Method: describeProcessGet
     *
     * Call DescribeProcess request via HTTP GET
     *
     * Parameter:
     * identifier - {String} 
     */
    describeProcessGet : function(identifier) {
        var uri = OWS.Utils.extendUrl(this.describeProcessUrlGet,{service:this.service,version:this.version,
                                                                request:"DescribeProcess",identifier:identifier});

        var request = OWS.Utils.loadGet(uri, {}, this.parseDescribeProcess, this.onException, this);
    },

    /**
     * Method: parseGetCapabilities
     * Parse input response document and call onGotCapabilities at the end
     *
     * Parameters:
     * resp - {XMLHTTP}
     */
    parseGetCapabilities: function (resp) {
        var dom = resp.responseXML ? resp.responseXML : OWS.Utils.getDomFromString(resp.responseText);
        this.title = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Title")[0].firstChild.nodeValue;
        this.abstract = null;
        try {
            this.abstract = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Abstract")[0].firstChild.nodeValue;
        } catch(e) {}

        // describeProcess Get, Post
        // execute Get, Post
        var operationsMetadataNode = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "OperationsMetadata")[0];
        var operationsMetadata = OpenLayers.Ajax.getElementsByTagNameNS(operationsMetadataNode,this.owsNS, this.owsPref, "Operation");
        for (var i = 0; i < operationsMetadata.length; i++) {
            var operationName = operationsMetadata[i].getAttribute("name");
            var get = OpenLayers.Ajax.getElementsByTagNameNS(operationsMetadata[i],this.owsNS, this.owsPref, "Get")[0].getAttributeNS(this.xlinkNS, xlink.wpsPref, "href");
            var post = OpenLayers.Ajax.getElementsByTagNameNS(operationsMetadata[i],this.owsNS, this.owsPref, "Post")[0].getAttributeNS(this.xlinkNS, xlink.wpsPref, "href");

            switch(operationName.toLowerCase()) {
                case "getcapabilities": this.getCapabilitiesUrlGet = get;
                                        this.getCapabilitiesUrlPost = post;
                                        break;
                case "describeprocess": this.describeProcessUrlGet = get;
                                        this.describeProcessUrlPost = post;
                                        break;
                case "execute": this.executeUrlGet = get;
                                        this.executeUrlPost = post;
                                        break;
            }
        }

        // processes
        var processesNode = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.wpsNS, this.wpsPref, "ProcessOfferings")[0];
        var processes = OpenLayers.Ajax.getElementsByTagNameNS(processesNode,this.wpsNS, this.wpsPref, "Process");
        for (var i = 0; i < processes.length; i++) {
            var identifier = OpenLayers.Ajax.getElementsByTagNameNS(processes[i],this.owsNS, this.owsPref, "Identifier")[0].firstChild.nodeValue;
            var title = OpenLayers.Ajax.getElementsByTagNameNS(processes[i],this.owsNS, this.owsPref, "Title")[0].firstChild.nodeValue;
            var abstract = null;
            try {
                abstract = OpenLayers.Ajax.getElementsByTagNameNS(processes[i],this.owsNS, this.owsPref, "Abstract")[0].firstChild.nodeValue;
            } catch(e) {}
            var version = processes[i].getAttributeNS(this.wpsNS, this.wpsPref, version);
            var process = new OWS.Process({identifier:identifier,title: title, abstract: abstract, version: version,wps:this});
            this.addProcess(process);
        }

        this.onGotCapabilities();
    },

    /**
     * Method: addProcess
     * Add process to this.processes list
     *
     * Parameters:
     * process - {Object}
     */
    addProcess: function(process) {
        this.processes.push(process);
    },

    /**
     * Method: parseDescribeProcess
     * Parse DescribeProcess response and call this.onDescribedProcess
     *
     * Parameters:
     * resp - {HTTPRexuest}
     */
    parseDescribeProcess: function (resp) {
        var dom = resp.responseXML ? resp.responseXML : OWS.Utils.getDomFromString(resp.responseText);

        var processes = dom.getElementsByTagName("ProcessDescription");
        for (var i = 0; i < processes.length; i++) {
            var identifier = OpenLayers.Ajax.getElementsByTagNameNS(processes[i],this.owsNS, this.owsPref, "Identifier")[0].firstChild.nodeValue;
            var process = this.getProcess(identifier);

            process.title = OpenLayers.Ajax.getElementsByTagNameNS(processes[i],this.owsNS, this.owsPref, "Title")[0].firstChild.nodeValue;
            process.abstract = OpenLayers.Ajax.getElementsByTagNameNS(processes[i],this.owsNS, this.owsPref, "Abstract")[0].firstChild.nodeValue;
            process.version = processes[i].getAttributeNS(this.wpsNS, this.wpsPref, "processVersion");

            /* parseInputs */
            process.inputs = process.inputs.concat(process.inputs,
                        this.parseDescribePuts(processes[i].getElementsByTagName("Input")));

            /* parseOutputs */
            process.outputs = process.outputs.concat(process.outputs,
                        this.parseDescribePuts(processes[i].getElementsByTagName("Output")));

            this.onDescribedProcess(process);
        }
        
    },

    /**
     * Method: parseDescribePuts
     * Parse Inputs and Outputs of the DescribeProcess elements
     *
     * Parameters:
     * puts - {List} of {DOM}s
     *
     * Returns
     * {List} of {OWS.Put}
     */
    parseDescribePuts: function(puts) {
        var wpsputs = [];
        for (var i = 0; i < puts.length; i++) {
            // inputs
            if (puts[i].getElementsByTagName("LiteralData").length > 0) {
                wpsputs.push(this.parseDescribeLiteralPuts(puts[i]));
            }
            else if (puts[i].getElementsByTagName("ComplexData").length > 0) {
                wpsputs.push(this.parseDescribeComplexPuts(puts[i]));
            }
            else if (puts[i].getElementsByTagName("BoundingBoxData").length > 0) {
                wpsputs.push(this.parseDescribeBoundingBoxPuts(puts[i]));
            }

            // outputs
            if (puts[i].getElementsByTagName("LiteralOutput").length > 0) {
                wpsputs.push(this.parseDescribeLiteralPuts(puts[i]));
            }
            else if (puts[i].getElementsByTagName("ComplexOutput").length > 0) {
                wpsputs.push(this.parseDescribeComplexPuts(puts[i]));
            }
            else if (puts[i].getElementsByTagName("BoundingBoxOutput").length > 0) {
                wpsputs.push(this.parseDescribeBoundingBoxPuts(puts[i]));
            }

            // metadata
            var metadataDom = OpenLayers.Ajax.getElementsByTagNameNS(puts[i],this.owsNS, this.owsPref, "Metadata");
            var metadata = {};
            if (metadataDom.length>0) {
                metadataDom[metadataDom[i].getAttributeNS(this.xlinkNS, xlink.wpsPref, "title")] = metadataDom[i].firstChild.nodeValue;
            }
            wpsputs[wpsputs.length-1].metadata = metadata;
        }
        return wpsputs;
    },

    /**
     * Method: parseDescribeComplexPuts
     * Parse ComplexValue elements
     *
     * Parameters:
     * dom - {DOM}  input
     */
    parseDescribeComplexPuts: function(dom){
        var identifier = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Identifier")[0].firstChild.nodeValue;
        var title = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Title")[0].firstChild.nodeValue;
        var abstract = null;
        try {
            abstract = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Abstract")[0].firstChild.nodeValue;
        } catch(e) {}

        var formats = [];

        // inputs
        var cmplxData = dom.getElementsByTagName("ComplexData");
        // outputs
        cmplxData = (cmplxData.length ? cmplxData : dom.getElementsByTagName("ComplexOutput"));



        if (cmplxData.length > 0) {
            // default format first
            var formatsNode = cmplxData[0].getElementsByTagName("Default")[0].getElementsByTagName("Format")[0];
            var frmts = OpenLayers.Ajax.getElementsByTagNameNS(formatsNode,this.owsNS, this.owsPref, "MimeType")[0].firstChild.nodeValue;
            formats.push(frmts);
            
            // all otheres afterwards
            var supportedFormats = cmplxData[0].getElementsByTagName("Supported")[0].getElementsByTagName("Format");
            for (var i = 0; i < supportedFormats.length; i++) {
                var format = OpenLayers.Ajax.getElementsByTagNameNS(supportedFormats[i],this.owsNS, this.owsPref, "MimeType")[0].firstChild.nodeValue;
                if (OWS.Utils.isIn(formats,format) == false) {
                    formats.push(format);
                }
            }
        }

        var asReference = true;
        if (formats[0].search("text") > -1) {
            asReference = false;
        }
        return new OWS.Put.Complex({
                    identifier: identifier,
                    title: title,
                    asReference: asReference,
                    abstract:abstract,
                    formats: formats
                });

    },

    /**
     * Method: parseDescribeBoundingBoxPuts
     * Parse BoundingBox elements
     *
     * Parameters:
     * dom - {DOM} input
     */
    parseDescribeBoundingBoxPuts: function(dom){
        var identifier = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Identifier")[0].firstChild.nodeValue;
        var title = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Title")[0].firstChild.nodeValue;
        var abstract = null;
        try {
            abstract = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Abstract")[0].firstChild.nodeValue;
        } catch(e) {}
        var crss = [];

        // inputs
        var domcrss = dom.getElementsByTagName("BoundingBoxData")[0];
        // outputs
        if (!domcrss) {
            domcrss = dom.getElementsByTagName("BoundingBoxOutput")[0];
        }

        // default first
        crss.push(domcrss.getElementsByTagName("Default")[0].getElementsByTagName("CRS")[0].getAttributeNS(this.xlinkNS, xlink.wpsPref, "href"));

        // supported afterwards
        var supported = domcrss.getElementsByTagName("Supported");
        for (var i = 0; i < supported.length; i++) {
            var crs = supported[i].getElementsByTagName("CRS")[0].getAttributeNS(this.xlinkNS, xlink.wpsPref, "href");
            if (OWS.Utils.isIn(crss,crs) == false) {
                crss.push(crs);
            }
        }


        return new OWS.Put.BoundingBox({
                    identifier: identifier,
                    title: title,
                    abstract:abstract,
                    crss: crss
                });
    },

    /**
     * Method: parseDescribeLiteralPuts
     * Parse LiteralValue elements
     *
     * Parameters:
     * dom - {DOM}  input
     */
    parseDescribeLiteralPuts: function(dom){

        var identifier = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Identifier")[0].firstChild.nodeValue;
        var title = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Title")[0].firstChild.nodeValue;
        var abstract = null;
        try {
            abstract = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Abstract")[0].firstChild.nodeValue;
        } catch(e) {}

        var allowedValues = [];
        var type = "string";
        var defaultValue = null;
        var inputs = [];
        
        // dataType
        var dataType = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "DataType")[0];
        if (dataType) {
            type = dataType.firstChild.nodeValue.toLowerCase();
        }
        // anyValue
        if (OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "AnyValue").length > 0){
            allowedValues = ["*"];
        }
        // allowedValues
        else if (OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "AllowedValues").length > 0) {
            var nodes = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, 
                                    "AllowedValues")[0].childNodes;
            // allowedValues
            for (var i = 0; i < nodes.length; i++) {
                if (nodes[i].nodeType != 1) { continue; } // skip text and comments
                if (nodes[i].localName == "Value") {
                    allowedValues.push(nodes[i].firstChild.nodeValue);
                }
                // range
                else if (nodes[i].localName == "Range") {
                    var min = OpenLayers.Ajax.getElementsByTagNameNS(nodes[i],this.owsNS, this.owsPref, "MinimumValue")[0].firstChild.nodeValue;
                    var max = OpenLayers.Ajax.getElementsByTagNameNS(nodes[i],this.owsNS, this.owsPref, "MaximumValue")[0].firstChild.nodeValue;
                    allowedValues.push([min,max]);
                }
            }

        }

        return new OWS.Put.Literal({
                identifier : identifier,
                title : title,
                abstract : abstract,
                allowedValues : allowedValues,
                type : type,
                defaultValue : defaultValue
        }); 
    },

    /**
     * Method: execute
     *
     * Parameter:
     * identifier
     */
    execute: function(identifier) {
        if(this.executeUrlPost) {
            this.executePost(identifier);
        }
    },

    /**
     * Method: executePost
     * Call Execute Request via HTTP POST
     *
     * Parameter:
     * identifier - {String} 
     */
    executePost : function(identifier) {
        var uri = this.executeUrlPost
        var process = this.getProcess(identifier);

        var data = OWS.WPS.executeRequestTemplate.replace("$IDENTIFIER$",identifier);
        data = data.replace("$STORE_AND_STATUS$",process.assync);

        // inputs
        var inputs = "";
        for (var i  = 0; i < process.inputs.length; i++ ) {
            var input = process.inputs[i];
            var tmpl = "";
            if (input.CLASS_NAME.search("Complex")>-1) {
                if (input.asReference) {
                    tmpl = OWS.WPS.complexInputReferenceTemplate.replace("$REFERENCE$",escape(input.getValue()));
                }
                else {
                    tmpl = OWS.WPS.complexInputDataTemplate.replace("$DATA$",input.getValue());
                }
            }
            else if (input.CLASS_NAME.search("Literal") > -1) {
                tmpl = OWS.WPS.literalInputTemplate.replace("$DATA$",input.getValue());
            }
            else if (input.CLASS_NAME.search("BoundingBox") > -1) {
                tmpl = OWS.WPS.boundingBoxInputTemplate.replace("$DIMENSIONS$",input.dimensions);
                tmpl = tmpl.replace("$CRS$",input.crs);
                tmpl = tmpl.replace("$MINX$",input.value.minx);
                tmpl = tmpl.replace("$MINY$",input.value.miny);
                tmpl = tmpl.replace("$MAXX$",input.value.maxx);
                tmpl = tmpl.replace("$MAXY$",input.value.maxy);
            }
            tmpl = tmpl.replace("$IDENTIFIER$",input.identifier);

            inputs += tmpl;
        }

        // outputs
        var outputs = "";
        for (var i = 0; i < process.outputs.length; i++) {
            var output = process.outputs[i];
            var tmpl = "";
            if (output.CLASS_NAME.search("Complex")>-1) {
                tmpl = OWS.WPS.complexOutputTemplate.replace("$AS_REFERENCE$",output.asReference);
            }
            else if (output.CLASS_NAME.search("Literal") > -1) {
                tmpl = OWS.WPS.literalOutputTemplate;
            }
            else if (output.CLASS_NAME.search("BoundingBox") > -1) {
                tmpl = OWS.WPS.boundingBoxOutputTemplate;
            }
            tmpl = tmpl.replace("$IDENTIFIER$",output.identifier); 
            outputs += tmpl;
        }
        data = data.replace("$DATA_INPUTS$",inputs);
        data = data.replace("$OUTPUT_DEFINITIONS$",outputs);

        var request = OWS.Utils.loadPost(uri, data, this.parseExecute, this.onException, this);
    },

    /**
     * Method: parseExecute
     * Parse Execute response
     *
     * Parameters:
     * response - {XMLHTTP}
     */
    parseExecute: function(resp) {
        var text = resp.responseText;
        if (OpenLayers.Util.getBrowserName() == "msie") {
            resp.responseXML = null;
            text = text.replace(/<\?xml .[^>]*>/,"");
        }
        var dom = resp.responseXML ? resp.responseXML : OWS.Utils.getDomFromString(text);
        this.statusLocation = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.wpsNS, this.wpsPref, "ExecuteResponse")[0].getAttribute("statusLocation");
        var identifier = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Identifier")[0].firstChild.nodeValue;
        var process = this.getProcess(identifier);
        var status = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.wpsNS, this.wpsPref, "Status");
        if (status.length > 0) { this.parseStatus(status[0]); }

        if (this.status == "ProcessSucceeded") {
            var procOutputsDom = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.wpsNS, this.wpsPref, "ProcessOutputs");
            var outputs = null;
            if (procOutputsDom.length) {
                outputs = OpenLayers.Ajax.getElementsByTagNameNS(procOutputsDom[0],this.wpsNS, this.wpsPref, "Output"); 
            }
            for (var i = 0; i < outputs.length; i++) {
                this.parseExecuteOutput(process,outputs[i]);
            }
        }

        this.statusEvents[this.status](process);
        this.onStatusChanged(this.status,process);
        
        if (this.status != "ProcessFailed" && this.status != "ProcessSucceeded") {
            if (this.statusLocation) {

                window.setTimeout("OWS.Utils.loadGet(OWS.WPS.instances["+this.id+"].statusLocation,"+
                                "{}, OWS.WPS.instances["+this.id+"].parseExecute,"+
                                "   OWS.WPS.instances["+this.id+"].onException, "+
                                "   OWS.WPS.instances["+this.id+"])", this.timeOut);
            }
        }
    },

    /**
     * Method: parseExecuteOutput
     * Parse wps:Output dom element, Store the value to output.value
     * property
     *
     * Parameters:
     * process - {OWS.Process} process, to which this output belongs to
     * dom - {DOMelement} <wps:Output />
     */
    parseExecuteOutput: function(process,dom) {
        var identifier  = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.owsNS, this.owsPref, "Identifier")[0].firstChild.nodeValue;
        var output = process.getOutput(identifier);

        var literalData = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.wpsNS, this.wpsPref, "LiteralData");
        var complexData = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.wpsNS, this.wpsPref, "ComplexData");
        var boundingBoxData = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.wpsNS, this.wpsPref, "BoundingBox");
	var reference = OpenLayers.Ajax.getElementsByTagNameNS(dom,this.wpsNS, this.wpsPref, "Reference");
	

	if (reference.length > 0) {
            output.setValue(reference[0].getAttributeNS(this.xlinkNS, xlink.wpsPref, "href"));
        }
        else if(literalData.length > 0) {
            output.setValue(literalData[0].firstChild.nodeValue);
        }
        else if (complexData.length > 0) {
            // set output do DOM
            for (var i = 0; i < complexData[0].childNodes.length; i++) {
                var node = complexData[0].childNodes[i];
                if (node.nodeType == 1) {
                    output.setValue(node);
                }
            }
            // if output is still empty, try to fetch the text content 
            if (!output.getValue()) {
                output.setValue(complexData[0].textContent);
            }
        }
        else if (boundingBoxData.length > 0 ) {
	    var minxy; var maxxy;
	    minxy = OpenLayers.Ajax.getElementsByTagNameNS(boundingBoxData,this.owsNS, this.owsPref, "LowerCorner");
	    maxxy = OpenLayers.Ajax.getElementsByTagNameNS(boundingBoxData,this.owsNS, this.owsPref, "UpperCorner");
	    var crs = boundingBoxData.getAttribute("crs");
	    var dimensions = boundingBoxData.getAttribute("dimensions");
            output.setValue([minxy.split(" ")[0],minxy.split(" ")[1],
			     maxxy.split(" ")[0],maxxy.split(" ")[1]]);
	    output.dimensions = dimensions;
	    output.crs = crs;
        }

    },

    /**
     * Method: setStatus
     *
     * Parameters:
     * status - {String} "ProcessSucceeded","ProcessFailed","ProcessStarted","ProcessPaused"
     * message - {String}
     * creationTime - {String}
     * percentCompleted - {Float}
     */
    setStatus: function(status,message,creationTime,percentCompleted) {

        this.status = status;
        this.statusMessage = message;
        this.statusTime = creationTime;
        this.percentCompleted = percentCompleted;
    },

    /**
     * Method: parseStatus
     *
     * Parameters:
     * status - {dom}
     */
    parseStatus: function(status) {
        for (var k in this.statusEvents) {
            var dom = OpenLayers.Ajax.getElementsByTagNameNS(status,this.wpsNS, this.wpsPref, k);
            if (dom.length>0) {
                this.setStatus(k,
                            dom[0].firstChild.nodeValue,
                            status.getAttribute("creationTime"),
                            dom[0].getAttribute("percentCompleted"));
            }
        }
    },

    /**
     * Method: onAccepted
     * To be redefined by the user
     */
    onAccepted: function(process) {
    },

    /**
     * Method: onSucceeded
     * To be redefined by the user
     */
    onSucceeded: function(process) {
    },

    /**
     * Method: onFailed
     * To be redefined by the user
     */
    onFailed: function(process) {
    },
    /**
     * Method: onStarted
     * To be redefined by the user
     */
    onStarted: function(process) {
    },

    /**
     * Method: onPaused
     * To be redefined by the user
     */
    onPaused: function(process) {
    },

    /**
     * Method: getProcess
     * Get particular process from the list of processes based on it's
     * identifier
     *
     * Parameters:
     * identifier - {String}
     *
     * Returns:
     * {Process}
     */
    getProcess: function(identifier) {
        
        for (var i = 0; i < this.processes.length; i++) {
            if (this.processes[i].identifier == identifier) {
                return this.processes[i];
            }
        }
        return undefined;
    },

    /**
     * Method: onException
     * Called, when some exception occured
     *
     * FIXME: Not finished yet!
     */
    onException: function () {
        var dom = OWS.Utils.getDomFromString(resp.responseText);
    },

    /**
     * Method: onGotCapabilities
     * To be redefined by the user
     */
    onGotCapabilities: function() {

    },

    /**
     * Method: onDescribedProcess
     * To be redefined by the user
     *
     * Parameters:
     * process
     */
    onDescribedProcess: function(process) {

    },

    /**
     * Method: onStatusChanged
     * To be redefined by the user
     *
     * Parameters:
     * status 
     * process
     */
    onStatusChanged: function(status,process) {

    }
});


/**
 * Class OWS.Process
 * Process object
 */
OWS.Process = new OWS({
    /**
     * Property: identifier
     * {String}
     */
    identifier:  null,
    
    /**
     * Property: title
     * {String}
     */
    title: null,

    /**
     * Property: abstract
     * {String}
     */
    abstract: null,

    /**
     * Property: inputs
     * {List}
     */
    inputs : [],

    /**
     * Property: output
     * {List}
     */
    outputs : [],

    /**
     * Property: metadata
     * {Object}
     */
    metadata: {},

    /**
     * Property: version
     * {String}
     */
    version: null,

    /**
     * Property: status
     * {Boolean}
     */
    status: false,

    /**
     * Property: wps
     * {String}
     */
    wps: null,

    /**
     * Construcor: identifier
     *
     * Parameters:
     * params   {Object}
     */
    initialize: function(params) {
        OWS.Utils.extend(params,this);
    },

    /**
     * Method: addInput
     */
    addInput : function(params) {
    },
    /**
     * Method: addOutput
     */
    addOutput : function(params) {
    },
    /**
     * Method: execute
     */
    execute :  function(){
        this.wps.execute(this.identifier);
    },

    /**
     * Method: getInput
     *
     * Parameters:
     * identifier {String}
     *
     * Returns:
     * {Object} input
     */
    getInput: function(identifier) {
        for (var i = 0; i < this.inputs.length;i++) {
            if (this.inputs[i].identifier == identifier) {
                return this.inputs[i];
            }
        }
        return null;
    },

    /**
     * Method: getOutput
     *
     * Parameters:
     * identifier {String}
     *
     * Returns:
     * {Object} output
     */
    getOutput: function(identifier) {
        for (var i = 0; i < this.outputs.length;i++) {
            if (this.outputs[i].identifier == identifier) {
                return this.outputs[i];
            }
        }
        return null;
    },

    CLASS_NAME: "OWS.Process"
});

/**
 * Class:   OWS.Put
 * In- and Outputs base class
 */
OWS.Put = new OWS({
    /**
     * Property:    identifier
     * {String}
     */
    identifier:  null,

    /**
     * Property:    title
     * {String}
     */
    title: null,

    /**
     * Property:    abstract
     * {String}
     */
    abstract: null,

    /**
     * Property:    value
     * {Object}
     */
    value: null,

    /**
     * Constructor:    initialize
     * {String}
     */
    initialize: function(params) {
        OWS.Utils.extend(params,this);
    },

    /**
     * Method:  setValue
     */
    setValue: function(value) {
        this.value = value;
    },

    /**
     * Method:  getValue
     */
    getValue: function() {
        return this.value;
    },

    CLASS_NAME: "OWS.Put"
});

/**
 * Class:   OWS.Put.Literal
 * Base Class for LiteralData In- and Outputs
 */
OWS.Put.Literal = new OWS(OWS.Put,{
    allowedValues:[],
    defaultValue: null,
    type: null,
    CLASS_NAME: "OWS.Put.Literal"
});

/**
 * Class:   OWS.Put.Complex
 * Base Class for ComplexData In- and Outputs
 */
OWS.Put.Complex = new OWS(OWS.Put,{
    asReference:false,
    formats:[],
    CLASS_NAME: "OWS.Put.Complex"
});

/**
 * Class:   OWS.Put.BoundingBox
 * Base Class for BoundingBoxData In- and Outputs
 */
OWS.Put.BoundingBox = new OWS(OWS.Put,{
    dimensions:2,
    crss: null,
    value: {minx: null,miny:null, maxx: null,maxy:null,bottom:null, top:null},
    CLASS_NAME: "OWS.Put.BoundingBox"
});
/*
OWS.Put.LiteralOutput = new OWS(OWS.Put,{
    allowedValues:[],
    defaultValue: null,
    type: null,
    CLASS_NAME: "OWS.Put.LiteralOutput"
});

OWS.Put.ComplexOutput = new OWS(OWS.Put,{
    asReference:false,
    formats:[],
    CLASS_NAME: "OWS.Put.ComplexOutput"
});

OWS.Put.BoundingBoxOutput = new OWS(OWS.Put,{
    dimensions:2,
    crss: null,
    bbox: {minx: null,miny:null, maxx: null,maxy:null,bottom:null, top:null},
    CLASS_NAME: "OWS.Put.BoundingBoxOutput"
});
*/

/**
 * Property:    executeRequestTemplate
 * {String} Temple for Execute Request XML 
 */
OWS.WPS.executeRequestTemplate = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+
                                 '<wps:Execute service="WPS" version="1.0.0" '+
                                 'xmlns:wps="http://www.opengis.net/wps/1.0.0" '+
                                 'xmlns:ows="http://www.opengis.net/ows/1.1" '+
                                 'xmlns:xlink="http://www.w3.org/1999/xlink" '+
                                 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '+
                                 'xsi:schemaLocation="http://www.opengis.net/wps/1.0.0/wpsExecute_request.xsd">'+
                                 '<ows:Identifier>$IDENTIFIER$</ows:Identifier>'+
                                '<wps:DataInputs>'+
                                "$DATA_INPUTS$"+
                                '</wps:DataInputs>'+
                                '<wps:ResponseForm>'+
                                '<wps:ResponseDocument wps:lineage="false" '+
                                'wps:storeExecuteResponse="true" '+
                                'wps:status="$STORE_AND_STATUS$">'+
                                "$OUTPUT_DEFINITIONS$"+
                                '</wps:ResponseDocument>'+
                                '</wps:ResponseForm>'+
                                '</wps:Execute>';

/**
 * Property:    literalInputTemplate
 * {String} Temple for Execute Request XML 
 */
OWS.WPS.literalInputTemplate  = "<wps:Input>"+
                                "<ows:Identifier>$IDENTIFIER$</ows:Identifier>"+
                                "<wps:Data>"+
				"<wps:LiteralData>$DATA$</wps:LiteralData>"+
                                "</wps:Data>"+
                                "</wps:Input>";

/**
 * Property:    complexInputReferenceTemplate
 * {String} Temple for Execute Request XML 
 */
OWS.WPS.complexInputReferenceTemplate = "<wps:Input>"+
                                "<ows:Identifier>$IDENTIFIER$</ows:Identifier>"+
                                "<wps:Data>"+
                                '<wps:Reference xlink:href="$REFERENCE$"/>'+
                                "</wps:Data>"+
                                "</wps:Input>";

/**
 * Property:    complexInputDataTemplate
 * {String} Temple for Execute Request XML 
 */
OWS.WPS.complexInputDataTemplate = "<wps:Input>"+
                                "<ows:Identifier>$IDENTIFIER$</ows:Identifier>"+
                                "<wps:Data>"+
				"<wps:ComplexData>"+
                                "$DATA$"+
				"</wps:ComplexData>"+
                                "</wps:Data>"+
                                "</wps:Input>";
/**
 * Property:    boundingBoxInputTemplate
 * {String} Temple for Execute Request XML 
 */
OWS.WPS.boundingBoxInputTemplate = "<wps:Input>"+
                                "<ows:Identifier>$IDENTIFIER$</ows:Identifier>"+
                                "<wps:Data>"+
				'<wps:BoundingBoxData ows:dimensions="$DIMENSIONS$" ows:crs="$CRS$">'+
                                "<ows:LowerCorner>$MINX$ $MINY$</ows:LowerCorner>"+
                                "<ows:UpperCorner>$MAXX$ $MAXY$</ows:UpperCorner>"+
				"</wps:BoundingBoxData>"+
                                "</wps:Data>"+
                                "</wps:Input>";

/**
 * Property:    complexOutputTemplate
 * {String} Temple for Execute Request XML 
 */
OWS.WPS.complexOutputTemplate = '<wps:Output wps:asReference="$AS_REFERENCE$">'+
                                '<ows:Identifier>$IDENTIFIER$</ows:Identifier>'+
                                "</wps:Output>";

/**
 * Property:    literalOutputTemplate
 * {String} Temple for Execute Request XML 
 */
OWS.WPS.literalOutputTemplate = '<wps:Output wps:asReference="false">'+
                                '<ows:Identifier>$IDENTIFIER$</ows:Identifier>'+
                                '</wps:Output>';

/**
 * Property:    boundingBoxOutputTemplate
 * {String} Temple for Execute Request XML 
 */
OWS.WPS.boundingBoxOutputTemplate = OWS.WPS.literalOutputTemplate;

/**
 * Property:    OWS.WPS.instances
 * {List} running instances of WPS
 */
OWS.WPS.instances = [];
