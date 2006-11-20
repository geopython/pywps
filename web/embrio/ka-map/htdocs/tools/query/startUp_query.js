/**********************************************************************
 *
 * $Id: startUp_query.js,v 1.4 2006/07/12 15:49:05 acappugi Exp $
 *
 * purpose: start up code to bootstrap initialization of kaMap within
 *          the sample interface.  Examples of using many parts of
 *          the kaMap core api.
 *
 * author: Lorenzo Becchi and Andrea Cappugi
 *
 * contributions by Paul Spencer (pspencer@dmsolutions.ca)
 *
 * TODO:
 *
 **********************************************************************
 *
 * Copyright (c) 2005, DM Solutions Group Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 **********************************************************************/

/******************************************************************************
 *
 * To customize startUp:
 *
 * 1) modify toolbar Layout
 *  act on screen.css file and modify the funcion myMapInitialized().
 *  If you change pan and identifyer images edit switchMode() function too.
 *
 *****************************************************************************/

var myKaMap = myKaNavigator = myKaQuery = myScalebar = myQManager = null;
var queryParams = null;

/**
 * parse the query string sent to this window into a global array of key = value pairs
 * this function should only be called once
 */
function parseQueryString() {
    queryParams = {};
    var s=window.location.search;
    if (s!='') {
        s=s.substring( 1 );
        var p=s.split('&');
        for (var i=0;i<p.length;i++) {
            var q=p[i].split('=');
            queryParams[q[0]]=q[1];
        }
    }
}

/**
 * get a query value by key.  If the query string hasn't been parsed yet, parse it first.
 * Return an empty string if not found
 */
function getQueryParam(p) {
    if (!queryParams) {
        parseQueryString();
    }
    if (queryParams[p]) {
        return queryParams[p];
    } else {
        return '';
    }
}

function myOnLoad() {
    initDHTMLAPI();

	window.onresize=drawPage;

	myKaMap = new kaMap( 'viewport' );

	var szMap = getQueryParam('map');
    var szExtents = getQueryParam('extents');
    var szCPS = getQueryParam('cps');

    var legendOptions = {};
    legendOptions.visibility = typeof gbLegendVisibilityControl != 'undefined' ? gbLegendVisibilityControl : true;
    legendOptions.opacity = typeof gbLegendOpacityControl != 'undefined' ? gbLegendOpacityControl : true;
    legendOptions.order = typeof gbLegendOrderControl != 'undefined' ? gbLegendOrderControl : true;
    legendOptions.query = typeof gbLegendQueryControl != 'undefined' ? gbLegendQueryControl : true;
    
     var myKaLegend = new kaLegend( myKaMap, 'legend', false, legendOptions);
    var myKaKeymap = new kaKeymap( myKaMap, 'keymap' );

    myKaMap.registerForEvent( KAMAP_INITIALIZED, null, myInitialized );
    myKaMap.registerForEvent( KAMAP_MAP_INITIALIZED, null, myMapInitialized );
    myKaMap.registerForEvent( KAMAP_SCALE_CHANGED, null, myScaleChanged );
    myKaMap.registerForEvent( KAMAP_EXTENTS_CHANGED, null, myExtentChanged );
    myKaMap.registerForEvent( KAMAP_LAYERS_CHANGED, null, myLayersChanged );
    myKaMap.registerForEvent( KAMAP_LAYER_STATUS_CHANGED, null, myLayersChanged );
   // myKaMap.registerForEvent( KAMAP_QUERY, null, myQuery );
    myKaMap.registerForEvent( KAMAP_MAP_CLICKED, null, myMapClicked );


    myKaNavigator = new kaNavigator( myKaMap );
    myKaNavigator.activate();
	
	
    myKaQuery = new kaQuery( myKaMap, KAMAP_RECT_QUERY );
   
    myKaRubberZoom = new kaRubberZoom( myKaMap );

    myScalebar = new ScaleBar(1);
    myScalebar.divisions = 3;
    myScalebar.subdivisions = 2;
    myScalebar.minWidth = 150;
    myScalebar.maxWidth = 250;
    myScalebar.place('scalebar');

    myKaSearch=new kaSearch(myKaMap);
    myQManager= new _queryManager(myKaMap,'searchres');
	drawPage();
    myKaMap.initialize( szMap, szExtents, szCPS );
}

/**
 * event handler for KAMAP_INITIALIZED.
 *
 * at this point, ka-Map! knows what map files are available and we have
 * access to them.
 */
function myInitialized() {
    //myMapInitialized( null, myKaMap.getCurrentMap().name );
}

/**
 * event handler for KAMAP_MAP_INITIALIZED
 *
 * the scales are put into a select ... this will be used for zooming
 */
function myMapInitialized( eventID, mapName ) {
    //get list of maps and populate the maps select box
    var aMaps = myKaMap.getMaps();
    // Update map selection list if one is available
    var oSelect = document.forms[0].maps;
    if (oSelect)
    {
        var j = 0;
        var opt = new Option( 'select a map', '', true, true );
        oSelect[j++] = opt;
        for(var i in aMaps) {
          oSelect[j++] = new Option(aMaps[i].title,aMaps[i].name,false,false);
        }

        //make sure the map is selected ...
        var oSelect = document.forms[0].maps;
        if (oSelect.options[oSelect.selectedIndex].value != mapName) {
            for(var i = 0; i < oSelect.options.length; i++ ) {
                if (oSelect.options[i].value == mapName) {
                    oSelect.options[i].selected = true;
                    break;
                }
           }
        }
    } 

    //update the scales select
    var currentMap = myKaMap.getCurrentMap();
    var scales = currentMap.getScales();
    var currentScale=myKaMap.getCurrentScale();

    //Insert tools into zoomer div

    var iWidth = 6;//width of the zoom to scale item
    var iMaxHeight = 10;//width of the zoom to scale item
    var iMinHeight = 20;//width of the zoom to scale item
    var zoomer="<span style='width:"+(scales.length*iWidth)+"'>";
    for(var i=0; i<scales.length; i++) {
        var zoomTo = 'mySetScale(' +scales[i]+')';
        //var iHeight =  parseInt(i)*2.5+10;
        var iHeight =  iMaxHeight - parseInt((iMaxHeight - iMinHeight) *i/scales.length);

        var zoomImg = '';
        if (scales[i]==currentScale) {
            zoomImg = '<img src="images/pixel-red.png" width="' + iWidth + '" height="' + iHeight + 'px" border="0" onclick="'+zoomTo+'"  title="Zoom to 1:'+scales[i]+'" alt="Zoom to 1:'+scales[i]+'"  id="img'+scales[i]+'"/>';
        } else {
            zoomImg = '<img src="images/pixel-blue.png" width="' + iWidth + '" height="' + iHeight + 'px" border="0" onclick="'+zoomTo+'"  title="Zoom to 1:'+scales[i]+'" alt="Zoom to 1:'+scales[i]+'" id="img'+scales[i]+'"/>';
        }
        zoomer = zoomer  + zoomImg ;
    }
    zoomer=zoomer+"</span>";
    getRawObject('zoomer').innerHTML = zoomer;
    //Activate query button
    switchMode('toolPan');

	/* handle request for layer visibility */
	var layers = getQueryParam('layers');
	if (layers != '') {
		var map = myKaMap.getCurrentMap();
		//turn off all layers
		var allLayers = map.getAllLayers();
		for (var i=0; i<allLayers.length; i++) {
			allLayers[i].setVisibility(false);
		}
		aLayers = layers.split(',');
		for (var i=0;i<aLayers.length; i++) {
			map.setLayerVisibility (unescape(aLayers[i]), true);
		}
	}
}

/**
 * handle the extents changing by updating a link in the interface that links
 * to the current view
 */
function myExtentChanged( eventID, extents ) {
	updateLinkToView();
}

function myLayersChanged(eventID, map) {
	updateLinkToView();
}

function updateLinkToView()  {
	var url = window.location.protocol+'/'+'/'+window.location.host +':'+window.location.port+'/'+window.location.pathname+'?';
	var extents = myKaMap.getGeoExtents();
	var cx = (extents[2] + extents[0])/2;
	var cy = (extents[3] + extents[1])/2;
	var cpsURL = 'cps='+cx+','+cy+','+myKaMap.getCurrentScale();
	var mapURL = 'map=' + myKaMap.currentMap;
    var theMap = myKaMap.getCurrentMap();
	var aLayers = theMap.getLayers();
	var layersURL = 'layers=';
	var sep = '';
	for (var i=0;i<aLayers.length;i++) {
		layersURL += sep + aLayers[i].name;
		sep = ',';
	}

	var link = document.getElementById('linkToView');
	link.href = url + mapURL + '&' + cpsURL + '&' + layersURL;
}

/**
 * called when kaMap tells us the scale has changed
 */
function myScaleChanged( eventID, scale ) {
    //todo: update scale select and enable/disable zoomin/zoomout
    var currentMap = myKaMap.getCurrentMap();
    var scales = currentMap.getScales();
    for(var i in scales){
        var imgString = 'img'+scales[i];
        var scaleString = 'img'+scale;
        if(getRawObject(imgString)) {
            if(imgString == scaleString) {
                getRawObject(scaleString).src = 'images/pixel-red.png';
            } else {
                getRawObject(imgString).src = 'images/pixel-blue.png';
            }
        }
    }
    myScalebar.update(scale);
    if (scale >= 1000000) {
        scale = scale / 1000000;
        scale = scale + " Million";
    }
    var outString = 'current scale 1:'+ scale;
    getRawObject('scale').innerHTML = outString;
}

/**
 * called when the user changes scales.  This will cause the map to zoom to
 * the new scale and trigger a bunch of events, including:
 * KAMAP_SCALE_CHANGED
 * KAMAP_EXTENTS_CHANGED
 */
function mySetScale( scale ) {
    myKaMap.zoomToScale( scale );
}

/**
 * called when the map selection changes due to the user selecting a new map.
 * By calling myKaMap.selectMap, this triggers the KAMAP_MAP_INITIALIZED event
 * after the new map is initialized which, in turn, causes myMapInitialized
 * to be called
 */
function mySetMap( name ) {
    myKaMap.selectMap( name );
}

function myQuery( eventID, queryType, coords ) {
    var szLayers = '';
    var layers = myKaMap.getCurrentMap().getQueryableLayers();
    if(layers.length==0) {
     alert("No queryable layers at this scale and extent");
     return;
    }
    for (var i=0;i<layers.length;i++) {
        szLayers = szLayers + "," + layers[i].name;
    }


    var extent = myKaMap.getGeoExtents();
    var scale = myKaMap.getCurrentScale();
    var cMap = myKaMap.getCurrentMap().name;
	var params='map='+cMap+'&q_type='+queryType+'&scale='+scale+'&groups='+szLayers+'&coords='+coords+'&extent='+extent[0]+'|'+extent[1]+'|'+extent[2]+'|'+extent[3];

	WOOpenWin( 'Query', 'map_query.php?'+params, 'resizable=yes,scrollbars=yes,width=600,height=400' );

//    alert( "Map: " + cMap + " | Scale: " + scale + " | Extent: " + extent + " | QUERY: " + queryType + " " + coords + " on layers " + szLayers );
}

function myMapClicked( eventID, coords ) {
    //alert( 'myMapClicked('+coords+')');
	//myKaMap.zoomTo(coords[0],coords[1]);
}

function myZoomIn() {
    myKaMap.zoomIn();
}

function myZoomOut() {
    myKaMap.zoomOut();
}

function myPrint() {
    var szLayers = '';
    
    var layers = myKaMap.getCurrentMap().getLayers();
    for (var i=0;i<layers.length;i++) {
        szLayers = szLayers + "," + layers[i].name;
    }
	
    var extent = myKaMap.getGeoExtents();
    var scale = myKaMap.getCurrentScale();
    var cMap = myKaMap.getCurrentMap().name;
    
    var img_width = '600';// pixel dimension. max_img_width set inside print_map.php
    
	var params='map='+cMap+'&scale='+scale+'&img_width='+img_width+'&groups='+szLayers+'&extent='+extent[0]+'|'+extent[1]+'|'+extent[2]+'|'+extent[3];
 
    WOOpenWin( 'Print', 'tools/print/print_map.php?'+params, 'resizable=yes,scrollbars=yes,width=600,height=400' );
    
}


function toggleToolbar(obj) {
    if (obj.style.backgroundImage == '') {
        obj.isOpen = true;
    }

    if (obj.isOpen) {
        obj.title = 'show toolbar';
        obj.style.backgroundImage = 'url(images/arrow_down.png)';
        var bValue = getObjectTop(obj);;
        var d = getObject('toolbar');
        d.display = "none";
        obj.isOpen = false;
        obj.style.top = "3px";
    } else {
        obj.title = 'hide toolbar';
        obj.style.backgroundImage = 'url(images/arrow_up.png)';
        var d = getObject('toolbar');
        d.display="block";
        obj.isOpen = true;
        var h = getObjectHeight('toolbar');
        obj.style.top = (h + 3) + "px";
    }
}

function toggleKeymap(obj) {
    if (obj.style.backgroundImage == '') {
        obj.isOpen = true;
    }

    if (obj.isOpen) {
        obj.title = 'show keymap';
        obj.style.backgroundImage = 'url(images/arrow_left.png)';
        var bValue = getObjectTop(obj);;
        var d = getObject('keymap');
        d.display = "none";
        obj.isOpen = false;
    } else {
        obj.title = 'hide keymap';
        obj.style.backgroundImage = 'url(images/arrow_right.png)';
        var d = getObject('keymap');
        d.display="block";
        obj.isOpen = true;
    }
}

function toggleReference(obj) {
    if (obj.style.backgroundImage == '') {
        obj.isOpen = true;
    }

    if (obj.isOpen) {
        obj.title = 'show reference';
        obj.style.backgroundImage = 'url(images/arrow_up.png)';
        var d = getObject('reference');
        d.display = 'none';
        obj.isOpen = false;
        obj.style.bottom = '3px';
    } else {
        obj.title = 'hide reference';
        obj.style.backgroundImage = 'url(images/arrow_down.png)';
        var d = getObject('reference');
        d.display = 'block';
        obj.isOpen = true;
        obj.style.bottom = (getObjectHeight('reference') + 3) + 'px';
    }
}

function dialogToggle( href, szObj) {
    var obj = getObject(szObj);
    if (obj.display == 'none') {
        obj.display = 'block';
        href.childNodes[0].src = 'images/dialog_shut.png';
    } else {
        obj.display = 'none';
        href.childNodes[0].src = 'images/dialog_open.png';
    }
}

/**
 * drawPage - calculate sizes of the various divs to make the app full screen.
 */
function drawPage() {
    var browserWidth = getInsideWindowWidth();
    var browserHeight = getInsideWindowHeight();

    var viewport = getRawObject('viewport');

    //Set Viewport Width
    if(myKaMap.isIE4) {
        //terrible hack to avoid IE to show scrollbar
        viewport.style.width = (browserWidth -2) + "px";
    } else {
        viewport.style.width = browserWidth + "px";
    }

    //Set Viewport Height
    if(myKaMap.isIE4) {
        //terrible hack to avoid IE to show scrollbar
        viewport.style.height = (browserHeight -2) + "px";
    } else {
        viewport.style.height = browserHeight + "px";
    }

    myKaMap.resize();
}

/**
 * getFullExtent
 * ...
 */
function getFullExtent() {
    var exStr = myKaMap.getCurrentMap().defaultExtents.toString();
    var ex = myKaMap.getCurrentMap().defaultExtents;
    myKaMap.zoomToExtents(ex[0],ex[1],ex[2],ex[3]);
}

/**
 * switchMode
 * ...
 */
function switchMode(id) {
    if (id=='toolQuery') {
        myKaQuery.activate();
        getRawObject('toolQuery').style.backgroundImage = 'url(images/icon_set_nomad/tool_query_2.png)';
        getRawObject('toolPan').style.backgroundImage = 'url(images/icon_set_nomad/tool_pan_1.png)';
        getRawObject('toolZoomRubber').style.backgroundImage = 'url(images/icon_set_nomad/tool_rubberzoom_1.png)';
    } else if (id=='toolPan') {
        myKaNavigator.activate();
        getRawObject('toolQuery').style.backgroundImage = 'url(images/icon_set_nomad/tool_query_1.png)';
        getRawObject('toolPan').style.backgroundImage = 'url(images/icon_set_nomad/tool_pan_2.png)';
        getRawObject('toolZoomRubber').style.backgroundImage = 'url(images/icon_set_nomad/tool_rubberzoom_1.png)';
    } else if (id=='toolZoomRubber') {
        myKaRubberZoom.activate();
        getRawObject('toolQuery').style.backgroundImage = 'url(images/icon_set_nomad/tool_query_1.png)';
        getRawObject('toolPan').style.backgroundImage = 'url(images/icon_set_nomad/tool_pan_1.png)';
        getRawObject('toolZoomRubber').style.backgroundImage = 'url(images/icon_set_nomad/tool_rubberzoom_2.png)';
    } else {
        myKaNavigator.activate();
    }
}

/*
 *  applyPNGFilter(o)
 *
 *  Applies the PNG Filter Hack for IE browsers when showing 24bit PNG's
 *
 *  var o = object (this png element in the page)
 *
 * The filter is applied using a nifty feature of IE that allows javascript to
 * be executed as part of a CSS style rule - this ensures that the hack only
 * gets applied on IE browsers :)
 */
function applyPNGFilter(o) {
    var t="images/a_pixel.gif";
    if( o.src != t ) {
        var s=o.src;
        o.src = t;
        o.runtimeStyle.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='"+s+"',sizingMethod='scale')";
    }
}

//functions to open popup

function WOFocusWin( nn ) {
	eval( "if( this."+name+") this."+name+".moveTo(50,50); this."+name+".focus();" );
}

function WOOpenWin( name, url, ctrl ) {
    eval( "this."+name+"=window.open('"+url+"','"+name+"','"+ctrl+"');" );

    /*IE needs a delay to move forward the popup*/
    // window.setTimeout( "WOFocusWin(nome);", 300 );
}

function WinOpener() {
    this.openWin=WOOpenWin;
	this.focusWin=WOFocusWin;
}
function toggleSearch(obj) {
    if (obj.style.backgroundImage == '') {
        obj.isOpen = true;
    }

    if (obj.isOpen) {
        obj.title = 'show search results';
        obj.style.backgroundImage = 'url(images/arrow_up.png)';
        var d = getObject('searchOut');
        d.display = 'none';
        obj.isOpen = false;
        obj.style.bottom = '3px';
    } else {
        obj.title = 'hide  search results';
        obj.style.backgroundImage = 'url(images/arrow_down.png)';
        var d = getObject('searchOut');
        d.display = 'block';
        obj.isOpen = true;
        obj.style.bottom = (getObjectHeight('searchOut') + 3) + 'px';
    }
}
