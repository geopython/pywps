/******************************************************************************
 * kaXmlOverlay - XML server side generated overlay for kaMap.
 *
 * Piergiorgio Navone 
 *
 * $Id: kaXmlOverlay.js,v 1.4 2006/08/08 13:17:55 pspencer Exp $
 *****************************************************************************/
 
/******************************************************************************
 * BEGIN section in Wiki syntax
 
=kaXmlOverlay Quick HOW-TO=

* '''1''' Import scripts in your page:

 <script type="text/javascript" src="xhr.js"></script>
 <script type="text/javascript" src="excanvas.js"></script>
 <script type="text/javascript" src="wz_jsgraphics.js"></script>
 <script type="text/javascript" src="XMLOverlay/kaXmlOverlay.js"></script>

* '''2''' Let ka-Map initialize itself: the next steps should wait at lest the KAMAP_MAP_INITIALIZED event.

* '''3''' Create a kaXmlOverlay object:

 myXmlOverlay = new kaXmlOverlay( myKaMap, 250 );

* '''4''' Add some objects on the overlay layer. There are two ways to do that

** Call the loadXml method: this method load an XML document from the web server.

 myXmlOverlay.loadXml('points.xml');

** Write a JavaScript function to add your objects:

 var my_point = myXmlOverlay.addNewPoint('Point ID', longuitude, latitude);
 var my_symbol = new kaXmlSymbol();
 my_symbol.size = 12;
 my_symbol.color = '#ff0000';
 my_point.addGraphic(my_symbol);


* '''5''' To have a periodic update:

 myInterval = setInterval("myMovingOverlay.loadXml('xmlget.php')",5000);


--------------------------------------------

= kaXmlOverlay Reference=

This document describe the interface of the JavaScript kaXmlOverlay library as well as the XLM documents describing overlays. The document is divided in tree sections:

# A summary of JavaScript objects and functions
# The definition of the XML
# An in deep description of attributes common to both XML and JavaScript functions


== JavaScript API==

In this section there is a list of main classes with methods an properties that you ca use to programmatically add overlays to your map.
A detailed an updated documentation for each function is maintained as JavaDoc like comments in the source code.


=== Class kaXmlOverlay===

This class represent a map layer where is possible to add overlays.
To instantiate this class use the constructor
 
 kaXmlOverlay( oKaMap, xml_url )
;oKaMap: A kaMap object
;zIndex: The z index of the layer


To load an XML document with overlay description call the method

 kaXmlOverlay.prototype.loadXml = function(xml_url)
;xml_url: URL of th XML with points to plot


To add a new point to an overlay

 kaXmlOverlay.prototype.addNewPoint = function(pid, x, y)
;pid: Point ID
;x: X geo-coordinate
;y: Y geo-coordinate
;return: A kaXmlPoint object with the given point ID.


To retrieve an existing point from an overlay call

 kaXmlOverlay.prototype.getPointObject = function(pid)
;pid: Point ID
;return: The kaXmlPoint object given the point ID. null if not found.


To remove one or more points from the overlay

kaXmlOverlay.prototype.removePoint = function( pid )
;pid: Point ID or a regexp. If pid is null or not present remove all points.


=== Class kaXmlPoint===
A kaXmlPoint represents a group of graphic object on the overlay layer. The point is placed on the map at specified geographic coordinates. A point can be moved on the map without the need of redrawing all its graphic objects. 

To instantiate a new point don't use the constructor but call the ''kaXmlOverlay.addNewPoint()'' function.


To place or move a kaXmlPoint on the map call

 kaXmlPoint.prototype.setPosition = function( x, y )
;x: X geo-coordinate
;y: Y geo-coordinate


To clear all graphics associated with the point call the method

 kaXmlPoint.prototype.clear = function()


To add graphic objects to a point use the method

 kaXmlPoint.prototype.addGraphic = function( obj )
;obj: an object of type kaXmlSymbol, kaXmlIcon, kaXmlLabel, kaXmlLinestring or kaXmlPolygon


To manually set the HTML content of a kaXmlPoint use the method

 kaXmlPoint.prototype.setInnerHtml = function(ihtml)
;ihtml: A string containing the HTML

This function delete any other content of the point.



=== Graphic objects classes===
The graphic objects that can be displayed are:

* kaXmlSymbol
* kaXmlLabel
* kaXmlIcon
* kaXmlLinestring
* kaXmlPolygon

All this classes have a constructor without parameters and different attributes: the attributes are described in the following of the document.

To use one of these objects create a new instance, configure it setting its properties ad add it to a ''kaXmlPoint'' with the method ''addGraphic''.



'''Using CANVAS for vector graphics'''

Symbols, linestrings and polygons are drawn using <canvas>. To change this behaviour and use
the previous implementation (drawgeom.php and wz_jsgraphcs) use

 xmlOverlayUseCanvas = false;


== XML Document Type Definition==

----------


 <!ELEMENT overlay (delete*, point*)>
 
 <!-- 
 	Delete from the overlay layer one or more points. If the atribute 'id' is present it's 
 	used as a regular expression to match point id to be deleted. If 'id' is not given 
 	deletes all points.
 -->
 <!ELEMENT delete EMPTY>
 
 <!--
 	Define a point with a given ID. If the ID exists it's moved to the new position
 	otherwise it is drawn on the map.
 	In order to redraw an existing point to change some attribute in the rendering
 	let include the attribute redraw="true" or a <delete> element. 
  -->
 <!ELEMENT point (ihtml?, symbol*, icon*, label*, linestring*, polygon*)>
 
 <!-- 
 	Insert arbitrary HTML in the point DIV.
 -->
 <!ELEMENT ihtml (#PCDATA)>
 
 
 <!ELEMENT symbol EMPTY>
 <!ELEMENT icon EMPTY>


 <!-- 
 	The content of the label element is the text of label.
 -->
 <!ELEMENT label (#PCDATA)>

 <!-- 
 	The content of the linestring element is a list of coordinates in the form:
 		x0 y0, x1 y1, [...], xn yn
 -->
 <!ELEMENT linestring EMPTY>
 
 <!-- 
 	The content of the polygon element is a list of coordinates in the form:
 		x0 y0, x1 y1, [...], xn yn
 -->
 <!ELEMENT polygon EMPTY>
 
 <!ATTLIST delete id CDATA #IMPLIED>
 
 <!ATTLIST point id CDATA #REQUIRED>
 <!ATTLIST point x CDATA #REQUIRED>
 <!ATTLIST point y CDATA #REQUIRED>
 <!ATTLIST point redraw (false|true) "false">
 
 <!ATTLIST symbol shape CDATA #IMPLIED>
 <!ATTLIST symbol size CDATA #IMPLIED>
 <!ATTLIST symbol color CDATA #IMPLIED>
 <!ATTLIST symbol bcolor CDATA #IMPLIED>
 <!ATTLIST symbol stroke CDATA #IMPLIED>
 <!ATTLIST symbol opacity CDATA #IMPLIED>
 
 <!ATTLIST icon src CDATA #REQUIRED>
 <!ATTLIST icon w CDATA #REQUIRED>
 <!ATTLIST icon h CDATA #REQUIRED>
 <!ATTLIST icon px CDATA #IMPLIED>
 <!ATTLIST icon py CDATA #IMPLIED>
 <!ATTLIST icon opacity CDATA #IMPLIED>
 
 <!ATTLIST label color CDATA #IMPLIED>
 <!ATTLIST label boxcolor CDATA #IMPLIED>
 <!ATTLIST label w CDATA #IMPLIED>
 <!ATTLIST label h CDATA #IMPLIED>
 <!ATTLIST label px CDATA #IMPLIED>
 <!ATTLIST label py CDATA #IMPLIED>
 <!ATTLIST label fsize CDATA #IMPLIED>
 <!ATTLIST label font CDATA #IMPLIED>
 
 <!ATTLIST linestring color CDATA #IMPLIED>
 <!ATTLIST linestring stroke CDATA #IMPLIED>
 <!ATTLIST linestring opacity CDATA #IMPLIED>

 <!ATTLIST polygon color CDATA #IMPLIED>
 <!ATTLIST polygon bcolor CDATA #IMPLIED>
 <!ATTLIST polygon stroke CDATA #IMPLIED>
 <!ATTLIST polygon opacity CDATA #IMPLIED>

----------


=== XML document example===

 <overlay>
  <point x="7435386.24" y="6172463.1" id="p1">
    <label>just a label</label>
    <symbol shape="bullet" size="10" opacity="1" color="#FF0000" />
  </point>
 </overlay>

== Overlay objects attributes==

=== POINT (<point>)===

The POINT is the father of all objects you can display on the overlay layer.
Wherever you want dislay someting on the overlay layer you have to define a
POINT than add to the POINT icons, symbols, labels, etc.

'''POINT attributes:'''

;id: (string, mandatory) This string is used to identify the point. It's needed to translate, delete, redraw the POINT.
;x: (number, required) The X coordinate in map units.
;y: (number, required) The Y coordinate in map units.


=== SYMBOL (kaXmlSymbol, <symbol>)===
A symbol is a graphic element drawn at POINT coordinates. It's similar to an icon, but it has a parametric color and size.

'''SYMBOL attributes:'''

;shape: (string, optional) The shape of the symbol. Today implementation allows only the shapes ''bullet'' and ''square''.
;color: (string, optional) The fill color of the symbol (HTML syntax).
;bcolor: (string, optional) Border color (HTML syntax).
;size: (integer, optional) The size in pixels of the symbol.
;stroke: (integer, optional) Line width in pixels.
;opacity: (number, optional) 1.0 is opaque, 0.0 is fully transparent.


=== ICON (kaXmlIcon, <icon>)===
An icon drawn at POINT coordinates. The image is defined with an URL. Width and height of the image must be provided, because the icon will be centred at POINT coordinates.

'''ICON attributes'''

;src: (string, required) The relative or absolute URL of the image
;w: (integer, required) Width of the image in pixels
;h: (integer, required) Height of the image in pixels
;px: (integer, optional) Horizontal offset in pixels (positive to move the icon on the right).
;py: (integer, optional) Vertical offset in pixels (negative to rise the icon).
;opacity: (number, optional) 1.0 is opaque, 0.0 is fully transparent.

=== LABEL (kaXmlLabel, <label>)===
A text label is written near the POINT. POINT coordinates represent the top-left corner of the LABEL.

'''LABEL attributes'''

;color: (string, optional) Text color (HTML syntax).
;boxcolor: (string, optional) Background color behind the text (HTML syntax).
;w: (integer, optional) Width of the label in pixels.
;h: (integer, optional) Height of the label in pixels.
;px: (integer, optional) Horizontal offset in pixels (positive to move the label on the right).
;py: (integer, optional) Vertical offset in pixels (negative to rise the label).
;font: (string, optional) The text font (HTML syntax).
;fsize: (string, optional) Font size (HTML syntax).
;text: (string, required) The label text: this attribute is present only in JavaScript: in the XML syntax the text is the content of the <label> element.


=== LINESTRING (kaXmlLinestring, <linestring>)===
This element represent a geographic feature, a single line in geographic coordinates that will be scaled with the map.
The coordinates of the line must be expressed a string in the form

 x0 y0, x1 y1, [...], xn yn

The coordinates string is the text node of the XML element. In JavaScript the coordinates string is passed
to the object with the method readCoordinates().

'''LINESTRING attributes'''

;color: (string, optional) Line color (HTML syntax).
;stroke: (integer, optional) Line width in pixels.
;opacity: (number, optional) 1.0 is opaque, 0.0 is fully transparent.


=== POLYGON (kaXmlPolygon, <polygon>)===
This element represent a geographic feature, a single polygon in geographic coordinates that will be scaled with the map.

'''POLYGON attributes'''

;color: (string, optional) Surface color (HTML syntax).
;bcolor: (string, optional) Border color (HTML syntax).
;stroke: (integer, optional) Border width in pixels.
;opacity: (number, optional) 1.0 is opaque, 0.0 is fully transparent.

---------------------------------------------------

= FAQs=

''Error: xmlDocument has no properties''

;: The XML is served with a wrong mime type by your web server. It should have a mime type "text/xml". Configure your server to associate ".xml" files with the correct mime, or, if you generate the XML dynamically, use a directive to set the mime type.


''In IE6 with excanvas.js canvas are not displayed''

;: The HTML page must begin with
 <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">

---------------------------------------------------

= TODOs=
* Evaluate the use of custom onclick or ondblclick events on points
* Add a tooltip for overlay points
* Make the label management smarter

 
 * END section in Wiki syntax
 *****************************************************************************/

/**
 * kaXmlOverlay( oKaMap, xml_url )
 *
 * oKaMap 	A kaMap object
 * zIndex	The z index of the layer
 */
function kaXmlOverlay( oKaMap, zIndex )
{
    kaTool.apply( this, [oKaMap] );
    this.name = 'kaXmlOverlay';

    for (var p in kaTool.prototype)
    {
        if (!kaXmlOverlay.prototype[p]) 
            kaXmlOverlay.prototype[p]= kaTool.prototype[p];
    }
    
    this.urlBase = this.kaMap.server;
    this.urlBase += (this.urlBase!=''&&this.urlBase.substring(-1)!='/')?'':'/';

	// The list of overlay points
	this.ovrObjects = new Array();   
	
	// The cavas of the overlay layer
	this.z_index = zIndex;
	this.overlayCanvas = this.kaMap.createDrawingCanvas( zIndex );
	
	// Register for events
    this.kaMap.registerForEvent( KAMAP_SCALE_CHANGED, this, this.scaleChanged );
	
}

kaXmlOverlay.prototype.scaleChanged = function( eventID, mapName ) {
	if (this.ovrObjects == null) return;
	for (var i=0; i < this.ovrObjects.length; i++) {
		if (this.ovrObjects[i]) this.ovrObjects[i].rescale();
	}
}

/**
 * Remove the overlay layer and free resources user by overlay objects.
 */
kaXmlOverlay.prototype.remove = function() {
    this.kaMap.deregisterForEvent( KAMAP_SCALE_CHANGED, this, this.scaleChanged );
	this.removePoint();
	this.kaMap.removeDrawingCanvas(this.overlayCanvas);
}


/**
 * Load XML from the server and update the overlay.
 *
 * xml_url	URL of th XML with points to plot
 */
kaXmlOverlay.prototype.loadXml = function(xml_url) {
    this.urlBase = this.kaMap.server;
    this.urlBase += (this.urlBase!=''&&this.urlBase.substring(-1)!='/')?'':'/';

	// The URL of the XML
	this.xmlOvrUrl = this.urlNormalize(xml_url);
	
	call(this.xmlOvrUrl,this,this.loadXmlCallback);
}

/**
 * Defines the DOMParser object for IE
 */
if (typeof DOMParser == "undefined") {
   DOMParser = function () {}

   DOMParser.prototype.parseFromString = function (str, contentType) {
      if (typeof ActiveXObject != "undefined") {
         var d = new ActiveXObject("MSXML.DomDocument");
         d.loadXML(str);
         return d;
      } else if (typeof XMLHttpRequest != "undefined") {
         var req = new XMLHttpRequest;
         req.open("GET", "data:" + (contentType || "application/xml") +
                         ";charset=utf-8," + encodeURIComponent(str), false);
         if (req.overrideMimeType) {
            req.overrideMimeType(contentType);
         }
         req.send(null);
         return req.responseXML;
      }
   }
}

kaXmlOverlay.prototype.loadXmlCallback = function(xml_string) {
	var xmlDocument =  (new DOMParser()).parseFromString(xml_string, "text/xml");
	this.loadXmlDoc(xmlDocument);
}

kaXmlOverlay.prototype.loadXmlDoc = function(xmlDocument) {

	var objDomTree = xmlDocument.documentElement;
	
	var dels = objDomTree.getElementsByTagName("delete");
	for (var i=0; i<dels.length; i++) {
		// read the id attribute
		var a_id = dels[i].getAttributeNode("id");
		if (a_id == null) {
			// delete all points
			this.removePoint();
		} else {
			this.removePoint(a_id.value);
		}
	}
	
	var need_update = false;
		
	var points = objDomTree.getElementsByTagName("point");
	for (var i=0; i<points.length; i++) {
		// read the mandatory attributes
		var a_pid = points[i].getAttributeNode("id");
		if (a_pid == null) {
			continue;
		}
		var pid = a_pid.value;
				
		var np = this.getPointObject(pid);
		if (np == null) {
			// Create a new point
			np = new kaXmlPoint(pid,this);
			this.ovrObjects.push(np);
		}

		np.parse(points[i]);
		need_update = true;
	}
	
	if (need_update) this.kaMap.updateObjects();
}

/**
 * 
 */
kaXmlOverlay.prototype.urlNormalize = function(url) {
	if (url == null) return "";
	if (url.match(/^\//) != '/') {
		return this.urlBase+url;
	}
	return url;
}
 
/**
 * pid		Point ID
 * return The DIV object of the given point ID. null if not found.
 */
kaXmlOverlay.prototype.getDiv = function(pid) {
	var div_id = this.getDivId(pid);
	return getRawObject(div_id);
}

/**
 * pid		Point ID
 * return The kaXmlPoint object given the point ID. null if not found.
 */
kaXmlOverlay.prototype.getPointObject = function(pid) {
	for (var i=0; i < this.ovrObjects.length; i++) {
		if (this.ovrObjects[i] != null && this.ovrObjects[i].pid == pid) {
			return this.ovrObjects[i];
	 	}
	}
	return null;
}

/**
 * Instantiate a new kaXmlPoint adn add it to the overlay. If the PID
 * already exists it's deleted and recreated.
 *
 * pid		Point ID
 * x			X Coordinate
 * y			Y Coordinate
 * return A kaXmlPoint object with the given point ID.
 */
kaXmlOverlay.prototype.addNewPoint = function(pid,x,y) {
	this.removePoint(pid);
	var np = new kaXmlPoint(pid,this);
	np.placeOnMap(x,y);
	this.ovrObjects.push(np);
	return np;
}

/**
 * pid		Point ID
 * return the DIV id given the point ID
 */
kaXmlOverlay.prototype.getDivId = function(pid) {
	return 'xmlovr_'+pid+'_div';
}

/**
 * Remove one or more point div from the map.
 * If pid is null or not present remove all points.
 *
 * pid		Point ID or a regexp 
 */
kaXmlOverlay.prototype.removePoint = function( pid ) {

	if ( (this.removePoint.arguments.length < 1) || (pid == null) ) {
	
		for (var i=this.ovrObjects.length; i-- > 0; ) {
			if (this.ovrObjects[i] != null) {
				this.ovrObjects[i].removeFromMap();
				delete this.ovrObjects[i];
				this.ovrObjects[i] = null;
			}
			this.ovrObjects.splice(i,1); 
		}
		
	} else {
	
		var re = new RegExp(pid);
		for (var i=this.ovrObjects.length; i-- > 0; ) {
			if (this.ovrObjects[i] != null) {
				if (re.test(this.ovrObjects[i].pid)) {
					this.ovrObjects[i].removeFromMap();
					delete this.ovrObjects[i];
					this.ovrObjects[i] = null;
					this.ovrObjects.splice(i,1);
				}
			} else {
				this.ovrObjects.splice(i,1);
			}
		}
	}
}
 

/**
 * Base class for all graphics elements.
 */
function kaXmlGraphicElement() {}

/**
 * Initialize the graphics element from an XML element
 *
 * point			The parent kaXmlPoint object
 * domElement	The XML DOM element that describe the graphic
 */
kaXmlGraphicElement.prototype.parseElement = function(point, domElement) {}

/**
 * Draw the graphics element
 *
 * point		The parent kaXmlPoint object
 */
kaXmlGraphicElement.prototype.draw = function(point) {}

/**
 * Draw the graphics element
 *
 * point		The parent kaXmlPoint object
 */
kaXmlGraphicElement.prototype.rescale = function(point) {}

/**
 * Dispose the resources allocated in the graphics element
 *
 * point		The parent kaXmlPoint object
 */
kaXmlGraphicElement.prototype.remove = function(point) {}


/**
 * Construct a symbol 
 */
function kaXmlSymbol() {
	kaXmlGraphicElement.apply(this);
	if (_BrowserIdent_hasCanvasSupport())
		kaXmlSymbol.prototype['draw'] = kaXmlSymbol.prototype['draw_canvas'];
	else
		kaXmlSymbol.prototype['draw'] = kaXmlSymbol.prototype['draw_js'];
		
    for (var p in kaXmlGraphicElement.prototype) {
        if (!kaXmlSymbol.prototype[p]) 
            kaXmlSymbol.prototype[p]= kaXmlGraphicElement.prototype[p];
    }
	
	this.shape = "bullet";
	this.size = 10;
    this.stroke = 1;
	this.color = null;
	this.bcolor = null;
	this.opacity = 1;
	
	this.canvas = null;
	this.ldiv = null;
}

kaXmlSymbol.prototype.remove = function(point) {
	this.canvas = null;
	this.ldiv = null;	
}

kaXmlSymbol.prototype.parseElement = function(point, domElement) {
	this.shape = domElement.getAttribute("shape");
	this.size = parseInt(domElement.getAttribute("size"));
	var c = domElement.getAttribute("color");
	if (c != null) this.color = c;
	var c = domElement.getAttribute("bcolor");
	if (c != null) this.bcolor = c;
	c = parseFloat(domElement.getAttribute("opacity"));
	if(! isNaN(c)) this.opacity = c; 
	c = parseInt(domElement.getAttribute("stroke"));
	if (! isNaN(c)) this.stroke = c;
}

kaXmlSymbol.prototype.draw_js = function(point) {
	var jsgObject = new jsGraphics(point.divId); 
	var d = this.size / 2;     

	jsgObject.setStroke(this.stroke);

	if (this.shape == 'square') {
	
		if (this.color) {
			jsgObject.setColor(this.color);
			jsgObject.fillRect(-d, -d, this.size, this.size);
		}	
		if (this.bcolor) {
			jsgObject.setColor(this.bcolor);
			jsgObject.fillRect(-d, -d, this.size, this.size);
		}	
		
	} else {
		
		if (this.color) {
			jsgObject.setColor(this.color);
			jsgObject.fillEllipse(-d, -d, this.size, this.size);
		}	
		if (this.bcolor) {
			jsgObject.setColor(this.bcolor);
			jsgObject.drawEllipse(-d, -d, this.size, this.size);
		}	
	}
	
	jsgObject.paint();
}

kaXmlSymbol.prototype.draw_canvas = function(point) {
	var d = Math.floor((this.size + this.stroke) / 2);     
	
	if (this.canvas == null) {
		this.ldiv = document.createElement( 'div' );
		this.ldiv.style.position = 'absolute';
	    this.ldiv.style.left = -d+'px';
	    this.ldiv.style.top = -d+'px';
		point.div.appendChild(this.ldiv);
		this.canvas = _BrowserIdent_newCanvas(this.ldiv);
		_BrowserIdent_setCanvasHW(this.canvas,d*2,d*2);
	} 
	
	var ctx = _BrowserIdent_getCanvasContext(this.canvas);
	ctx.save();
	//alert("Point("+point.pid+") Size("+this.size+") D("+d+")");
	
	ctx.translate(d,d);
	ctx.globalAlpha = this.opacity;
	ctx.lineWidth = this.stroke;
	if (this.bcolor) ctx.strokeStyle = this.bcolor;	
	if (this.color) ctx.fillStyle = this.color;
	
	if (this.shape == 'square') {
		if (this.color) ctx.fillRect(-this.size/2.0,-this.size/2.0,this.size,this.size);
		if (this.bcolor) ctx.strokeRect(-this.size/2.0,-this.size/2.0,this.size,this.size);
	} else {
		ctx.beginPath();
		ctx.arc(0,0,this.size/2.0,0,Math.PI*2,false);
		if (this.color) ctx.fill();	
		if (this.bcolor) ctx.stroke();	
	}
	ctx.restore();
}

/**
 * Construct a geographic feature
 */
function kaXmlFeature( point ) {
	kaXmlGraphicElement.apply(this);
    for (var p in kaXmlGraphicElement.prototype) {
        if (!kaXmlFeature.prototype[p]) 
            kaXmlFeature.prototype[p]= kaXmlGraphicElement.prototype[p];
    }
    
    this.stroke = 1;
    this.color = null;
    this.bcolor = null;
    this.opacity = 1;

	this.cxmin = 0;
	this.cymax = 0;
	this.cymin = 0;
	this.cxmax = 0;
	this.coords = "";
	this.img = null;
	this.canvas = null;
	this.ldiv = null;	
	this.xn = null;
	this.yn = null;
	
	// Calculate the min cellSize
	var map = point.xml_overlay.kaMap.getCurrentMap();
	var scales = map.getScales();
	this.maxScale = scales[scales.length - 1];
	this.mcs = point.xml_overlay.kaMap.cellSize / (point.xml_overlay.kaMap.getCurrentScale() / this.maxScale);
}

kaXmlFeature.prototype.remove = function(point) {
	this.img = null;
	this.canvas = null;
	this.ldiv = null;
	this.coords = null;	
	this.xn.splice(0);
	this.yn.splice(0);
}

	
kaXmlFeature.prototype.parseElement = function(point, domElement) {
	var t;
	t = parseInt(domElement.getAttribute("stroke"));
	if (! isNaN(t)) this.stroke = t;
	t = domElement.getAttribute("color");
	if (t != null) this.color = t;
	t = domElement.getAttribute("bcolor");
	if (t != null) this.bcolor = t;
	t = parseFloat(domElement.getAttribute("opacity"));
	if(! isNaN(t)) this.opacity = t; 
	
	var text = "";
	if (domElement.firstChild != null) {
		text = domElement.firstChild.data;
		this.readCoordinates(point, text);	
	}
}
/**
 * Read the feature coordinates from a string 
 *
 *   x0 y0, x1 y1, [...], xn yn
 */
kaXmlFeature.prototype.readCoordinates = function(point, text) {
	var cx = new Array();
	var cy = new Array();
	var pp = text.split(',');
	var i;
	for (i=0; i<pp.length; i++) {
		var s = pp[i];
		var xy = s.match(/[-\+\d\.]+/g);
		if (xy != null) {
			var x=parseFloat(xy[0]);
			var y=parseFloat(xy[1]);
			cx.push(x);
			cy.push(y);
		}
	}
	
	this.setCoordinates(point,cx,cy);
}

/**
 * Set the coordinates of the feature.
 * 
 * xArray	Ordered array of x coordinates (float)
 * yArray	Ordered array of y coordinates (float)
 */
kaXmlFeature.prototype.setCoordinates = function(point, xArray, yArray) {
	this.cxmin = 0;
	this.cymax = 0;
	this.cymin = 0;
	this.cxmax = 0;
	this.coords = "";
	var i;
	for (i=0; i<xArray.length; i++) {
		var x=xArray[i];
		var y=yArray[i];
		if (i==0 || x<this.cxmin) this.cxmin = x;
		if (i==0 || y>this.cymax) this.cymax = y;
		if (i==0 || y<this.cymin) this.cymin = y;
		if (i==0 || x>this.cxmax) this.cxmax = x;
	}
	
	this.xn = new Array();
	this.yn = new Array();
	
	// Normalize the coordinates
	for (i=0; i<xArray.length; i++) {
		var x = (xArray[i] - this.cxmin) / this.mcs;
		var y = (this.cymax - yArray[i]) / this.mcs;
		if (i>0) this.coords += ",";
			this.coords += Math.round(x)+","+Math.round(y);
		this.xn.push(x);
		this.yn.push(y);
	}
}

kaXmlFeature.prototype.rescale = function(point) {
	this.draw(point);
}


/**
 * Construct a linestring 
 */
function kaXmlLinestring( point ) {
	kaXmlFeature.apply(this, [point]);
	
	if (_BrowserIdent_hasCanvasSupport())
		kaXmlLinestring.prototype['draw'] = kaXmlLinestring.prototype['draw_canvas'];
	else
		kaXmlLinestring.prototype['draw'] = kaXmlLinestring.prototype['draw_server'];	
	
    for (var p in kaXmlFeature.prototype) {
        if (!kaXmlLinestring.prototype[p]) 
            kaXmlLinestring.prototype[p]= kaXmlFeature.prototype[p];
    }
}

kaXmlLinestring.prototype.draw_server = function(point) {
	var xy = point.xml_overlay.kaMap.geoToPix( this.cxmin, this.cymax );
	var x0 = xy[0];
	var y0 = xy[1];
	
	xy = point.xml_overlay.kaMap.geoToPix( point.div.lon, point.div.lat );
	var xr = xy[0];
	var yr = xy[1];
	
	var border = 5;
	
	if (this.img == null) {
    		this.img = document.createElement( 'img' );
	    point.div.appendChild( this.img );
	    this.img.style.position = 'absolute';
	}
	
    this.img.style.top = (y0 - yr - border)+'px';
    this.img.style.left = (x0 - xr - border)+'px';
    var scf = point.xml_overlay.kaMap.getCurrentScale() / this.maxScale;
    var it = _BrowserIdent_getPreferredImageType();
    var u = point.xml_overlay.kaMap.server+"/XMLOverlay/drawgeom.php?gt=L&st="+this.stroke+"&bp="+border+"&sc="+scf+"&cl="+this.coords;
    if (this.color != null) u += "&lc="+escape(this.color);
    if (it == "P") {
    		u += "&it=P";
    } else {
    		u += "&it=G";
    }
    if (_BrowserIdent_getPreferredOpacity() == "server") {
    		if (this.opacity < 1) u += "&op="+(this.opacity*100);
    } else {
    		if (this.opacity < 1) _BrowserIdent_setOpacity(this.img, this.opacity);
    }
    this.img.src = u;
}

kaXmlLinestring.prototype.draw_canvas = function(point) {
	var xy = point.xml_overlay.kaMap.geoToPix( this.cxmin, this.cymax );
	var x0 = xy[0];
	var y0 = xy[1];
	
	xy = point.xml_overlay.kaMap.geoToPix( this.cxmax, this.cymin );
	var x1 = xy[0];
	var y1 = xy[1];
	
	xy = point.xml_overlay.kaMap.geoToPix( point.div.lon, point.div.lat );
	var xr = xy[0];
	var yr = xy[1];
	
	var border = 5;
    var scf = point.xml_overlay.kaMap.getCurrentScale() / this.maxScale;
	
	var sizex = (x1 - x0) + (border*2);
	var sizey = (y1 - y0) + (border*2);
	
	if (this.canvas == null) {
		this.ldiv = document.createElement( 'div' );
		this.ldiv.style.position = 'absolute';
		point.div.appendChild(this.ldiv);
		this.canvas = _BrowserIdent_newCanvas(this.ldiv);
	} 
	
    this.ldiv.style.left = (x0 - xr - border)+'px';
	this.ldiv.style.top = (y0 - yr - border)+'px';
	_BrowserIdent_setCanvasHW(this.canvas,sizey,sizex);
	
	var ctx = _BrowserIdent_getCanvasContext(this.canvas);
	ctx.save();
	ctx.clearRect(0, 0, sizex, sizey);
	ctx.translate(border,border);
	ctx.strokeStyle = this.color;
	ctx.globalAlpha = this.opacity;
	ctx.lineWidth = this.stroke;
	ctx.beginPath();
	ctx.moveTo(this.xn[0]/scf, this.yn[0]/scf);
	
	var i;
	for (i=1; i<this.xn.length; i++) {
		ctx.lineTo(this.xn[i]/scf, this.yn[i]/scf);
	}
	ctx.stroke();
	ctx.restore();
}

/**
 * Construct a Polygon from the XML element
 */
function kaXmlPolygon( point ) {
	kaXmlFeature.apply(this, [point]);
	
	if (_BrowserIdent_hasCanvasSupport())
		kaXmlPolygon.prototype['draw'] = kaXmlPolygon.prototype['draw_canvas'];
	else
		kaXmlPolygon.prototype['draw'] = kaXmlPolygon.prototype['draw_server'];
	
    for (var p in kaXmlFeature.prototype) {
        if (!kaXmlPolygon.prototype[p]) 
            kaXmlPolygon.prototype[p]= kaXmlFeature.prototype[p];
    }
}

kaXmlPolygon.prototype.draw_server = function(point) {
	var xy = point.xml_overlay.kaMap.geoToPix( this.cxmin, this.cymax );
	var x0 = xy[0];
	var y0 = xy[1];
	
	xy = point.xml_overlay.kaMap.geoToPix( point.div.lon, point.div.lat );
	var xr = xy[0];
	var yr = xy[1];
	
	var border = 5;
	
	if (this.img == null) {
    		this.img = document.createElement( 'img' );
	    this.img.style.position = 'absolute';
	    point.div.appendChild( this.img );
	}
	
    var scf = point.xml_overlay.kaMap.getCurrentScale() / this.maxScale;
    var it = _BrowserIdent_getPreferredImageType();
    var u = point.xml_overlay.kaMap.server+"/XMLOverlay/drawgeom.php?gt=P&st="+this.stroke+"&bp="+border+"&sc="+scf+"&cl="+this.coords;
    if (this.color != null) u += "&fc="+escape(this.color);
    if (this.bcolor != null && this.bcolor != "") u += "&lc="+escape(this.bcolor);
    if (it == "P") {
    		u += "&it=P";
    } else {
    		u += "&it=G";
    }
    if (_BrowserIdent_getPreferredOpacity() == "server") {
    		if (this.opacity < 1) u += "&op="+(this.opacity*100);
    } else {
    		if (this.opacity < 1) _BrowserIdent_setOpacity(this.img, this.opacity);
    }
    
    this.img.style.top = (y0 - yr - border)+'px';
    this.img.style.left = (x0 - xr - border)+'px';
    
    this.img.src = u;
}

kaXmlPolygon.prototype.draw_canvas = function(point) {
	var xy = point.xml_overlay.kaMap.geoToPix( this.cxmin, this.cymax );
	var x0 = xy[0];
	var y0 = xy[1];
	
	xy = point.xml_overlay.kaMap.geoToPix( this.cxmax, this.cymin );
	var x1 = xy[0];
	var y1 = xy[1];
	
	xy = point.xml_overlay.kaMap.geoToPix( point.div.lon, point.div.lat );
	var xr = xy[0];
	var yr = xy[1];
	
	var border = 5;
    var scf = point.xml_overlay.kaMap.getCurrentScale() / this.maxScale;
	
	var sizex = (x1 - x0) + (border*2);
	var sizey = (y1 - y0) + (border*2);
	
	if (this.canvas == null) {
		this.ldiv = document.createElement( 'div' );
		this.ldiv.style.position = 'absolute';
		point.div.appendChild(this.ldiv);
		this.canvas = _BrowserIdent_newCanvas(this.ldiv);
	} 
	
    this.ldiv.style.left = (x0 - xr - border)+'px';
	this.ldiv.style.top = (y0 - yr - border)+'px';
	_BrowserIdent_setCanvasHW(this.canvas,sizey,sizex);
	
	var ctx = _BrowserIdent_getCanvasContext(this.canvas);
	ctx.save();
	ctx.clearRect(0, 0, sizex, sizey);
	ctx.translate(border,border);
    if (this.color != null) ctx.fillStyle = this.color;
    if (this.bcolor != null && this.bcolor != "") ctx.strokeStyle = this.bcolor;
	ctx.globalAlpha = this.opacity;
	ctx.lineWidth = this.stroke;
	ctx.beginPath();
	ctx.moveTo(this.xn[0]/scf, this.yn[0]/scf);
	
	var i;
	for (i=1; i<this.xn.length; i++) {
		ctx.lineTo(this.xn[i]/scf, this.yn[i]/scf);
	}
	
	if (this.color != null) ctx.fill();
	if (this.bcolor != null && this.bcolor != "") ctx.stroke();
	ctx.restore();
}

/**
 * Construct a label from the XML element
 */
function kaXmlLabel() {
	kaXmlGraphicElement.apply(this);
    for (var p in kaXmlGraphicElement.prototype) {
        if (!kaXmlLabel.prototype[p]) 
            kaXmlLabel.prototype[p]= kaXmlGraphicElement.prototype[p];
    }
	
	this.text = "";
	this.color = "black";
	this.boxcolor = null;
	this.w = 64;
	this.h = 24;
	this.xoff = 0;
	this.yoff = 0;
	this.fsize = "10px";
	this.font = "Arial";
	this.ldiv = null;
	this.ltxt = null;
}

kaXmlLabel.prototype.remove = function(point) {
	this.canvas = null;
	this.ldiv = null;	
	this.ltxt = null;
}

kaXmlLabel.prototype.parseElement = function(point, domElement) {
	if (domElement.firstChild != null) {
		this.text = domElement.firstChild.data;
	}

	var t;		
	t = domElement.getAttribute("color");
	if (t != null) {
		this.color = t;
	}
	this.boxcolor = domElement.getAttribute("boxcolor");
	t = parseInt(domElement.getAttribute("w"));
	if (!isNaN(t)) {
		this.w = t;
	}
	t = parseInt(domElement.getAttribute("h"));
	if (!isNaN(t)) {
		this.h = t;
	}
	t = parseInt(domElement.getAttribute("px"));
	if (!isNaN(t)) {
		this.xoff = t;
	}
	t = parseInt(domElement.getAttribute("py"));
	if (!isNaN(t)) {
		this.yoff = t;
	}
	t = domElement.getAttribute("fsize");
	if (t != null) {
		this.fsize = t;
	}
	t = domElement.getAttribute("font");
	if (t != null) {
		this.font = t;
	}	
}

kaXmlLabel.prototype.draw = function(point) {
	var x = this.xoff;
	var y = this.yoff;
	
	this.ldiv = document.createElement( 'div' );
	this.ldiv.style.fontFamily = this.font;
	this.ldiv.style.fontSize = this.fsize;
	this.ldiv.style.textAlign = 'center';
	this.ldiv.style.color = this.color;
    this.ldiv.style.left = x+'px';
    this.ldiv.style.top = y+'px';
	this.ldiv.style.position = 'absolute';
	if (this.boxcolor != null) this.ldiv.style.backgroundColor = this.boxcolor;
	if (this.w>0) this.ldiv.style.width = this.w+'px';
	else this.ldiv.style.whiteSpace = 'nowrap';
	if (this.h>0) this.ldiv.style.height = this.h+'px';
	
	this.ltxt = document.createTextNode(this.text);
	this.ldiv.appendChild( this.ltxt );
	
	point.div.appendChild( this.ldiv );
}

/**
 * Construct an icon
 */
function kaXmlIcon() {
	kaXmlGraphicElement.apply(this);
	if (_BrowserIdent_hasCanvasSupport())
		kaXmlIcon.prototype['draw'] = kaXmlIcon.prototype['draw_canvas'];
	else
		kaXmlIcon.prototype['draw'] = kaXmlIcon.prototype['draw_plain'];
    for (var p in kaXmlGraphicElement.prototype) {
        if (!kaXmlIcon.prototype[p]) 
            kaXmlIcon.prototype[p]= kaXmlGraphicElement.prototype[p];
    }
    
	this.icon_src = null;
	this.icon_w = 0;
	this.icon_h = 0;
	this.xoff = 0;
	this.yoff = 0;
	this.rot = 0;
	this.ldiv = null;	
	this.img = null;	
	this.canvas = null;
}

kaXmlIcon.prototype.remove = function(point) {
	this.ldiv = null;	
	this.canvas = null;
	if (this.img) this.img.onload = null;
	this.img = null;	
}

kaXmlIcon.prototype.parseElement = function(point, domElement) {
	this.icon_src = point.xml_overlay.urlNormalize(domElement.getAttribute("src"));
	this.icon_w = parseInt(domElement.getAttribute("w"));
	this.icon_h = parseInt(domElement.getAttribute("h"));
	var t;
	t = parseInt(domElement.getAttribute("px"));
	if (!isNaN(t)) {
		this.xoff = t;
	}
	t = parseInt(domElement.getAttribute("py"));
	if (!isNaN(t)) {
		this.yoff = t;
	}
	t = parseInt(domElement.getAttribute("rot"));
	if (!isNaN(t)) {
		this.rot = t;
	}
}

kaXmlIcon.prototype.draw_canvas = function(point) {
	var dx = -this.icon_w / 2 + this.xoff;     
	var dy = -this.icon_h / 2 + this.yoff;     
	
	if (this.canvas == null) {
		this.ldiv = document.createElement( 'div' );
		this.ldiv.style.position = 'absolute';
	    this.ldiv.style.top = dy+'px';
    	this.ldiv.style.left = dx+'px';
		point.div.appendChild(this.ldiv);
		this.canvas = _BrowserIdent_newCanvas(this.ldiv);
		_BrowserIdent_setCanvasHW(this.canvas,this.icon_h*2,this.icon_w*2);
	} 
	
	var ctx = _BrowserIdent_getCanvasContext(this.canvas);
	ctx.save();
    ctx.translate(-dx,-dy);
    ctx.rotate(this.rot * Math.PI/180);
    this.img = new Image();
    this.img.src = this.icon_src;
    var timg = this.img;
    var tw = this.icon_w;
    var th = this.icon_h;
	this.img.onload = function() {
		ctx.drawImage(timg, dx, dy, tw, th);
		ctx.restore();
	}
}

kaXmlIcon.prototype.draw_plain = function(point) {
	var dx = -this.icon_w / 2 + this.xoff;     
	var dy = -this.icon_h / 2 + this.yoff;     
	
    this.ldiv = document.createElement( 'div' );
    this.ldiv.style.position = 'absolute';
    this.ldiv.style.top = dy+'px';
    this.ldiv.style.left = dx+'px';
    
    this.img = document.createElement( 'img' );
    this.img.src = this.icon_src;
    //img.class = 'png24';
    this.img.width = this.icon_w;
    this.img.height = this.icon_h;
    
    this.ldiv.appendChild( this.img );
    point.div.appendChild( this.ldiv );
}

/**
 * This object is a single point on the overlay.
 * The object hold the div and all the stuff to draw and move the point 
 * (symbol, label, icon, etc.).
 *
 * pid			The point ID (string)
 * xml_overlay	The kaXmlOverlay object owner of this point
 */
function kaXmlPoint(pid, xml_overlay) {
	this.xml_overlay = xml_overlay;
	this.pid = pid;
	this.divId = this.xml_overlay.getDivId(pid);
	this.geox = 0;
	this.geoy = 0;
	this.shown = false;
	
	this.graphics = new Array();
	
	this.div = document.createElement('div');
	this.div.setAttribute('id', this.divId);
}

/**
 * Show the point in the specified geo-position.
 */
kaXmlPoint.prototype.placeOnMap = function( x, y ) {
	if (!this.shown) {
		this.geox = x;
		this.geoy = y;
		this.xml_overlay.kaMap.addObjectGeo( this.xml_overlay.overlayCanvas, x, y, this.div );
		this.shown = true;
	} 
}

/**
 * Delete the point.
 */
kaXmlPoint.prototype.removeFromMap = function( ) {
	if (this.shown) {
		this.xml_overlay.kaMap.removeObject( this.div );
		this.shown = false;
	}
	
	var i;
	for (i=0; i<this.graphics.length; i++) {
		this.graphics[i].remove(this);
	}
	
	this.graphics.splice(0);
	
	this.div = null;
	this.xml_overlay = null;
}

/**
 * Move the point in the specified geo-position.
 */
kaXmlPoint.prototype.setPosition = function( x, y ) {
	if (this.shown) {
		this.geox = x;
		this.geoy = y;
		this.div.lat = y;
		this.div.lon = x;
	}
}

/**
 * Add a new kaXmlGraphicElement to this kaXmlPoint.
 * kaXmlGraphicElement subclasses are:
 *  
 *  kaXmlSymbol
 *  kaXmlIcon
 *  kaXmlLabel
 *  kaXmlLinestring
 *  kaXmlPolygon
 *
 * obj	an object of class kaXmlGraphicElement
 */
kaXmlPoint.prototype.addGraphic = function( obj ) {
		this.graphics.push(obj);
		obj.draw(this);
}

/**
 * Clear all the graphic elements of this kaXmlPoint.
 */
kaXmlPoint.prototype.clear = function() {
	this.div.innerHTML = "";
	this.graphics.length = 0;
	//this.graphics = new Array();
}

/**
 * Set the HTML content of this kaXmlPoint.
 * This function delete any other content of the point.
 *
 * ihtml		A string containing the HTML
 */
kaXmlPoint.prototype.setInnerHtml = function(ihtml) {
	this.clear();
	this.div.innerHTML = ihtml;
}

/**
 * Parse the XML fragment describing the point. Then draw or translate
 * the point on the map.
 *
 * point_element	 A DOM element <point>
 */
kaXmlPoint.prototype.parse = function(point_element) {

	var i;
	var x = parseFloat(point_element.getAttribute("x"));
	var y = parseFloat(point_element.getAttribute("y"));
	var redraw_a = point_element.getAttribute("redraw");
	var redraw = false;
	if (redraw_a == "true")	redraw = true;
			
	if (!this.shown) {
		this.placeOnMap(x,y);
		this.shown = true;
	} else {
		this.setPosition(x,y);
		
		// Need redraw?
		if (!redraw) return;
		
		// clear and redraw the point
		this.clear();
	}
		
	// look for ihtml element
	var ihtml_element = point_element.getElementsByTagName("ihtml");
	for (i=0; i<ihtml_element.length; i++) {
		this.div.innerHTML = ihtml_element[i].firstChild.nodeValue;
	}
	
	var t;
	var elements;
	
	// look for symbol element
	elements = point_element.getElementsByTagName("symbol");
	for (i=0; i<elements.length; i++) {
		t = new kaXmlSymbol();
		t.parseElement(this, elements[i]);
		this.addGraphic(t);
	}
	
	// look for icon element
	elements = point_element.getElementsByTagName("icon");
	for (i=0; i<elements.length; i++) {
		t = new kaXmlIcon();
		t.parseElement(this, elements[i]);
		this.addGraphic(t);
	}

	// look for label element
	elements = point_element.getElementsByTagName("label");
	for (i=0; i<elements.length; i++) {
		t = new kaXmlLabel();
		t.parseElement(this, elements[i]);
		this.addGraphic(t);
	}
	
	// look for linestring element
	elements = point_element.getElementsByTagName("linestring");
	for (i=0; i<elements.length; i++) {
		t = new kaXmlLinestring(this);
		t.parseElement(this, elements[i]);
		this.addGraphic(t);
	}
	
	// look for polygon element
	elements = point_element.getElementsByTagName("polygon");
	for (i=0; i<elements.length; i++) {
		t = new kaXmlPolygon(this);
		t.parseElement(this, elements[i]);
		this.addGraphic(t);
	}
}

kaXmlPoint.prototype.rescale = function(point_element) {
	var i;
	for (i=0; i<this.graphics.length; i++) {
		this.graphics[i].rescale(this);
	}
}

/**************************************************************/


var _BrowserIdent_browser = null;
var _BrowserIdent_version = null;
var _BrowserIdent_place = 0;
var _BrowserIdent_thestring = null;
var _BrowserIdent_detect = null;

function _BrowserIdent() {
	_BrowserIdent_detect = navigator.userAgent.toLowerCase();

	if (_BrowserIdent_checkIt('konqueror')) {
		_BrowserIdent_browser = "Konqueror";
	} else if (_BrowserIdent_checkIt('safari')) _BrowserIdent_browser = "Safari";
	else if (_BrowserIdent_checkIt('omniweb')) _BrowserIdent_browser = "OmniWeb";
	else if (_BrowserIdent_checkIt('opera')) _BrowserIdent_browser = "Opera"
	else if (_BrowserIdent_checkIt('webtv')) _BrowserIdent_browser = "WebTV";
	else if (_BrowserIdent_checkIt('icab')) _BrowserIdent_browser = "iCab";
	else if (_BrowserIdent_checkIt('msie')) _BrowserIdent_browser = "Internet Explorer";
	else if (_BrowserIdent_checkIt('firefox')) _BrowserIdent_browser = "Firefox";
	else if (!_BrowserIdent_checkIt('compatible')) {
		_BrowserIdent_browser = "Netscape Navigator"
		_BrowserIdent_version = _BrowserIdent_detect.charAt(8);
	} else _BrowserIdent_browser = "An unknown browser";

	if (!_BrowserIdent_version) _BrowserIdent_version = _BrowserIdent_detect.charAt(_BrowserIdent_place + _BrowserIdent_thestring.length);
	
	//alert(navigator.userAgent+"\nBrowser["+_BrowserIdent_browser+"] Version["+_BrowserIdent_version+"]");
}

function _BrowserIdent_checkIt(string) {
	_BrowserIdent_place = _BrowserIdent_detect.indexOf(string) + 1;
	_BrowserIdent_thestring = string;
	return _BrowserIdent_place;
}

function _BrowserIdent_setOpacity(imageobject, opacity) {
	if (opacity == undefined || opacity >= 1) return '';
	if (_BrowserIdent_browser == "Netscape Navigator")
		imageobject.style.MozOpacity=opacity;
	else if (_BrowserIdent_browser == "Internet Explorer" && parseInt(this.version)>=4) {
		//filter: alpha(opacity=50);
		var tmp = imageobject.style.cssText;
		tmp = "filter: alpha(opacity="+(opacity*100)+");" + tmp;
		imageobject.style.cssText = tmp;
	} else {
		var tmp = imageobject.style.cssText;
		tmp = "opacity: "+opacity+";" + tmp;	
		imageobject.style.cssText = tmp;
	}
}

function _BrowserIdent_getPreferredImageType() {
	if (_BrowserIdent_browser == "Netscape Navigator") return "P";
	else if (_BrowserIdent_browser == "Opera") return "P";
	else if (_BrowserIdent_browser == "Firefox") return "P";
	else if (_BrowserIdent_browser == "Safari") return "P";
	else if (_BrowserIdent_browser == "Konqueror") return "P";
	else return "G"
}

function _BrowserIdent_getPreferredOpacity() {
	if (_BrowserIdent_browser == "Netscape Navigator") return "server";
	else if (_BrowserIdent_browser == "Firefox") return "server";
	else if (_BrowserIdent_browser == "Opera") return "server";
	else if (_BrowserIdent_browser == "Konqueror") return "server";
	else return "client"
}

var xmlOverlayUseCanvas = true;

function _BrowserIdent_hasCanvasSupport() {

	if (! xmlOverlayUseCanvas) return false;
	
	if (_BrowserIdent_browser == "Internet Explorer") return true;
	if (_BrowserIdent_browser == "Firefox") return true;
	if (_BrowserIdent_browser == "Safari") return true;
	//if (_BrowserIdent_browser == "Konqueror") return true;
	//if (_BrowserIdent_browser == "Opera") return true;
	
	return false;
}

function _BrowserIdent_newCanvas(parentNode) {
	var el = document.createElement('canvas');
	parentNode.appendChild(el);
	if (typeof G_vmlCanvasManager != "undefined") {
		el = G_vmlCanvasManager.initElement(el);
	}
	return el;
}

function _BrowserIdent_getCanvasContext(canvas) {
	return canvas.getContext('2d');
}

function _BrowserIdent_setCanvasHW(canvas, height, width) {
		canvas.width = width; 
		canvas.height = height;
}

_BrowserIdent();
