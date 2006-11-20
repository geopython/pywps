/**********************************************************************
 *
 * $Id: kaMap.js,v 1.98 2006/09/05 14:03:28 pspencer Exp $
 *
 * purpose: core engine for implementing a tiled, continuous pan mapping
 *          engine.
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original kaMap code was written by DM Solutions Group.
 * bug fixes contributed by Lorenzo Becchi and Andrea Cappugi
 * max_extents support by Tim Schaub
 *
 * TODO:
 *
 *   - convert to prototype
 *   - code refactoring for simplification/speed
 *   - code refactoring
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

/**
 * kaMap! events
 */
var gnLastEventId = 0;
var KAMAP_ERROR = gnLastEventId ++;
var KAMAP_WARNING = gnLastEventId ++;
var KAMAP_NOTICE = gnLastEventId++;
var KAMAP_INITIALIZED = gnLastEventId ++;
var KAMAP_MAP_INITIALIZED = gnLastEventId ++;
var KAMAP_EXTENTS_CHANGED = gnLastEventId ++;
var KAMAP_SCALE_CHANGED = gnLastEventId ++;
var KAMAP_LAYERS_CHANGED = gnLastEventId ++;
var KAMAP_LAYER_STATUS_CHANGED = gnLastEventId ++;
var KAMAP_CONTEXT_MENU = gnLastEventId ++;
var KAMAP_METAEXTENTS_CHANGED = gnLastEventId++;
var KAMAP_MAP_CLICKED = gnLastEventId++;

/******************************************************************************
 * kaMap main class
 *
 * construct a new kaMap instance.  Pass the id of the div to put the kaMap in
 *
 * this class is the main API for any application.  Only use the functions
 * provided by this API to ensure everything functions correctly
 *
 * szID - string, the id of a div to put the kaMap! into
 *
 *****************************************************************************/
function kaMap( szID ) {
    this.isCSS = false;
    this.isW3C = false;
    this.isIE4 = false;
    this.isNN4 = false;
    this.isIE6CSS = false;

    if (document.images) {
        this.isCSS = (document.body && document.body.style) ? true : false;
        this.isW3C = (this.isCSS && document.getElementById) ? true : false;
        this.isIE4 = (this.isCSS && document.all) ? true : false;
        this.isNN4 = (document.layers) ? true : false;
        this.isIE6CSS = (document.compatMode && document.compatMode.indexOf("CSS1") >= 0) ? true : false;
    }

    this.domObj = this.getRawObject( szID );
    this.domObj.style.overflow = 'hidden';

    this.hideLayersOnMove = false;
    //if true layer not checked are loaded if false aren't loaded
    this.loadUnchecked=false;
    /**
     * initialization states
     * 0 - not initialized
     * 1 - initializing
     * 2 - initialized
     */
    this.initializationState = 0;

    //track mouse down events
    this.bMouseDown = false;

    //track last recorded mouse position
    this.lastx = 0;
    this.lasty = 0;

    //keep a reference to the inside layer since we use it a lot
    this.theInsideLayer = null;

    //viewport width and height are used in many calculations
    this.viewportWidth = this.getObjectWidth(this.domObj);
    this.viewportHeight = this.getObjectHeight(this.domObj);

    //track amount the inside layer has moved to help in wrapping images
    this.xOffset = 0;
    this.yOffset = 0;

    //track current origin offset value
    this.xOrigin = 0;
    this.yOrigin = 0;

    //the name of the current map
    this.currentMap = '';

    //the current width and height in tiles
    this.nWide = 0;
    this.nHigh = 0;

    //current top and left are tracked when the map moves
    //to start the map at some offset, these would be set to
    //the appropriate pixel value.
    this.nCurrentTop = 0; //null;
    this.nCurrentLeft = 0; //null;

    //keep a live reference to aPixel to help with caching problems - hish
    this.aPixel = new Image(1,1);
    this.aPixel.src = 'images/a_pixel.gif';

    //error stack for tracking images that have failed to load
    this.imgErrors = new Array();

    //an array of available maps
    this.aMaps = new Array();

    //tile size and buffer size determine how many tiles to create
    this.tileWidth = null;
    this.tileHeight = null;
    this.nBuffer = 1;

    this.baseURL = '';

    //size of a pixel, geographically - assumed to be square
    this.cellSize = null;

    //image id counter - helps with reloading failed images
    this.gImageID = 0;

    //event manager
    this.eventManager = new _eventManager();

    //slider stuff
    this.as=slideid=null;
    this.accelerationFactor=1;
    this.pixelsPerStep = 30;
    this.timePerStep = 25;

    //this is a convenience to allow redirecting the client code to a server
    //other than the one that this file was loaded from.  This may not
    //work depending on security settings, except for loading tiles since
    //those come directly from a php script instead of an XmlHttpRequest.
    //
    //by default, if this is empty, it loads from the same site as the
    //page loaded from.  If set, it should be a full http:// reference to the
    //directory in which init.php, tile.php and the other scripts are located.
    this.server = '';

    //similarly, this is the global initialization script called once per page
    //load ... the result of this script tell the client what other scripts
    //are used for the other functions
    this.init = "../../ka-map/htdocs/init.php";

    //these are the values that need to be initialized by the init script
    this.tileURL = null;

    this.aObjects = [];
    this.aCanvases = [];
    this.layersHidden = false;

    this.aTools = [];
    this.aInfoTools = [];

    /* register the known events */
    for (var i=0; i<gnLastEventId; i++) {
        this.registerEventID( i );
    }
    this.createLayers();
};

kaMap.prototype.seekLayer = function(doc, name) {
    var theObj;
    for (var i = 0; i < doc.layers.length; i++) {
        if (doc.layers[i].name == name) {
            theObj = doc.layers[i];
            break;
        }
        // dive into nested layers if necessary
        if (doc.layers[i].document.layers.length > 0) {
            theObj = this.seekLayer(document.layers[i].document, name);
        }
    }
    return theObj;
};

// Convert object name string or object reference
// into a valid element object reference
kaMap.prototype.getRawObject = function(obj) {
    var theObj;
    if (typeof obj == "string") {
        if (this.isW3C) {
            theObj = document.getElementById(obj);
        } else if (this.isIE4) {
            theObj = document.all(obj);
        } else if (this.isNN4) {
            theObj = seekLayer(document, obj);
        }
    } else {
        // pass through object reference
        theObj = obj;
    }
    return theObj;
};

// Convert object name string or object reference
// into a valid style (or NN4 layer) reference
kaMap.prototype.getObject = function(obj) {
    var theObj = this.getRawObject(obj);
    if (theObj && this.isCSS) {
        theObj = theObj.style;
    }
    return theObj;
};

// Retrieve the rendered width of an element
kaMap.prototype.getObjectWidth = function(obj)  {
    var elem = this.getRawObject(obj);
    var result = 0;
    if (elem.offsetWidth) {
        result = elem.offsetWidth;
    } else if (elem.clip && elem.clip.width) {
        result = elem.clip.width;
    } else if (elem.style && elem.style.pixelWidth) {
        result = elem.style.pixelWidth;
    }
    return parseInt(result);
};

// Retrieve the rendered height of an element
kaMap.prototype.getObjectHeight = function(obj)  {
    var elem = this.getRawObject(obj);
    var result = 0;
    if (elem.offsetHeight) {
        result = elem.offsetHeight;
    } else if (elem.clip && elem.clip.height) {
        result = elem.clip.height;
    } else if (elem.style && elem.style.pixelHeight) {
        result = elem.style.pixelHeight;
    }
    return parseInt(result);
};

/**
 * kaMap.zoomTo( lon, lat [, scale] )
 *
 * zoom to some geographic point (in current projection) and optionally scale
 *
 * lon - the x coordinate to zoom to
 * lat - the y coordinate to zoom to
 * scale - optional. The scale to use
 */
kaMap.prototype.zoomTo = function( cgX, cgY ) {
    var oMap = this.getCurrentMap();
    var inchesPerUnit = new Array(1, 12, 63360.0, 39.3701, 39370.1, 4374754);
    var newScale;
    var bScaleChanged = false;
    if (arguments.length == 3) {
        newScale = arguments[2];
        bScaleChanged = (newScale != this.getCurrentScale())
    } else {
        newScale = this.getCurrentScale();
    }
	var bZoomTo = true;
	if (!bScaleChanged) {
		var extents = this.getGeoExtents();
      	if (cgX >= extents[0] && cgX <= extents[2] &&
          	cgY >= extents[1] && cgY <= extents[3]) {
        	var cx = (extents[0]+extents[2])/2;
	        var cy = (extents[1]+extents[3])/2;
	        var dx = (cx - cgX)/this.cellSize;
	        var dy = (cgY - cy)/this.cellSize;
	        this.slideBy(dx,dy);
			bZoomTo = false;
      	}
	}
	if (bZoomTo) {
	    this.cellSize = newScale/(oMap.resolution * inchesPerUnit[oMap.units]);
	    var nFactor = oMap.zoomToScale( newScale );
	    this.setMapLayers();
	    var cpX = cgX / this.cellSize;
	    var cpY = cgY / this.cellSize;

	    var vpLeft = Math.round(cpX - this.viewportWidth/2);
	    var vpTop = Math.round(cpY + this.viewportHeight/2);


	    //figure out which tile the center point lies on
	    var cTileX = Math.floor(cpX/this.tileWidth)*this.tileWidth;
	    var cTileY = Math.floor(cpY/this.tileHeight)*this.tileHeight;


	    //figure out how many tiles left and up we need to move to lay out from
	    //the top left and have the top/left image off screen (or partially)
	    var nTilesLeft = Math.ceil(this.viewportWidth/(2*this.tileWidth))*this.tileWidth;
	    var nTilesUp = Math.ceil(this.viewportHeight/(2*this.tileHeight))*this.tileHeight;

	    this.nCurrentLeft = cTileX - nTilesLeft;
	    this.nCurrentTop = -1*(cTileY + nTilesUp);

	    this.xOrigin = this.nCurrentLeft;
	    this.yOrigin = this.nCurrentTop;

	    this.theInsideLayer.style.left = -1*(vpLeft - this.xOrigin) + "px";
	    this.theInsideLayer.style.top = (vpTop + this.yOrigin) + "px";

	    var layers = oMap.getLayers();
	    for( var k=0; k<layers.length; k++) {
	        var d = layers[k].domObj;
	        for(var j=0; j<this.nHigh; j++) {
	            for( var i=0; i<this.nWide; i++) {
	                var img = d.childNodes[(j*this.nWide)+i];
	                img.src = this.aPixel.src;
	                img.style.top = (this.nCurrentTop + j*this.tileHeight - this.yOrigin) + "px";
	                img.style.left = (this.nCurrentLeft + i*this.tileWidth - this.xOrigin) + "px";
	                layers[k].setTile(img);
	            }
	        }
	    }
	    this.checkWrap( );
	    this.updateObjects();
	}
    if (bScaleChanged) {
		this.triggerEvent( KAMAP_SCALE_CHANGED, this.getCurrentScale() );
	}
    this.triggerEvent( KAMAP_EXTENTS_CHANGED, this.getGeoExtents() );
};

/**
 * kaMap.zoomToExtents( minx, miny, maxx, maxy )
 *
 * best fit zoom to extents.  Center of extents will be in the center of the
 * view and the extents will be contained within the view at the closest scale
 * available above the scale these extents represent
 *
 * minx, miny, maxx, maxy - extents in units of current projection.
 */
kaMap.prototype.zoomToExtents = function(minx, miny, maxx, maxy) {
    /* calculate new scale from extents and viewport, then find closest
     * scale and calculate new extents from centerpoint and scale.  Then
     * move theInsideLayer and all the images to show that centerpoint at
     * the center of the view at the given scale
     */
    var inchesPerUnit = new Array(1, 12, 63360.0, 39.3701, 39370.1, 4374754);
    var oMap = this.getCurrentMap();

    //the geographic center - where we want to end up
    var cgX = (maxx+minx)/2;
    var cgY = (maxy+miny)/2;

    var tmpCellSizeX = (maxx - minx)/this.viewportWidth;
    var tmpCellSizeY = (maxy - miny)/this.viewportHeight;
    var tmpCellSize = Math.max( tmpCellSizeX, tmpCellSizeY );

    var tmpScale = tmpCellSize * oMap.resolution * inchesPerUnit[oMap.units];
    var newScale = oMap.aScales[0];
    for (var i=1; i<oMap.aScales.length; i++) {
        if (tmpScale >= oMap.aScales[i]) {
            break;
        }
        newScale = oMap.aScales[i];
    }
    //now newScale has our new scale size
    this.cellSize = newScale/(oMap.resolution * inchesPerUnit[oMap.units]);
    var nFactor = oMap.zoomToScale( newScale );
    this.setMapLayers();
    var cpX = cgX / this.cellSize;
    var cpY = cgY / this.cellSize;

    var vpLeft = Math.round(cpX - this.viewportWidth/2);
    var vpTop = Math.round(cpY + this.viewportHeight/2);


    //figure out which tile the center point lies on
    var cTileX = Math.floor(cpX/this.tileWidth)*this.tileWidth;
    var cTileY = Math.floor(cpY/this.tileHeight)*this.tileHeight;


    //figure out how many tiles left and up we need to move to lay out from
    //the top left and have the top/left image off screen (or partially)
    var nTilesLeft = Math.ceil(this.viewportWidth/(2*this.tileWidth))*this.tileWidth;
    var nTilesUp = Math.ceil(this.viewportHeight/(2*this.tileHeight))*this.tileHeight;

    this.nCurrentLeft = cTileX - nTilesLeft;
    this.nCurrentTop = -1*(cTileY + nTilesUp);

    this.xOrigin = this.nCurrentLeft;
    this.yOrigin = this.nCurrentTop;

    this.theInsideLayer.style.left = -1*(vpLeft - this.xOrigin) + "px";
    this.theInsideLayer.style.top = (vpTop + this.yOrigin) + "px";

    var layers = oMap.getLayers();
    for( var k=0; k<layers.length; k++) {
        var d = layers[k].domObj;
        for(var j=0; j<this.nHigh; j++) {
            for( var i=0; i<this.nWide; i++) {
                var img = d.childNodes[(j*this.nWide)+i];
                img.src = this.aPixel.src;
                img.style.top = (this.nCurrentTop + j*this.tileHeight - this.yOrigin) + "px";
                img.style.left = (this.nCurrentLeft + i*this.tileWidth - this.xOrigin) + "px";
                layers[k].setTile(img);
            }
        }
    }
    this.checkWrap( );
    this.updateObjects();
    this.triggerEvent( KAMAP_SCALE_CHANGED, this.getCurrentScale() );
    this.triggerEvent( KAMAP_EXTENTS_CHANGED, this.getGeoExtents() );
};

/**
 * kaMap.createDrawingCanvas( idx )
 *
 * create a layer on which objects can be drawn (such as point objects)
 *
 * idx - int, the z-index of the layer.  Should be < 100 but above the map
 * layers.
 */
kaMap.prototype.createDrawingCanvas = function( idx ) {
    var d = document.createElement( 'div' );
    d.style.position = 'absolute';
    d.style.left = '0px';
    d.style.top = '0px';
    d.style.width= '3000px';
    d.style.height = '3000px';
    d.style.zIndex = idx;
    this.theInsideLayer.appendChild( d );
    this.aCanvases.push( d );
    d.kaMap = this;
    return d;
};

kaMap.prototype.removeDrawingCanvas = function( canvas ) {

    for (var i=0; i<this.aCanvases.length;i++) {
        if (this.aCanvases[i] == canvas) {
            this.aCanvases.splice( i, 1 );
        }
    }
    this.theInsideLayer.removeChild(canvas);
    canvas.kaMap = null;
    return true;
};

/**
 * kaMap.addObjectGeo( canvas, lon, lat, obj )
 *
 * add an object to a drawing layer and position it at the given geographic
 * position.  This is defined as being in the projection of the map.
 *
 * TODO: possibly add ability to call a reprojection service (xhr request?) to
 * convert lon/lat into the current coordinate system if not lon/lat.
 *
 * canvas - object, the drawing canvas to add this object to
 * x - int, the x position in pixels
 * y - int, the y position in pixels
 * obj - object, the object to add (an img, div etc)
 *
 * returns true
 */
kaMap.prototype.addObjectGeo = function( canvas, lon, lat, obj ) {
    obj.lon = lon;
    obj.lat = lat;
    var aPix = this.geoToPix( lon, lat );
    return this.addObjectPix( canvas, aPix[0], aPix[1], obj );
};

/**
 * kaMap.addObjectPix( canvas, x, y, obj )
 *
 * add an object to the map canvas and position it at the given pixel position.
 * The position should not include the xOrigin/yOrigin offsets
 *
 * canvas - object, the canvas to add this object to
 * x - int, the x position in pixels
 * y - int, the y position in pixels
 * obj - object, the object to add (an img, div etc)
 *
 * returns true;
 */
kaMap.prototype.addObjectPix = function( canvas, x, y, obj ) {
    var xOffset = (obj.xOffset) ? obj.xOffset : 0;
    var yOffset = (obj.yOffset) ? obj.yOffset : 0;
    var top = (y - this.yOrigin + yOffset);
    var left = (x - this.xOrigin + xOffset);
    obj.style.position = 'absolute';
    obj.style.top = top + "px";
    obj.style.left = left + "px";
    obj.canvas = canvas;
    canvas.appendChild( obj );
    this.aObjects.push( obj );

    return true;
};

/**
 * kaMap.shiftObject( x, y, obj )
 *
 * move an object by a pixel amount
 *
 * x - int, the number of pixels in the x direction to move the object
 * y - int, the number of pixels in the y direction to move the object
 * obj - object, the object to move
 *
 * returns true
 */
kaMap.prototype.shiftObject = function( x, y, obj ) {
    var top = safeParseInt(obj.style.top);
    var left = safeParseInt(obj.style.left);

    obj.style.top = (top + y) + "px";
    obj.style.left = (left + x) + "px";

    return true;
};

/**
 * kaMap.removeObject( obj )
 *
 * removes an object previously added with one of the addObjectXxx calls
 *
 * obj - object, an object that has been previously added, or null to remove
 *       all objects
 *
 * returns true if the object was removed, false otherwise (i.e. if it was
 * never added).
 */
kaMap.prototype.removeObject = function( obj ) {
    if (obj == null) {
        for (var i=0; i<this.aObjects.length; i++) {
            obj = this.aObjects[i];
            if (obj.canvas) {
                obj.canvas.removeChild(obj);
            }
        }
        this.aObjects = [];
        return true;
    } else {
        for (var i=0; i<this.aObjects.length; i++) {
            if (this.aObjects[i] == obj) {
                obj = this.aObjects[i];
                if (obj.canvas) {
                    obj.canvas.removeChild( obj );
                    obj.canvas = null;
                }
                this.aObjects.splice(i,1);
                return true;
            }
        }
        return false;
    }
};

/**
 * kaMap.removeAllObjects( canvas )
 *
 * removes all objects on a particular canvas
 *
 * canvas - a canvas that was previously created with createDrawingCanvas
 */
kaMap.prototype.removeAllObjects = function(canvas) {
    for (var i=0; i<this.aObjects.length; i++) {
       obj = this.aObjects[i];
       if (obj.canvas && obj.canvas == canvas) {
          obj.canvas.removeChild( obj );
          obj.canvas = null;
          this.aObjects.splice(i--,1);
       }
    }
    return true;
};

/**
 * kaMap.centerObject( obj )
 *
 * slides the map to place the object at the center of the map
 *
 * obj - object, an object previously added to the map
 *
 * returns true
 */
kaMap.prototype.centerObject = function(obj) {
    var vpX = -safeParseInt(this.theInsideLayer.style.left) + this.viewportWidth/2;
    var vpY = -safeParseInt(this.theInsideLayer.style.top) + this.viewportHeight/2;

    var xOffset = (obj.xOffset)?obj.xOffset:0;
    var yOffset = (obj.yOffset)?obj.yOffset:0;

    var dx = safeParseInt(obj.style.left) - xOffset- vpX;
    var dy = safeParseInt(obj.style.top) - yOffset - vpY;

    this.slideBy(-dx, -dy);
    return true;
};

/**
 * kaMap.geoToPix( gX, gY )
 *
 * convert geographic coordinates into pixel coordinates.  Note this does not
 * adjust for the current origin offset that is used to adjust the actual
 * pixel location of the tiles and other images
 *
 * gX - float, the x coordinate in geographic units of the active projection
 * gY - float, the y coordinate in geographic units of the active projection
 *
 * returns an array of pixel coordinates with element 0 being the x and element
 * 1 being the y coordinate.
 */
kaMap.prototype.geoToPix = function( gX, gY ) {
    var pX = gX / this.cellSize;
    var pY = -1 * gY / this.cellSize;
    return [Math.floor(pX), Math.floor(pY)];
};

/**
 * kaMap.pixToGeo( pX, pY [, bAdjust] )
 *
 * convert pixel coordinates into geographic coordinates.  This can optionally
 * adjust for the pixel offset by passing true as the third argument
 *
 * pX - int, the x coordinate in pixel units
 * pY - int, the y coordinate in pixel units
 *
 * returns an array of geographic coordinates with element 0 being the x
 * and element 1 being the y coordinate.
 */
kaMap.prototype.pixToGeo = function( pX, pY ) {
    var bAdjust = (arguments.length == 3 && arguments[2]) ? true : false;

    if (bAdjust) {
        pX = pX + this.xOrigin;
        pY = pY + this.yOrigin;
    }
    var gX = -1 * pX * this.cellSize;
    var gY = pY * this.cellSize;
    return [gX, gY];
};

/**
 * kaMap.initialize( [szMap] )
 *
 * main initialization of kaMap.  This must be called after page load and
 * should only be called once (i.e. on page load).  It does not perform
 * intialization synchronously.  This means that the function will return
 * before initialization is complete.  To determine when initialization is
 * complete, the calling application must register for the KAMAP_INITIALIZED
 * event.
 *
 * szMap - string, optional, the name of a map to initialize by default.  If
 *         not set, use the default configuration map file.
 *
 * returns true
 */
kaMap.prototype.initialize = function() {
    if (this.initializationState == 2) {
        this.triggerEvent( KAMAP_ERROR, 'ERROR: ka-Map! is already initialized!' );
        return false;
    } else if (this.intializationState == 1) {
        this.triggerEvent( KAMAP_WARNING, 'WARNING: ka-Map! is currently initializing ... wait for the KAMAP_INITIALIZED event to be triggered.' );
        return false;
    }

    this.initializationState = 1;
    /* call initialization script on the server */
    var szURL = this.server+this.init;

    var sep = (this.init.indexOf("?") == -1) ? "?" : "&";

    if (arguments.length > 0 && arguments[0] != '') {
        szURL = szURL + sep + "map="+ arguments[0];
        sep = "&";
    }
    if (arguments.length > 1 && arguments[1] != '') {
        szURL = szURL + sep + "extents="+ arguments[1];
        sep = "&";
    }
    if (arguments.length > 2 && arguments[2] != '') {
        szURL = szURL + sep + "centerPoint="+ arguments[2];
        sep = "&";
    }
    call(szURL, this, this.initializeCallback);
    return true;
};

/**
 * hidden function on callback from init.php
 */
kaMap.prototype.initializeCallback = function( szInit ) {
    // szInit contains /*init*/ if it worked, or some php error otherwise
    if (szInit.substr(0, 1) != "/") {
        this.triggerEvent( KAMAP_ERROR, 'ERROR: ka-Map! initialization '+
                          'failed on the server.  Message returned was:\n' +
                          szInit);
        return false;
    }

    eval(szInit);

    this.triggerEvent( KAMAP_INITIALIZED );

    this.initializationState = 2;
};

/**
 * kaMap.setBackgroundColor( color )
 *
 * call this to set a background color for the inside layer.  This color
 * shows through any transparent areas of the map.  This is primarily
 * intended to be used by the initializeMap callback function to set the
 * background to the background color in the map file.
 *
 * color: string, a valid HTML color string
 *
 * returns true;
 */
kaMap.prototype.setBackgroundColor = function( color ) {
    this.domObj.style.backgroundColor = color;
    return true;
};

/**
 * hidden method of kaMap to initialize all the various layers needed by
 * kaMap to draw and move the map image.
 */
kaMap.prototype.createLayers = function() {
    this.theInsideLayer = document.createElement('div');
    this.theInsideLayer.id = 'theInsideLayer';
    this.theInsideLayer.style.position = 'absolute';
    this.theInsideLayer.style.left = '0px';
    this.theInsideLayer.style.top = '0px';
    this.theInsideLayer.style.zIndex = '1';
    this.theInsideLayer.kaMap = this;
    if (this.currentTool) {
        this.theInsideLayer.style.cursor = this.currentTool.cursor;
    }
    this.domObj.appendChild(this.theInsideLayer);

    this.domObj.kaMap = this;
    this.theInsideLayer.onmousedown = kaMap_onmousedown;
    this.theInsideLayer.onmouseup = kaMap_onmouseup;
    this.theInsideLayer.onmousemove = kaMap_onmousemove;
    this.theInsideLayer.onmouseover = kaMap_onmouseover;
    this.domObj.onmouseout = kaMap_onmouseout;
    this.theInsideLayer.onkeypress = kaMap_onkeypress;
    this.theInsideLayer.ondblclick = kaMap_ondblclick;
    this.theInsideLayer.oncontextmenu = kaMap_oncontextmenu;
    this.theInsideLayer.onmousewheel = kaMap_onmousewheel;
    if (window.addEventListener &&
        navigator.product && navigator.product == "Gecko") {
        this.domObj.addEventListener( "DOMMouseScroll", kaMap_onmousewheel, false );
    }

    //this is to prevent problems in IE
    this.theInsideLayer.ondragstart = new Function([], 'var e=e?e:event;e.cancelBubble=true;e.returnValue=false;return false;');
};

/**
 * internal function
 * update the layer URLs based on their current positions
 */
kaMap.prototype.initializeLayers = function(nFactor) {
    var deltaMouseX = this.nCurrentLeft + safeParseInt(this.theInsideLayer.style.left) - this.xOrigin;
    var deltaMouseY = this.nCurrentTop + safeParseInt(this.theInsideLayer.style.top) - this.yOrigin;

    var vpTop = this.nCurrentTop - deltaMouseY;
    var vpLeft = this.nCurrentLeft - deltaMouseX;

    var vpCenterX = vpLeft + this.viewportWidth/2;
    var vpCenterY = vpTop + this.viewportHeight/2;

    var currentTileX = Math.floor(vpCenterX/this.tileWidth)*this.tileWidth;
    var currentTileY = Math.floor(vpCenterY/this.tileHeight)*this.tileHeight;

    var tileDeltaX = currentTileX - this.nCurrentLeft;
    var tileDeltaY = currentTileY - this.nCurrentTop;

    var newVpCenterX = vpCenterX * nFactor;
    var newVpCenterY = vpCenterY * nFactor;

    var newTileX = Math.floor(newVpCenterX/this.tileWidth) * this.tileWidth;
    var newTileY = Math.floor(newVpCenterY/this.tileHeight) * this.tileHeight;

    var newCurrentLeft = newTileX - tileDeltaX;
    var newCurrentTop = newTileY - tileDeltaY;

    this.nCurrentLeft = newCurrentLeft;
    this.nCurrentTop = newCurrentTop;

    var newTilLeft = -newVpCenterX + this.viewportWidth/2;
    var newTilTop = -newVpCenterY + this.viewportHeight/2;

    var xOldOrigin = this.xOrigin;
    var yOldOrigin = this.yOrigin;

    this.xOrigin = this.nCurrentLeft;
    this.yOrigin = this.nCurrentTop;

    this.theInsideLayer.style.left = (newTilLeft + this.xOrigin) + "px";
    this.theInsideLayer.style.top = (newTilTop + this.yOrigin) + "px";

    var layers = this.aMaps[this.currentMap].getLayers();
    for( var k=0; k<layers.length; k++) {
        var d = layers[k].domObj;
        for(var j=0; j<this.nHigh; j++) {
            for( var i=0; i<this.nWide; i++) {
                var img = d.childNodes[(j*this.nWide)+i];
                img.src = this.aPixel.src;
                img.style.top = (this.nCurrentTop + j*this.tileHeight - this.yOrigin) + "px";
                img.style.left = (this.nCurrentLeft + i*this.tileWidth - this.xOrigin) + "px";
                layers[k].setTile(img);
            }
        }
    }
    this.checkWrap();
    this.updateObjects();
};

/***************************************
 * internal function adedd by cappu
 * use to paint a layer calculating tile
 * position for current exten and scale
 * and calling the layer.seTile
 ***************************************/
kaMap.prototype.paintLayer = function(l) {
     var d = l.domObj;
     for(var j=0; j<this.nHigh; j++) {
         for( var i=0; i<this.nWide; i++) {
             var img = d.childNodes[(j*this.nWide)+i];
            // img.src = this.aPixel.src;
             img.style.top = (this.nCurrentTop + j*this.tileHeight - this.yOrigin) + "px";
             img.style.left = (this.nCurrentLeft + i*this.tileWidth - this.xOrigin) + "px";
             l.setTile(img);
         }
     }
     this.checkWrap();
};

/* kaMap.updateObjects
 * call this after any major change to the state of kaMap including after
 * a zoomTo, zoomToExtents, etc.
 */
kaMap.prototype.updateObjects = function() {
    for (var i=0; i<this.aObjects.length;i++) {
        var obj = this.aObjects[i];
        var xOffset = (obj.xOffset) ? obj.xOffset : 0;
        var yOffset = (obj.yOffset) ? obj.yOffset : 0;
        var aPix = this.geoToPix( obj.lon, obj.lat );
        var top = (aPix[1] - this.yOrigin + yOffset);
        var left = (aPix[0] - this.xOrigin + xOffset);
        obj.style.top = top + "px";
        obj.style.left = left + "px";
    }
};

/**
 * kaMap.resize()
 *
 * called when the viewport layer changes size.  It is the responsibility
 * of the user of this API to track changes in viewport size and call this
 * function to update the map
 */
kaMap.prototype.resize = function( ) {
    if (this.initializationState != 2) {
        return false;
    }
    var newViewportWidth = this.getObjectWidth(this.domObj);
    var newViewportHeight = this.getObjectHeight(this.domObj);

    if (this.viewportWidth == null) {
        this.theInsideLayer.style.top = (-1*this.nCurrentTop + this.yOrigin) + "px";
        this.theInsideLayer.style.left = (-1*this.nCurrentLeft + this.xOrigin) + "px";
        this.viewportWidth = newViewportWidth;
        this.viewportHeight = newViewportHeight;
    }
    var newWide = Math.ceil((newViewportWidth / this.tileWidth) + 2*this.nBuffer);
    var newHigh = Math.ceil((newViewportHeight / this.tileHeight) + 2*this.nBuffer);

    this.viewportWidth = newViewportWidth;
    this.viewportHeight = newViewportHeight;

    if (this.nHigh == 0 && this.nWide == 0) {
        this.nWide = newWide;
    }

    while (this.nHigh < newHigh) {

        this.appendRow();
    }
    while (this.nHigh > newHigh && newHigh > 3) {
        this.removeRow();
    }
    while (this.nWide < newWide) {
        this.appendColumn();
    }
    while (this.nWide > newWide && newWide > 3) {
        this.removeColumn();
    }
    //create image don't call layer.set tile so i need to do that!
    var map = this.getCurrentMap();
    var layers =map.getLayers();
    for(i=0;i<layers.length;i++) {
        layers[i].setTileLayer();
    }

    this.triggerEvent( KAMAP_EXTENTS_CHANGED, this.getGeoExtents() );
    this.triggerEvent( KAMAP_EXTENTS_CHANGED, this.getGeoExtents() );
};

/**
 * internal function to create images for map tiles
 *
 * top - integer, the top of this image in pixels
 * left - integer, the left of this image in pixels
 * obj - object, the layer in which this image will reside
 */
kaMap.prototype.createImage = function( top, left, obj ) {
    var img = document.createElement('img');
    img.src=this.aPixel.src;
    img.width=this.tileWidth;
    img.height=this.tileHeight;
    //first for firefox, rest for IE :(
    img.setAttribute('style', 'position:absolute; top:'+top+'px; left:'+left+'px;' );
    img.style.position = 'absolute';
    img.style.top = (top - this.yOrigin)+'px';
    img.style.left = (left - this.xOrigin)+'px';
    img.style.width = this.tileWidth + "px";
    img.style.height = this.tileHeight + "px";
    img.style.visibility = 'hidden';
    img.galleryimg = "no"; //turn off image toolbar in IE
    img.onerror = kaMap_imgOnError;
    img.onload = kaMap_imgOnLoad;
    img.errorCount = 0;
    img.id = "i" + this.gImageID;
    img.layer = obj;
    img.kaMap = this;
    this.gImageID = this.gImageID + 1;
    img.ie_hack = false;

    if (this.isIE4) {
    	if (obj.imageformat &&
    	       (obj.imageformat.toLowerCase() == "alpha")) {
		img.ie_hack = true;
	}
    }

    return img;
};

kaMap.prototype.resetTile = function( id, bForce ) {
    var img = this.DHTMLapi.getRawObject(id);
    if (img.layer) {
        img.layer.setTile(this, bForce);
    }
};

kaMap.prototype.reloadImage = function(id) {
};

kaMap.prototype.resetImage = function(id) {
};

/**
 * internal function to handle images that fail to load
 */
kaMap_imgOnError = function(e) {
    if (this.layer) {
        this.layer.setTile(this, true);
    }
};

/**
 * internal function to track images as they finish loading.
 */
kaMap_imgOnLoad = function(e) {
    if ((this.ie_hack) &&
    	(this.src != this.kaMap.aPixel.src)) {
    	var src = this.src;
        this.src = this.kaMap.aPixel.src;
        this.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='"+src+"')";
    }
    this.style.visibility = 'visible';
};

/**
 * internal function to append a row of images to each of the layers
 *
 * this function is used when the viewport is resized
 * modified by cappu can take a single layer as input
 */
kaMap.prototype.appendRow = function(layer) {
    if (this.nWide == 0) {
        return;
    }
    var layers = null;
    if(arguments.length==1) {
        layers = Array(layer);
    } else {
        layers = this.aMaps[this.currentMap].getLayers();
    }
    for( var i=0; i<layers.length; i++) {
        var obj = layers[i].domObj;
        for (var j=0; j<this.nWide; j++) {
            var top = this.nCurrentTop + (this.nHigh * this.tileHeight);
            var left = this.nCurrentLeft + (j * this.tileWidth);
            var img = this.createImage( top, left, layers[i] );
            //hack around IE problem with clipping layers when a filter is
            //active
            if (this.isIE4) {
                img.style.filter = "Alpha(opacity="+layers[i].opacity+")";
            }
            obj.appendChild( img );
        }
    }
    this.nHigh = this.nHigh + 1;
};

/**
 * internal function to append a column of images to each of the layers
 *
 * this function is used when the viewport is resized
 * modified by cappu can take a single layer as input
 */
kaMap.prototype.appendColumn = function(layer) {
    if (this.nHigh == 0) {
        return;
    }
    var layers = null;
    if(arguments.length==1) {
        layers = Array(layer);
    } else {
        layers = this.aMaps[this.currentMap].getLayers();
    }
    for( var i=0; i<layers.length; i++) {
        var obj = layers[i].domObj;
        for(var j=this.nHigh-1; j>=0; j--) {
            var top = this.nCurrentTop + (j * this.tileHeight);
            var left = this.nCurrentLeft + (this.nWide * this.tileWidth);
            var img = this.createImage( top, left, layers[i] );
            //hack around IE problem with clipping layers when a filter is
            //active
            if (this.isIE4) {
                img.style.filter = "Alpha(opacity="+layers[i].opacity+")";
            }
            if (j < this.nHigh-1) {
                obj.insertBefore(img, obj.childNodes[((j+1)*this.nWide)]);
            } else {
                obj.appendChild(img);
            }
         }
    }
    this.nWide = this.nWide + 1;
};

/**
 * internal function to remove a column of images to each of the layers
 *
 * this function is used when the viewport is resized
 * modified by cappu can take a single layer as input
 */
kaMap.prototype.removeColumn = function(layer) {
    if (this.nWide < 3) {
        return;
    }
    var layers = null;
    if(arguments.length==1) {
        layers = Array(layer);
    } else {
        layers = this.aMaps[this.currentMap].getLayers();
    }
    for( var i=0; i<layers.length; i++) {
        var d = layers[i].domObj;
        for(var j=this.nHigh - 1; j >= 0; j--) {
            var img = d.childNodes[((j+1)*this.nWide)-1];
            d.removeChild( img );
            //attempt to prevent memory leaks
            img.onload = null;
            img.onerror = null;
        }
    }
    this.nWide = this.nWide - 1;
};

/**
 * internal function to remove a row of images to each of the layers
 *
 * this function is used when the viewport is resized
 * modified by cappu can take a single layer as input
 */
kaMap.prototype.removeRow = function(layer) {
    if (this.nHigh < 3) {
        return;
    }

    var layers = null;
    if(arguments.length==1) {
        layers = Array(layer);
    } else {
        layers = this.aMaps[this.currentMap].getLayers();
    }

    for( var i=0; i<layers.length; i++) {
        var d = layers[i].domObj;
        for(var j=this.nWide - 1; j >= 0; j--) {
            var img = d.childNodes[((this.nHigh-1)*this.nWide)+j];
            d.removeChild( img );
            //attempt to prevent memory leaks
            img.onload = null;
            img.onerror = null;
        }
    }
    this.nHigh = this.nHigh - 1;
};

kaMap.prototype.hideLayers = function() {
    if (!this.hideLayersOnMove) {
        return;
    }

    if (this.layersHidden) {
        return;
    }
    var layers = this.aMaps[this.currentMap].getLayers();
    for( var i=0; i<layers.length; i++) {
        layers[i]._visible = layers[i].visible;
        if (layers[i].name != '__base__') {
            layers[i].setVisibility( false );
        }
    }
    for( var i = 0; i < this.aCanvases.length; i++) {
        this.aCanvases[i].style.visibility = 'hidden';
        this.aCanvases[i].style.display = 'none';
    }
    this.layersHidden = true;
};

kaMap.prototype.showLayers = function() {
    if (!this.hideLayersOnMove) {
        return;
    }

    if (!this.layersHidden) {
        return;
    }
    var layers = this.aMaps[this.currentMap].getLayers();
    for( var i=0; i<layers.length; i++) {
        layers[i].setVisibility( layers[i]._visible );
    }
    for( var i = 0; i < this.aCanvases.length; i++) {
        this.aCanvases[i].style.visibility = 'visible';
        this.aCanvases[i].style.display = 'block';
    }
    this.layersHidden = false;
};

/**
 * move the map by a certain amount
 */
kaMap.prototype.moveBy = function( x, y ) {
    var til = this.theInsideLayer;
    til.style.top = (safeParseInt(til.style.top)+y) + 'px';
    til.style.left = (safeParseInt(til.style.left)+x )+ 'px';
    this.checkWrap();
};

/**
 * slide the map by a certain amount
 */
kaMap.prototype.slideBy = function(x,y) {
    if (this.slideid!=null) {
        goQueueManager.dequeue( this.slideid );
    }

    this.as = [];

    var absX = Math.abs(x);
    var absY = Math.abs(y);

    var signX = x/absX;
    var signY = y/absY;

    var distance = absX>absY?absX:absY;
    var steps = Math.floor(distance/this.pixelsPerStep);

    var dx = dy = 0;
    if (steps > 0) {
        dx = (x)/(steps*this.pixelsPerStep);
        dy = (y)/(steps*this.pixelsPerStep);
    }

    var remainderX = x - dx*steps*this.pixelsPerStep;
    var remainderY = y - dy*steps*this.pixelsPerStep;

    var px=py=0;

    var curspeed=this.accelerationFactor;
    var i=0;
    while(i<steps) {
        if (i>0) {
          px+=this.as[i-1][0];
          py+=this.as[i-1][1];
        }

        var cx = px+Math.round(dx*this.pixelsPerStep);
        var cy = py+Math.round(dy*this.pixelsPerStep);
        this.as[i]=new Array(cx-px,cy-py);
        i++;
    }
    if (remainderX != 0 || remainderY != 0) {
        this.as[i] = [remainderX, remainderY];
    }
    this.hideLayers();
    this.slideid=goQueueManager.enqueue(this.timePerStep,this,this.slide,[0]);
};

/**
 * handle individual movement within a slide
 */
kaMap.prototype.slide = function(pos) {
    if (pos>=this.as.length) {
        this.as=slideid=null;
        this.showLayers();
        this.triggerEvent( KAMAP_EXTENTS_CHANGED, this.getGeoExtents() );
        return;
    }

    this.moveBy( this.as[pos][0], this.as[pos][1] );

    pos ++;
    this.slideid=goQueueManager.enqueue(this.timePerStep,this,this.slide,[ pos]);
};

/**
 * internal function to handle various events that are passed to the
 * current tool
 */
kaMap_onkeypress = function( e ) {
    if (this.kaMap.currentTool) {
        this.kaMap.currentTool.onkeypress( e );
    }
    if (this.kaMap.aInfoTools.length > 0) {
        for (var i=0; i<this.kaMap.aInfoTools.length; i++) {
            this.kaMap.aInfoTools[i].onkeypress(e);
        }
    }
};

kaMap_onmousemove = function( e ) {
    e = (e)?e:((event)?event:null);
    if (e.button==2) {
        this.kaMap.triggerEvent( KAMAP_CONTEXT_MENU );
    }
    if (this.kaMap.currentTool) {
        this.kaMap.currentTool.onmousemove( e );
    }
    if (this.kaMap.aInfoTools.length > 0) {
        for (var i=0; i<this.kaMap.aInfoTools.length; i++) {
            this.kaMap.aInfoTools[i].onmousemove(e);
        }
    }
};

kaMap_onmousedown = function( e ) {
    if (this.kaMap.currentTool) {
        this.kaMap.currentTool.onmousedown( e );
    }
    if (this.kaMap.aInfoTools.length > 0) {
        for (var i=0; i<this.kaMap.aInfoTools.length; i++) {
            this.kaMap.aInfoTools[i].onmousedown(e);
        }
    }
};

kaMap_onmouseup = function( e ) {
    if (this.kaMap.currentTool) {
        this.kaMap.currentTool.onmouseup( e );
    }
    if (this.kaMap.aInfoTools.length > 0) {
        for (var i=0; i<this.kaMap.aInfoTools.length; i++) {
            this.kaMap.aInfoTools[i].onmouseup(e);
        }
    }
};

kaMap_onmouseover = function( e ) {
    if (this.kaMap.currentTool) {
        this.kaMap.currentTool.onmouseover( e );
    }
    if (this.kaMap.aInfoTools.length > 0) {
        for (var i=0; i<this.kaMap.aInfoTools.length; i++) {
            this.kaMap.aInfoTools[i].onmouseover(e);
        }
    }
};

kaMap_onmouseout = function( e ) {
     if (this.kaMap.currentTool) {
        this.kaMap.currentTool.onmouseout( e );
    }
    if (this.kaMap.aInfoTools.length > 0) {
        for (var i=0; i<this.kaMap.aInfoTools.length; i++) {
            this.kaMap.aInfoTools[i].onmouseout(e);
        }
    }
};

kaMap_oncontextmenu = function( e ) {
    e = e?e:event;
    if (e.preventDefault) {
        e.preventDefault();
    }
    return false;
};

kaMap_ondblclick = function( e ) {
    if (this.kaMap.currentTool) {
        this.kaMap.currentTool.ondblclick( e );
    }
    if (this.kaMap.aInfoTools.length > 0) {
        for (var i=0; i<this.kaMap.aInfoTools.length; i++) {
            this.kaMap.aInfoTools[i].ondblclick(e);
        }
    }
};

kaMap_onmousewheel = function( e ) {
    if (this.kaMap.currentTool) {
        this.kaMap.currentTool.onmousewheel( e );
    }
};

kaMap.prototype.cancelEvent = function(e) {
    e = (e)?e:((event)?event:null);
    e.returnValue = false;
    if (e.preventDefault) {
        e.preventDefault();
    }
    return false;
};

kaMap.prototype.registerTool = function( toolObj ) {
    this.aTools.push( toolObj );
};

kaMap.prototype.activateTool = function( toolObj ) {
    if (toolObj.isInfoTool()) {
        this.aInfoTools.push(toolObj);
    } else {
        if (this.currentTool) {
            this.currentTool.deactivate();
        }
        this.currentTool = toolObj;
        if (this.theInsideLayer) {
            this.setCursor(this.currentTool.cursor);
        }
    }
};

kaMap.prototype.deactivateTool = function( toolObj ) {
    if (toolObj.isInfoTool()) {
        for (var i=0; i<this.aInfoTools.length; i++) {
            if (this.aInfoTools[i] == toolObj) {
                this.aInfoTools.splice(i,1);
                break;
            }
        }
    } else {
        if (this.currentTool == toolObj) {
            this.currentTool = null;
        }
        if (this.theInsideLayer) {
            this.theInsideLayer.style.cursor = 'auto';
        }
    }
};

/*
 * inspired by code in WindowManager.js
 * Copyright 2005 MetaCarta, Inc., released under the BSD License
 */
kaMap.prototype.setCursor = function(cursor) {
    if (cursor && cursor.length && typeof cursor == 'object') {
        for (var i = 0; i < cursor.length; i++) {
            this.theInsideLayer.style.cursor = cursor[i];
            if (this.theInsideLayer.style.cursor == cursor[i]) {
                break;
            }
        }
    } else if (typeof cursor == 'string') {
        this.theInsideLayer.style.cursor = cursor;
    } else {
        this.theInsideLayer.style.cursor = 'auto';
    }
};

/**
 * internal function to check if images need to be wrapped
 */
kaMap.prototype.checkWrap = function() {
    var bWrapped = false;
    // adjust theInsideLayer so it doesn't show more than maxExtents (if set)
    this.checkMaxExtents();

    this.xOffset = safeParseInt(this.theInsideLayer.style.left) + this.nCurrentLeft - this.xOrigin;
    this.yOffset = safeParseInt(this.theInsideLayer.style.top) + this.nCurrentTop - this.yOrigin;

	//TODO: the various wrap functions remove/append child nodes but its probably
	//not necessary since we are absolutely positioning the images.  This is
	//actually a leftover from when we were relatively positioning images (which
	//ended up being too slow).
    while (this.xOffset > 0) {
        this.wrapR2L();
        bWrapped = true;
    }
    while (this.xOffset < -(this.nBuffer*this.tileWidth)) {
        this.wrapL2R();
        bWrapped = true;
    }
    while (this.yOffset > -(this.nBuffer*this.tileHeight)) {
        this.wrapB2T();
        bWrapped = true;
    }
    while (this.yOffset < -(2*this.nBuffer*this.tileHeight)) {
        this.wrapT2B();
        bWrapped = true;
    }

    var layer = this.aMaps[this.currentMap].getLayers()[0];
    if (layer) {
        var img = layer.domObj.childNodes[0].style;
        this.nCurrentTop = safeParseInt(img.top) + this.yOrigin;
        this.nCurrentLeft = safeParseInt(img.left) + this.xOrigin;
    }

    if (bWrapped) {
        this.triggerEvent( KAMAP_METAEXTENTS_CHANGED, this.getMetaExtents() );
    }
};

/**
 * kaMap.checkMaxExtents()
 *
 * For maps with maxExtent set, this function adjusts the position of
 * theInsideLayer so it never shows more than the maximum extent specified
 * in the mapfile.  Called from kaMap.checkWrap() since that is called
 * with all movement of theInsideLayer
 *
 * Added by tschaub
 */
kaMap.prototype.checkMaxExtents = function() {
    var maxExtents = this.getCurrentMap().maxExtents;
    if (maxExtents.length == 4) {
		if ((maxExtents[0] >= maxExtents[2]) || (maxExtents[1] >= maxExtents[3])) {
			// fail silently
			return false;
		}
        var geoExtents = this.getGeoExtents();
        var hPixelAdjustment = 0;
        var vPixelAdjustment = 0;
        // check left and right
        if (geoExtents[0] < maxExtents[0]) {
            // extra on right
            hPixelAdjustment = Math.round((maxExtents[0] - geoExtents[0]) / this.cellSize);
        }
        if (geoExtents[2] > maxExtents[2]) {
            // extra on left
			if(hPixelAdjustment != 0)
			{
				// if both left and right are over, split the difference
	            hPixelAdjustment += Math.round((maxExtents[2] - geoExtents[2]) / this.cellSize);
				hPixelAdjustment /= 2;
			} else {
				hPixelAdjustment += Math.round((maxExtents[2] - geoExtents[2]) / this.cellSize);
			}
        }
		// check if horizontal adjustment is needed
		if(hPixelAdjustment != 0) {
            this.theInsideLayer.style.left = (safeParseInt(this.theInsideLayer.style.left) - hPixelAdjustment) + 'px';
        }
        // check top and bottom - both can not be corrected
        if(geoExtents[1] < maxExtents[1]) {
            // extra on bottom
            vPixelAdjustment = Math.round((maxExtents[1] - geoExtents[1]) / this.cellSize);
        }
        if(geoExtents[3] > maxExtents[3]) {
            // extra on top
			if(vPixelAdjustment != 0) {
				// if both top and bottom are over, split the difference
	            vPixelAdjustment += Math.round((maxExtents[3] - geoExtents[3]) / this.cellSize);
				vPixelAdjustment /= 2;
			} else {
	            vPixelAdjustment = Math.round((maxExtents[3] - geoExtents[3]) / this.cellSize);
			}
        }
		if(vPixelAdjustment != 0) {
            this.theInsideLayer.style.top = (safeParseInt(this.theInsideLayer.style.top) + vPixelAdjustment) + 'px';
        }
    }
};

/**
 * internal function to reuse extra images
 * take last image from each row and put it at the beginning
 */
kaMap.prototype.wrapR2L = function() {
    this.xOffset = this.xOffset - (this.nBuffer * this.tileWidth);

    var layers = this.aMaps[this.currentMap].getLayers();
    for( var k=0; k<layers.length; k++) {
        var d = layers[k].domObj;
        var refLeft = safeParseInt(d.childNodes[0].style.left);
        for (var j=0; j<this.nHigh; j++) {
            var imgLast = d.childNodes[((j+1)*this.nWide)-1];
            var imgNext = d.childNodes[j*this.nWide];

            imgLast.style.left = (refLeft - this.tileWidth) + 'px';
            imgLast.src = this.aPixel.src;
            d.removeChild(imgLast);
            d.insertBefore(imgLast, imgNext);
            if (layers[k].visible) {
                layers[k].setTile(imgLast);
            }
        }
    }
};

/**
 * internal function to reuse extra image
 * take first image from each row and put it at the end
 */
kaMap.prototype.wrapL2R = function() {
     this.xOffset = this.xOffset + (this.nBuffer*this.tileWidth);
    var layers = this.aMaps[this.currentMap].getLayers();
    for( var k=0; k<layers.length; k++) {
        var d = layers[k].domObj;
        var refLeft = safeParseInt(d.childNodes[this.nWide-1].style.left);
        for (var j=0; j<this.nHigh; j++) {
            var imgFirst = d.childNodes[j*this.nWide];
            var imgNext;
            /* need to use insertBefore to get a node at the end of a 'row'
             * but this doesn't work for the very last row :(*/
            if (j < this.nHigh-1) {
                imgNext = d.childNodes[((j+1)*this.nWide)];
            } else {
                imgNext = null;
            }

            imgFirst.style.left = (refLeft + this.tileWidth) + 'px';
            imgFirst.src = this.aPixel.src;

            d.removeChild(imgFirst);
            if (imgNext) {
                d.insertBefore(imgFirst, imgNext);
            } else {
                d.appendChild(imgFirst);
            }
            if (layers[k].visible) {
                layers[k].setTile(imgFirst);
            }
        }
    }
};

/**
 * internal function to reuse extra images
 * take top image from each column and put it at the bottom
 */
kaMap.prototype.wrapT2B = function() {
    this.yOffset = this.yOffset + (this.nBuffer*this.tileHeight);
    var layers = this.aMaps[this.currentMap].getLayers();
    for( var k=0; k<layers.length; k++) {
        var d = layers[k].domObj;
        var refTop = safeParseInt(d.childNodes[(this.nHigh*this.nWide)-1].style.top);
        for (var i=0; i<this.nWide; i++) {
            var imgBottom = d.childNodes[0];
            imgBottom.style.top = (refTop + this.tileHeight) + 'px';
            imgBottom.src = this.aPixel.src;
            d.removeChild(imgBottom);
            d.appendChild(imgBottom);
            if (layers[k].visible) {
                layers[k].setTile(imgBottom);
            }
        }
    }
};

/**
 * internal function to reuse extra images
 * take bottom image from each column and put it at the top
 */
kaMap.prototype.wrapB2T = function() {
    this.yOffset = this.yOffset - (this.nBuffer*this.tileHeight);
    var layers = this.aMaps[this.currentMap].getLayers();
    for( var k=0; k<layers.length; k++) {
        var d = layers[k].domObj;
        var refTop = safeParseInt(d.childNodes[0].style.top);
        for (var i=0; i<this.nWide; i++) {
            var imgTop = d.childNodes[(this.nHigh*this.nWide)-1];

            imgTop.style.top = (refTop - this.tileHeight) + 'px';
            imgTop.src = this.aPixel.src;

            d.removeChild(imgTop);
            d.insertBefore(imgTop, d.childNodes[0]);
            if (layers[k].visible) {
                layers[k].setTile(imgTop);
            }

        }
    }
};

/**
 * kaMap.addMap( oMap )
 *
 * add a new instance of _map to kaMap.  _map is an internal class that
 * represents a map file from the configuration file.  This function is
 * intended for internal use by the init.php script.
 *
 * oMap - object, an instance of _map
 */
kaMap.prototype.addMap = function( oMap ) {
    oMap.kaMap = this;
    this.aMaps[oMap.name] = oMap;
};

/**
 * kaMap.getMaps()
 *
 * return an array of all the _map objects that kaMap knows about.  These can
 * be used to generate controls to switch between maps and to get information
 * about the layers (groups) and scales available in a given map.
 */
kaMap.prototype.getMaps = function() {
    return this.aMaps;
};

/**
 * kaMap.getCurrentMap()
 *
 * returns the currently selected _map object.  This can be used to get
 * information about the layers (groups) and scales available in the current
 * map.
 */
kaMap.prototype.getCurrentMap = function() {
    return this.aMaps[this.currentMap];
};

/**
 * kaMap.selectMap( name )
 *
 * select one of the maps that kaMap knows about and re-initialize kaMap with
 * this new map.  This function returns true if name is valid and false if the
 * map is invalid.  Note that a return of true does not imply that the map is
 * fully active.  You must register for the KAMAP_MAP_INITIALIZED event since
 * the map initialization happens asynchronously.
 *
 * name - string, the name of the map to select
 * zoom - (optional) array of 3 (centerx, centery, scale) or 4 (minx, miny,
 *        maxx,maxy) values to zoom to.
 */
kaMap.prototype.selectMap = function( name ) {
    if (!this.aMaps[name]) {
        return false;
    } else {
        this.currentMap = name;
        var oMap = this.getCurrentMap();
        this.setBackgroundColor(oMap.backgroundColor);

        this.setMapLayers();
        if (arguments[1] && arguments[1].length == 3) {
            this.zoomTo(arguments[1][0], arguments[1][1], arguments[1][2]);
            oMap.aZoomTo.length = 0;
        } else if (oMap.aZoomTo.length != 0) {
            this.zoomTo(oMap.aZoomTo[0], oMap.aZoomTo[1], oMap.aZoomTo[2]);
            oMap.aZoomTo.length = 0;
        } else if (arguments[1] && arguments[1].length == 4) {
            this.zoomToExtents( arguments[1][0], arguments[1][1],
                                arguments[1][2], arguments[1][3] );
        } else {
            this.zoomToExtents( oMap.currentExtents[0], oMap.currentExtents[1],
                               oMap.currentExtents[2], oMap.currentExtents[3] );
        }
        this.triggerEvent( KAMAP_MAP_INITIALIZED, this.currentMap );
        return true;
    }
};

/*
 * internal function added by cappu
 * check wich layers are visible and checked visible
 * in legend for current scale and map in InsideLayer
 * If needed create append or remove mapLayer!
 */
kaMap.prototype.setMapLayers = function( ) {
    var oMap = this.getCurrentMap();
    //remove layers not to be drown at the selected scale this should be change to not remove the visible
    for(var i = this.theInsideLayer.childNodes.length - 1; i>=0; i-- ) {
        if (this.theInsideLayer.childNodes[i].className == 'mapLayer') {
            this.theInsideLayer.childNodes[i].appended=false;
            this.theInsideLayer.removeChild(this.theInsideLayer.childNodes[i]);        }
    }
   //now check layer and create or append
    layers=oMap.getLayers(); //get only visible and checked layers
    for( var i=0; i<layers.length; i++) {
        if(!layers[i].domObj) {
            var d = this.createMapLayer( layers[i].name );
            this.theInsideLayer.appendChild( d );
            d.appended=true;
            layers[i].domObj = d;
            layers[i].setOpacity( layers[i].opacity );
            layers[i].setZIndex( layers[i].zIndex );
            layers[i].setVisibility( layers[i].visible );
            this.nWide = 0;
            this.nHigh = 0;
            this.drawGroup(layers[i]);
        } else if (!layers[i].domObj.appended) {
            this.theInsideLayer.appendChild( layers[i].domObj );
            layers[i].domObj.appended=true;
            layers[i].setZIndex( layers[i].zIndex );
        }
    }
    return true;
};

/*
 * internal function added by cappu
 * this function force a layer create image
 */
kaMap.prototype.drawGroup = function(group) {
    var newViewportWidth = this.getObjectWidth(this.domObj);
    var newViewportHeight = this.getObjectHeight(this.domObj);

    if (this.viewportWidth == null) {
        this.theInsideLayer.style.top = (-1*this.nCurrentTop + this.yOrigin) + "px";
        this.theInsideLayer.style.left = (-1*this.nCurrentLeft + this.xOrigin) + "px";
        this.viewportWidth = newViewportWidth;
        this.viewportHeight = newViewportHeight;
    }
    var newWide = Math.ceil((newViewportWidth / this.tileWidth) + 2*this.nBuffer);
    var newHigh = Math.ceil((newViewportHeight / this.tileHeight) + 2*this.nBuffer);

    this.viewportWidth = newViewportWidth;
    this.viewportHeight = newViewportHeight;

    if (this.nHigh == 0 && this.nWide == 0) {
        this.nWide = newWide;
    }

    while (this.nHigh < newHigh) {
        this.appendRow(group);
    }
    while (this.nHigh > newHigh) {
        this.removeRow(group);
    }
    while (this.nWide < newWide) {
        this.appendColumn(group);
    }
    while (this.nWide > newWide) {
        this.removeColumn(group);
    }
    return true;
};

kaMap.prototype.createMapLayer = function( id ) {
    var d = document.createElement( 'div' );
    d.id = id;
    d.className = 'mapLayer';
    d.style.position = 'absolute';
    d.style.visibility = 'visible';
    d.style.left = '0px';
    d.style.top = '0px';
    d.style.width= '3000px';
    d.style.height = '3000px';
    d.appended= false;//added by cappu
    return d;
};

//modified by cappu
kaMap.prototype.addMapLayer = function( l ) {
    var map = this.getCurrentMap();
    map.addLayer(l);
    this.setMapLayers();
    this.paintLayer(l);
    this.triggerEvent( KAMAP_LAYERS_CHANGED, this.currentMap );
};

//added by cappu
kaMap.prototype.removeMapLayer = function( id ) {
    var map = this.getCurrentMap();
    var layer = map.getLayer(id);
    if (!layer) {
        return false;
    }
    if (map.removeLayer ( map.getLayer(id) )) {
        this.setMapLayers();
        this.triggerEvent( KAMAP_LAYERS_CHANGED, this.currentMap );
    }
};

kaMap.prototype.getCenter = function() {
    var deltaMouseX = this.nCurrentLeft - this.xOrigin + safeParseInt(this.theInsideLayer.style.left);
    var deltaMouseY = this.nCurrentTop - this.yOrigin +  safeParseInt(this.theInsideLayer.style.top);

    var vpTop = this.nCurrentTop - deltaMouseY;
    var vpLeft = this.nCurrentLeft - deltaMouseX;

    var vpCenterX = vpLeft + this.viewportWidth/2;
    var vpCenterY = vpTop + this.viewportHeight/2;

    return new Array( vpCenterX, vpCenterY );
};

/**
 * kaMap.getGeoExtents()
 *
 * returns an array of geographic extents for the current view in the form
 * (inx, miny, maxx, maxy)
 */
kaMap.prototype.getGeoExtents = function() {
    var minx = -1*(safeParseInt(this.theInsideLayer.style.left) - this.xOrigin) * this.cellSize;
    var maxx = minx + this.viewportWidth * this.cellSize;
    var maxy= (safeParseInt(this.theInsideLayer.style.top) - this.yOrigin) * this.cellSize;
    var miny= maxy - this.viewportHeight * this.cellSize;
    return [minx,miny,maxx,maxy];
};

/**
 * kaMap.getMetaExtents()
 *
 * returns an array of geographic extents for the loaded tiles in the form
 * (minx, miny, maxx, maxy)
 */
kaMap.prototype.getMetaExtents = function() {
    //use current extents if no layers visible
    var result = this.getGeoExtents();
    var oMap = this.getCurrentMap();
    layers=oMap.getLayers();
    for( var i=0; i<layers.length; i++) {
        //find first layer with a domObj
        if(layers[i].domObj) {
            var d = layers[i].domObj;
            //top left of first image should be top left of loaded tiles
            var pl = safeParseInt(d.childNodes[0].style.left);
            var pt = safeParseInt(d.childNodes[0].style.top);
            //convert to geographic
            var glt = this.pixToGeo(pl,pt,true);
            var left = -1*glt[0];
            var top = -1*glt[1];
            //bottom right is easy to calculate from this
            var right = left + this.nWide*this.tileWidth*this.cellSize;
            var bottom = top - this.nHigh*this.tileHeight*this.cellSize;
			//this is right because top and bottom are in the wrong order
            result = [left, bottom, right, top];
            break;
        }
    }
    return result;
};

kaMap.prototype.zoomIn = function() {
    this.zoomByFactor(this.aMaps[this.currentMap].zoomIn());
};

kaMap.prototype.zoomOut = function() {
    this.zoomByFactor(this.aMaps[this.currentMap].zoomOut());
};

kaMap.prototype.zoomToScale = function( scale ) {
    this.zoomByFactor(this.aMaps[this.currentMap].zoomToScale(scale));
};

kaMap.prototype.zoomByFactor = function( nZoomFactor ) {
    if (nZoomFactor == 1) {
        this.triggerEvent( KAMAP_NOTICE, "NOTICE: changing to current scale aborted");
        return;
    }

    this.cellSize = this.cellSize/nZoomFactor;
    this.setMapLayers();
    this.initializeLayers(nZoomFactor);

    this.triggerEvent( KAMAP_SCALE_CHANGED, this.getCurrentScale() );
    this.triggerEvent( KAMAP_EXTENTS_CHANGED, this.getGeoExtents() );
};

kaMap.prototype.getCurrentScale = function() {
    return this.aMaps[this.currentMap].aScales[this.aMaps[this.currentMap].currentScale];
};

kaMap.prototype.setLayerQueryable = function( name, bQueryable ) {
    this.aMaps[this.currentMap].setLayerQueryable( name, bQueryable );
};

kaMap.prototype.setLayerVisibility = function( name, bVisible ) {
    if(!this.loadUnchecked && bVisible) {
        layer=this.aMaps[this.currentMap].getLayer(name);
        layer.visible=true;
        this.setMapLayers();
        this.aMaps[this.currentMap].setLayerVisibility( name, bVisible );
        this.paintLayer(layer);
    } else {
        this.aMaps[this.currentMap].setLayerVisibility( name, bVisible );
    }
};

kaMap.prototype.setLayerOpacity = function( name, opacity ) {
    this.aMaps[this.currentMap].setLayerOpacity( name, opacity );
};

kaMap.prototype.registerEventID = function( eventID ) {
    return this.eventManager.registerEventID(eventID);
};

kaMap.prototype.registerForEvent = function( eventID, obj, func ) {
    return this.eventManager.registerForEvent(eventID, obj, func);
};

kaMap.prototype.deregisterForEvent = function( eventID, obj, func ) {
    return this.eventManager.deregisterForEvent(eventID, obj, func);
};

kaMap.prototype.triggerEvent = function( eventID /*pass additional arguments*/ ) {
    return this.eventManager.triggerEvent.apply( this.eventManager, arguments );
};

/**
 * special helper function to parse an integer value safely in case
 * it is represented in IEEE format (scientific notation).
 */
function safeParseInt( val ) {
    return Math.round(parseFloat(val));
};

/******************************************************************************
 * _map
 *
 * internal class used to store map objects coming from the init script
 *
 * szName - string, the layer name (or group name, in this case ;))
 *
 * szTitle - string, the human-readable title of the map
 *
 * nCurrentScale - integer, the current scale as an index into aszScales;
 *
 * aszScales - array, an array of scale values for zooming.  The first scale is
 *             assumed to be the default scale of the map
 *
 * aszLayers - array, an array of layer names and statuses.  The array is indexed by
 *             the layer name and the value is true or false for the status.
 *
 *****************************************************************************/
function _map(o) {
    this.aLayers = [];
    this.aZoomTo = [];
    this.kaMap = null;
    this.name = (typeof(o.name) != 'undefined') ? o.name : 'noname';
    this.title = (typeof(o.title) != 'undefined') ? o.title : 'no title';
    this.aScales = (typeof(o.scales) != 'undefined') ? o.scales : [1];
    this.currentScale = (typeof(o.currentScale) != 'undefined') ? parseFloat(o.currentScale) : 0;
    this.units = (typeof(o.units) != 'undefined') ? o.units : 5;
    this.resolution = (typeof(o.resolution) != 'undefined') ? o.resolution:72; //used in scale calculations
    this.defaultExtents = (typeof(o.defaultExtents) != 'undefined') ? o.defaultExtents:[];
    this.currentExtents = (typeof(o.currentExtents) != 'undefined') ? o.currentExtents:[];
    this.maxExtents = (typeof(o.maxExtents) != 'undefined') ? o.maxExtents : [];
    this.backgroundColor = (typeof(o.backgroundColor) != 'undefined') ? o.backgroundColor : '#ffffff';
    //to be used for versioning the map file ...
    this.version = (typeof(o.version) != 'undefined') ? o.version : "";
};

_map.prototype.addLayer = function( layer ) {
    layer._map = this;
    layer.zIndex = this.aLayers.length;
    this.aLayers.push( layer );
};

//added by cappu
_map.prototype.removeLayer = function( l ) {
  var alayer=Array();
  for(i=0,a=0;i<this.aLayers.length;i++) {
      if(this.aLayers[i]!=l) {
          alayer[a]=this.aLayers[i];
          a++;
      }
  }
  this.aLayers=alayer;
  return true;
};

//modified by cappu return only layer querable and visible for current scale
_map.prototype.getQueryableLayers = function() {
    var r = [];
    var l = this.getLayers();
    for( var i=0; i<l.length; i++) {
        if (l[i].isQueryable()) {
            r.push(l[i]);
        }
    }
    return r;
};

//modified by cappu, return only layer visible and checked for current scale !!
_map.prototype.getLayers = function() {
    var r = [];
    for( var i=0; i<this.aLayers.length; i++) {
        if (this.aLayers[i].isVisible() &&
            (this.aLayers[i].visible || this.kaMap.loadUnchecked) ) {
            r.push(this.aLayers[i]);
        }
    }
    return r;
};

//added by cappu replace old getQueryableLayers
_map.prototype.getAllQueryableLayers = function() {
    var r = [];
    for( var i=0; i<this.aLayers.length; i++) {
        if (this.aLayers[i].isQueryable()) {
            r.push(this.aLayers[i]);
        }
    }
    return r;
};

//added by cappu replace old getLayers
_map.prototype.getAllLayers = function() {
    return this.aLayers;
};

_map.prototype.getLayer = function( name ) {
    for (var i=0; i<this.aLayers.length; i++) {
        if (this.aLayers[i].name == name) {
            return this.aLayers[i];
        }
    }
};

_map.prototype.getScales = function() {
    return this.aScales;
};

_map.prototype.zoomIn = function() {
    var nZoomFactor = 1;
    if (this.currentScale < this.aScales.length - 1) {
        nZoomFactor = this.aScales[this.currentScale]/this.aScales[this.currentScale+1];
        this.currentScale = this.currentScale + 1;
    }
    return nZoomFactor;
};

_map.prototype.zoomOut = function() {
    var nZoomFactor = 1;
    if (this.currentScale > 0) {
        nZoomFactor = this.aScales[this.currentScale]/this.aScales[this.currentScale-1];
        this.currentScale = this.currentScale - 1;
    }
    return nZoomFactor;
};

_map.prototype.zoomToScale = function( scale ) {
    var nZoomFactor = 1;
    for (var i=0; i<this.aScales.length; i++) {
        if (this.aScales[i] == scale) {
            nZoomFactor = this.aScales[this.currentScale]/scale;
            this.currentScale = parseInt(i);
        }
    }
    return nZoomFactor;
};

_map.prototype.setLayerQueryable = function( name, bQueryable ) {
    var layer = this.getLayer( name );
    if(typeof(layer) != 'undefined') {
        layer.setQueryable( bQueryable );
    }
};

_map.prototype.setLayerVisibility = function( name, bVisible ) {
    var layer = this.getLayer( name );
    if(typeof(layer) != 'undefined') {
        layer.setVisibility( bVisible );
    }
};

_map.prototype.setLayerOpacity = function( name, opacity ) {
    var layer = this.getLayer( name );
    if(typeof(layer) != 'undefined') {
        layer.setOpacity( opacity );
    }
};

_map.prototype.setDefaultExtents = function( minx, miny, maxx, maxy ){
    this.defaultExtents = [minx, miny, maxx, maxy];
    if (this.currentExtents.length == 0)
        this.setCurrentExtents( minx, miny, maxx, maxy );
};

_map.prototype.setCurrentExtents = function( minx, miny, maxx, maxy ) {
    this.currentExtents = [minx, miny, maxx, maxy];
};

_map.prototype.setMaxExtents = function( minx, miny, maxx, maxy ) {
    this.maxExtents = [minx, miny, maxx, maxy];
};

_map.prototype.setBackgroundColor = function( szBgColor ) {
    this.backgroundColor = szBgColor;
};

/******************************************************************************
 * _layer
 *
 * internal class used to store map layers within a map.  Map layers track
 * visibility of the layer in the user interface.  Parameters are passed
 * as an object with the following attributes:
 *
 * name - string, the name of the layer
 * visible - boolean, the current state of the layer (true is visible)
 * opacity - integer, between 0 (transparent) and 100 (opaque), controls opacity
 *           of the layer as a whole
 * imageformat - string, the format to request the tiles in for this layer.  Can
 *               be used to optimize file sizes for different layer types
 *               by using GIF for images with fewer colours and JPEG or PNG24
 *               for high-colour layers (such as raster imagery).
 *
 * queryable - boolean, is the layer queryable?  This is different from the
 *              layer being included in queries.  bQueryable marks a layer as
 *              being capable of being queried.  The layer also has to have
 *              it's query state turned on using setQueryable
 * scales     - array to containing the layer visibility for each scale
 * force    - force layer
 *****************************************************************************/
function _layer( o ) {
    this.domObj = null;
    this._map = null;
    this.name = (typeof(o.name) != 'undefined') ? o.name : 'unnamed';
    this.visible = (typeof(o.visible) != 'undefined') ? o.visible : true;
    this.opacity = (typeof(o.opacity) != 'undefined') ? o.opacity : 100;
    this.imageformat = (typeof(o.imageformat) != 'undefined') ? o.imageformat : null;
    this.queryable = (typeof(o.queryable) != 'undefined') ? o.queryable : false;
    this.queryState = (typeof(o.queryable) != 'undefined') ? o.queryable : false;
    this.tileSource = (typeof(o.tileSource) != 'undefined') ? o.tileSource : 'auto';
    this.scales = (typeof(o.scales) != 'undefined') ? o.scales : new Array(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1);
    this.toLoad=0;
    /* this is used to mark the last time a tile in this layer was redrawn so that
     * some caching on the server can still be used effectively.
     */
    var ts = new Date();
    this.timeStamp = Math.round(ts.getTime()/1000) + ts.getTimezoneOffset() * 60;
    this.redrawInterval = (typeof(o.redrawInterval) != 'undefined') ? o.redrawInterval : -1;
    
    this.refreshInterval = (typeof(o.refreshInterval) != 'undefined') ? o.refreshInterval : -1;
    if (this.refreshInterval > 0) {
        goQueueManager.enqueue( this.refreshInterval*1000, this, this.redraw );
    }
};

_layer.prototype.isQueryable = function() {
    return this.queryState;
};

_layer.prototype.setQueryable = function( bQueryable ) {
    if (this.queryable) {
        this.queryState = bQueryable;
    }
};

//added by  cappu check layer visibility at current scale
_layer.prototype.isVisible= function() {
    return (this.scales[this._map.currentScale]==1)? true:false;
};

/**
 * layer.setOpacity( amount )
 *
 * set a layer to be semi transparent.  Amount is a number between
 * 0 and 100 where 0 is fully transparent and 100 is fully opaque
 */
_layer.prototype.setOpacity = function( amount ) {
    this.opacity = amount;
    if (this.domObj) {
        this.domObj.style.opacity = amount/100;
        this.domObj.style.mozOpacity = amount/100;
        for(var i=0;i<this.domObj.childNodes.length;i++) {
            this.domObj.childNodes[i].style.filter = "Alpha(opacity="+amount+")";
        }
    }
};

_layer.prototype.setTile = function(img) {
    var l = safeParseInt(img.style.left) + this._map.kaMap.xOrigin;
    var t = safeParseInt(img.style.top) + this._map.kaMap.yOrigin;
    // dynamic imageformat
    var szImageformat = '';
    var src;
    var image_format = '';
    if (this.imageformat && this.imageformat != '') {
        image_format = this.imageformat;
        szImageformat = '&i='+image_format;
    }
    if(this.tileSource == 'cache') {
        var metaLeft = Math.floor(l/(this._map.kaMap.tileWidth * this._map.kaMap.metaWidth)) * this._map.kaMap.tileWidth * this._map.kaMap.metaWidth;
        var metaTop = Math.floor(t/(this._map.kaMap.tileHeight * this._map.kaMap.metaHeight)) * this._map.kaMap.tileHeight * this._map.kaMap.metaHeight;
        var metaTileId = 't' + metaTop + 'l' + metaLeft;
        var groupsDir = (this.name != '') ? this.name.replace(/\W/g, '_') : 'def';
        var cacheDir = this._map.kaMap.webCache + this._map.name + '/' + this._map.aScales[this._map.currentScale] + '/' + groupsDir + '/def/' + metaTileId;
        var tileId = "t" + t + "l" + l;
        // the following conversion of image format to image extension
        // works for JPEG, GIF, PNG, PNG24 - others may need different treatment
        var imageExtension = this.imageformat.toLowerCase().replace(/[\de]/g, '');
        src = cacheDir + "/" + tileId + "." + imageExtension;
    } else {
        var szVersion = '';
        if (this._map.version != '') {
            szVersion = '&version='+this._map.version;
        }
        var szForce = '';
        var szLayers = '';
        if (arguments[1]) {
            szForce = '&force=true';
        }
        var szTimestamp = '';
        if (this.tileSource == 'redraw' || this.tileSource == "refresh") {
            szTimestamp = '&ts='+this.timeStamp;
            if (this.redrawInterval) {
                szTimestamp = szTimestamp + '&interval='+this.redrawInterval;
            }
        }
        
        var szGroup = '&g='+img.layer.domObj.id;
        var szScale = '&s='+this._map.aScales[this._map.currentScale];
        var q = '?';
        if (this._map.kaMap.tileURL.indexOf('?') != -1) {
            if (this._map.kaMap.tileURL.slice(-1) != '&') {
                q = '&';
            } else {
                q = '';
            }
        }
        if (this.tileSource == 'nocache') {
            src = this._map.kaMap.server +
            this._map.kaMap.tileURL.replace('tile.php', 'tile_nocache.php') +
            q + 'map=' + this._map.name +
            '&t=' + t +
            '&l=' + l +
            szScale + szForce + szGroup + szImageformat;
            // tack on any variables for replacement
            if(typeof(this.replacementVariables) != 'undefined') {
                for(var key in this.replacementVariables) {
                    src += '&' + encodeURIComponent(key) + '=' + encodeURIComponent(this.replacementVariables[key]);
                }
            }
        } else {
            src = this._map.kaMap.server +
            this._map.kaMap.tileURL +
            q + 'map=' + this._map.name +
            '&t=' + t +
            '&l=' + l +
            szScale + szForce + szGroup + szImageformat + szTimestamp + szVersion;
        }
    }
    if (img.src != src) {
        img.style.visibility = 'hidden';
        img.src = src;
    }
};

_layer.prototype.setVisibility = function( bVisible ) {
    this.visible = bVisible;
    if (this.domObj) {
        this.domObj.style.visibility = bVisible?'visible':'hidden';
        //horrid hack - this is needed in case any element contained
        //within the div has its visibility set ... it overrides the
        //style of the container!!!
        this.domObj.style.display = bVisible?'block':'none';
	    for( var i=0; i<this.domObj.childNodes.length; i++) {
	        this.setTile(this.domObj.childNodes[i]);
	    }
		this._map.kaMap.triggerEvent( KAMAP_LAYER_STATUS_CHANGED, this );
	}
};

_layer.prototype.setZIndex = function( zIndex ) {
    this.zIndex = zIndex;
    if (this.domObj) {
        this.domObj.style.zIndex = zIndex;
    }
};

//Set all layers tile added by cappu
_layer.prototype.setTileLayer = function() {
    this.loaded=0;
    for(i = 0; i < this.domObj.childNodes.length; i++) {
        img = this.domObj.childNodes[i];
        if(arguments[0]) {
            this.setTile(img, arguments[0]);
        }
        else {
            this.setTile(img);
        }
    }
};

/* redraw a layer completely, updating an internal timestamp that is passed as
 * an argument to the server.  If the tile data has changed, you'll get new
 * tiles.
 *
 * first, and only, argument to this function is the new update frequency, if
 * any.  If the update frequency is <= 0 then the layer will not be
 * automatically refreshed.
 */
_layer.prototype.redraw = function() {
    if (arguments[0]) {
        this.refreshInterval = arguments[0];
    }
    if (this.visible) {
        var ts = new Date();
        this.timeStamp = Math.round(ts.getTime()/1000) + ts.getTimezoneOffset() * 60;
        this.setTileLayer();
    }
    if (this.refreshInterval > 0) {
        goQueueManager.enqueue( this.refreshInterval*1000, this, this.redraw );
    }
};

/******************************************************************************
 * Event Manager class
 *
 * an internal class for managing generic events.  kaMap! uses the event
 * manager internally and exposes certain events to the application.
 *
 * the kaMap class provides wrapper functions that hide this implementation
 * useage:
 *
 * myKaMap.registerForEvent( gnSomeEventID, myObject, myFunction );
 * myKaMap.registerForEvent( 'SOME_EVENT', myObject, myFunction );
 *
 * myKaMap.deregisterForEvent( gnSomeEventID, myObject, myFunction );
 * myKaMap.deregisterForEvent( 'SOME_EVENT', myObject, myFunction );
 *
 * myObject is normally null but can be a javascript object to have myFunction
 * executed within the context of an object (becomes 'this' in the function).
 *
 *****************************************************************************/
function _eventManager( )
{
    this.events = [];
    this.lastEventID = 0;
}

_eventManager.prototype.registerEventID = function( eventID ) {
    var ev = new String(eventID);
    if (!this.events[eventID]) {
        this.events[eventID] = [];
    }
};

_eventManager.prototype.registerForEvent = function(eventID, obj, func) {
    var ev = new String(eventID);
    this.events[eventID].push( [obj, func] );
};

_eventManager.prototype.deregisterForEvent = function( eventID, obj, func ) {
    var ev = new String(eventID);
    var bResult = false;
    if (!this.events[eventID]) {
        return false;
    }

    for (var i=0;i<this.events[eventID].length;i++) {

        if (this.events[eventID][i][0] == obj &&
            this.events[eventID][i][1] == func) {
            this.events[eventID].splice(i,1);
            bResult = true;
        }
    }
    return bResult;
};

_eventManager.prototype.triggerEvent = function( eventID ) {
    var ev = new String(eventID);
    if (!this.events[eventID]) {
        return false;
    }

    var args = new Array();
    for(i=1; i<arguments.length; i++) {
        args[args.length] = arguments[i];
    }

    for (var i=0; i<this.events[eventID].length; i++) {
        this.events[eventID][i][1].apply( this.events[eventID][i][0],
                                          arguments );
    }
    return true;
};

/******************************************************************************
 * Queue Manager class
 *
 * an internal class for managing delayed execution of code.  This uses the
 * window.setTimeout interface but adds support for execution of functions
 * on objects
 *
 * The problem with setTimeout is that you need a reference to a global object
 * to do something useful in an object-oriented environment, and we don't
 * really have that here.  So the Queue Manager handles a stack of pending
 * delayed execution code and evaluates it when it comes due.  It can be
 * used exactly like window.setTimeout in that it returns an id that can
 * subsequently be used to clear the delayed code.
 *
 * To add something to the queue, call
 * var id = goQueueManager.enqueue( timeout, obj, func, args );
 *
 * timeout - time to delay (milliseconds)
 * obj - the object to execute the function within.  Can be null for global
 *       scope
 * func - the function to execute.  Note this is the function, not a string
 *        containing the function.
 * args - an array of values to be passed to the function.
 *
 * To remove a function from the queue, call goQueueManager.dequeue( id );
 *****************************************************************************/
var goQueueManager = new _queueManager();

function _queueManager() {
    this.queue = new Array();
}

_queueManager.prototype.enqueue = function( timeout, obj, func, args ) {
    var pos = this.queue.length;
    for (var i=0; i< this.queue.length; i++) {
        if (this.queue[i] == null) {
            pos = i;
            break;
        }
    }
    var id = window.setTimeout( "_queueManager_execute("+pos+")", timeout );
    this.queue[pos] = new Array( id, obj, func, args );
    return pos;
};

_queueManager.prototype.dequeue = function( pos ) {
    if (this.queue[pos] != null) {
        window.clearTimeout( this.queue[pos][0] );
        this.queue[pos] = null;
    }
};

function _queueManager_execute( pos) {
    if (goQueueManager.queue[pos] != null) {
        var obj = goQueueManager.queue[pos][1];
        var func = goQueueManager.queue[pos][2];
        if (goQueueManager.queue[pos][3] != null) {
            func.apply( obj, goQueueManager.queue[pos][3] );
        } else {
            func.apply( obj );
        }
        goQueueManager.queue[pos] = null;
    }
};
