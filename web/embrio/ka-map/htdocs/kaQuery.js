/**********************************************************************
 *
 * $Id: kaQuery.js,v 1.14 2006/09/25 13:18:50 lbecchi Exp $
 *
 * purpose: a simple tool for supporting queries.  It just provides
 *          the user interface for defining the query point or 
 *          area and defers the actual query to the application
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 * KAMAP_MOUSE_STOPPED contributed by Sebastien Roch
 *
 * TODO:
 * 
 *   - implement a sample backend for query code
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
 **********************************************************************
 *
 * To use this tool:
 * 
 * 1) add a script tag to your page
 * 
 * <script type="text/javascript" src="kaQuery.js"></script>
 * 
 * 2) create a new instance of kaQuery
 * 
 * myKaQuery = new kaQuery( myKaMap, KAMAP_RECT_QUERY );
 * 
 * or if you want to do something when mouse stops over the viewport (delay is 400ms here) :
 * 
 * myKaQuery = new kaQuery( myKaMap, KAMAP_MOUSE_STOPPED, 400 );
 * myKaQuery.activate();
 *
 * 3) provide some way of activating it ( not necessary with KAMAP_MOUSE_STOPPED, it's always activated)
 *    This example would allow switching between querying and navigating.
 * 
 * <input type="button" name="navigate" value="Navigate"
 *  onclick="myKaNavigator.activate()">
 * <input type="button" name="query" value="Query"
 *  onclick="myKaQuery.activate()">
 * 
 * 4) listen for the query event 
 * 
 * myKaMap.registerForEvent( KAMAP_QUERY, null, myQuery );
 * myKaMap.resgisterForEvent( KAMAP_MOUSE_STOPPED, null, myMouseStopped );
 * 
 * 5) and do something when the user requests a query
 * 
 * function myQuery( eventID, queryType, coords )
 * {
 *     alert( "QUERY: " + queryType + " " + coords );
 * }
 *
 * 
 * Querying actually does nothing except generate a KAMAP_QUERY event with 
 * the query type and coordinates passed as parameters to the event handler
 *
 * Signature of the query event handler is:
 *
 * function myQueryHandler( eventID, queryType, queryCoords )
 *
 * eventID: int, KAMAP_QUERY
 *
 * queryType: int, one of KAMAP_POINT_QUERY, KAMAP_RECT_QUERY or KAMAP_MOUSE_STOPPED
 *
 * queryCoords: array, array of two or four floating point coordinates
 *              depending on the query type
 *
 * You can affect the style of the zoom box by changing oQuery.domObj.style as
 * you would with any other HTML element (it's a div).
 *
 *****************************************************************************/
// the query event id
var KAMAP_QUERY = gnLastEventId ++;

// human names for the query types
var KAMAP_POINT_QUERY = 0;
var KAMAP_RECT_QUERY = 1;

// ********************** ADDED BY SEBASTIEN ROCH *************************** 
var KAMAP_MOUSE_STOPPED = 2;
// ************************** END MODIF ************************ 

/*
 *	Main function
 *	constructor : (oKaMap, type, [delay])
 *  If type is KAMAP_MOUSE_STOPPED, you have to set up the delay after
 *  which this event is triggered, or default is 500ms
*/
function kaQuery( oKaMap, type ) {
    kaTool.apply( this, [oKaMap] );
    this.type = type;
    // ********************** ADDED BY SEBASTIEN ROCH ***************************
    if(this.type == KAMAP_MOUSE_STOPPED){
	    this.bInfoTool = true;
	    // check arguments
	    if(arguments.length == 3){
    		this.delay = arguments[2];
    	} else {
    		alert("Incorrect nb of arguments for instance kaQuery. Delay will be set by default to 500ms");
    		this.delay = 500;
    	}
    }
    // ************************** END MODIF ************************ 
    this.name = 'kaQuery';
    this.cursor = 'help';
    
    this.startx = null;
    this.starty = null;
    this.endx = null;
    this.endy = null;
    this.bMouseDown = false;
    // ********************** ADDED BY SEBASTIEN ROCH ***************************
	// array for storing geo coords when mouse is stopped
	this.coords = new Array();
	// flag
	this.mouseStopped = false; 
    this.chrono = null;
    // ************************** END MODIF ************************ 
    
    //this is the HTML element that is visible
    this.domObj = document.createElement( 'div' );
    this.domObj.style.position = 'absolute';
    this.domObj.style.top = '0px';
    this.domObj.style.left = '0px';
    this.domObj.style.width = '1px';
    this.domObj.style.height = '1px';
    this.domObj.style.zIndex = 50;
    this.domObj.style.visibility = 'hidden';
    this.domObj.style.border = '1px solid red';
    this.domObj.style.backgroundColor = 'white';
    this.domObj.style.opacity = 0.50;
    this.domObj.style.mozOpacity = 0.50;
    this.domObj.style.filter = 'Alpha(opacity=50)';
    this.kaMap.theInsideLayer.appendChild( this.domObj );

    for (var p in kaTool.prototype) {
        if (!kaQuery.prototype[p])
            kaQuery.prototype[p]= kaTool.prototype[p];
    }
};

/*
 * draw a box representing the query region.
 *
 * kaQuery maintains the query region in four variables.  The variables are
 * assumed to be in pixel coordinates and are used to position the box.  If
 * any of the coordinates are null, clear the query box.
 */
kaQuery.prototype.drawZoomBox = function() {
    if (this.startx == null || this.starty == null ||
        this.endx == null || this.endy == null ) {
        this.domObj.style.visibility = 'hidden';
        this.domObj.style.top = '0px';
        this.domObj.style.left = '0px';
        this.domObj.style.width = '1px';
        this.domObj.style.height = '1px';
        return;
    }
    
    this.domObj.style.visibility = 'visible';
    if (this.endx < this.startx) {
        this.domObj.style.left = (this.endx - this.kaMap.xOrigin) + 'px';
        this.domObj.style.width = (this.startx - this.endx) + "px";
    }
    else {
        this.domObj.style.left = (this.startx - this.kaMap.xOrigin) + 'px';
        this.domObj.style.width = (this.endx - this.startx) + "px";
    }

    if (this.endy < this.starty) {
        this.domObj.style.top = (this.endy - this.kaMap.yOrigin) + 'px';
        this.domObj.style.height = (this.starty - this.endy) + "px";
    } else {
        this.domObj.style.top = (this.starty - this.kaMap.yOrigin) + 'px';
        this.domObj.style.height = (this.endy - this.starty) + "px";
    }
};

/**
 * kaQuery.onmousemove( e )
 *
 * called when the mouse moves over theInsideLayer.
 *
 * e - object, the event object or null (in ie)
 */
kaQuery.prototype.onmousemove = function(e) {
    e = (e)?e:((event)?event:null);
    
    // ********************** ADDED BY SEBASTIEN ROCH ***************************
    // don't return false if we are handling a KAMAP_MOUSE_STOPPED query
    if(this.type != KAMAP_MOUSE_STOPPED){
	    if (!this.bMouseDown) {
    	    return false;
    	}
    }
    // ************************** END MODIF ************************ 
    
    var x = e.pageX || (e.clientX +
          (document.documentElement.scrollLeft || document.body.scrollLeft));
    var y = e.pageY || (e.clientY +
                (document.documentElement.scrollTop || document.body.scrollTop));
	
	// ********************** MODIFIED/ADDED BY SEBASTIEN ROCH ***************************
	var adjCoords = this.adjustPixPosition( x, y );
	
	if(this.type == KAMAP_MOUSE_STOPPED){
		// get geo position
		var p = this.kaMap.pixToGeo(adjCoords[0], adjCoords[1]); 
		this.coords[0] = p[0];
		this.coords[1] = p[1];
		
		// if chrono is ON, we reset it
		if(this.chrono != null)
			clearTimeout(this.chrono);
		
		// call the onmousestop function after a delay if mouse doesn't move anymore
		var t = this;
		if(this.mouseStopped == false){
			this.chrono = setTimeout(function(){t.onmousestop()}, this.delay);
		}
	}
	
    if (this.type == KAMAP_RECT_QUERY) {
        this.endx = -adjCoords[0];
        this.endy = -adjCoords[1];
        
        this.drawZoomBox();
    }
    // ************************** END MODIF ************************ 
    return false;
};

// ********************** MODIFIED/ADDED BY SEBASTIEN ROCH ***************************
/**
 * kaQuery.onmousestop()
 *
 * called if mouse is stopped during "this.delay"
 * 
 */
kaQuery.prototype.onmousestop = function(){
	// stop chrono
	clearTimeout(this.chrono);
	// update flag -> avoid calling the onmousestop function if it's already being called
	this.mouseStopped = true;
	this.kaMap.triggerEvent(KAMAP_MOUSE_STOPPED, this.type, this.coords);
	this.mouseStopped = false;
	return;
};
 // ************************** END MODIF ************************ 


/**
 * kaQuery.onmouseout( e )
 *
 * called when the mouse leaves theInsideLayer.  Terminate the query
 *
 * e - object, the event object or null (in ie)
 */
kaQuery.prototype.onmouseout = function(e) {
    e = (e)?e:((event)?event:null);
    
    // ********** MODIFIED/ADDED BY SEBASTIEN ROCH ******************
    clearTimeout(this.chrono);
    // ************************** END MODIF ************************ 
    
    if (!e.target) e.target = e.srcElement;
    if (e.target.id == this.kaMap.domObj.id) {
        this.bMouseDown = false;
        this.startx = this.endx = this.starty = this.endy = null;
        this.drawZoomBox();
        return kaTool.prototype.onmouseout.apply(this, [e]);
    }
};


/**
 * kaQuery.onmousedown( e )
 *
 * called when a mouse button is pressed over theInsideLayer.
 *
 * e - object, the event object or null (in ie)
 */
kaQuery.prototype.onmousedown = function(e) {
	e = (e)?e:((event)?event:null);
	
	// ********** MODIFIED/ADDED BY SEBASTIEN ROCH ******************
    // we "desactivate" clicks if type is KAMAP_MOUSE_STOPPED
	if(this.type != KAMAP_MOUSE_STOPPED){
	// ************************** END MODIF ************************
	    if (e.button==2) {
	        return this.cancelEvent(e);
	    }
	    else {
	        if (this.kaMap.isIE4)
	        	document.onkeydown = kaTool_redirect_onkeypress;
	        
	        document.onkeypress = kaTool_redirect_onkeypress;
	        
	        this.bMouseDown = true;
	        
	        var x = e.pageX || (e.clientX +
	              (document.documentElement.scrollLeft || document.body.scrollLeft));
	        var y = e.pageY || (e.clientY +
	                    (document.documentElement.scrollTop || document.body.scrollTop));
	        
	        var aPixPos = this.adjustPixPosition( x,y );
	        this.startx=this.endx = -aPixPos[0];
	        this.starty=this.endy = -aPixPos[1];
	        
	        this.drawZoomBox();
	        
	        e.cancelBubble = true;
	        e.returnValue = false;
	        if (e.stopPropagation) e.stopPropagation();
	        if (e.preventDefault) e.preventDefault();
	        return false;
	    }
	}
};

/**
 * kaQuery.onmouseup( e )
 *
 * called when a mouse button is clicked over theInsideLayer.
 *
 * e - object, the event object or null (in ie)
 */
kaQuery.prototype.onmouseup = function(e) {
	e = (e)?e:((event)?event:null);
	
	// ********** MODIFIED/ADDED BY SEBASTIEN ROCH ******************
    // we "desactivate" clicks if type is KAMAP_MOUSE_STOPPED
    if(this.type != KAMAP_MOUSE_STOPPED){
    // ************************** END MODIF ************************
	    var type = KAMAP_POINT_QUERY;
	    var start = this.kaMap.pixToGeo( -this.startx, -this.starty );
	    
	    var coords = start;
	    if (this.startx!=this.endx&&this.starty!=this.endy) {
	        type = KAMAP_RECT_QUERY;
	        coords = start.concat(this.kaMap.pixToGeo( -this.endx, -this.endy ));
	        if(coords[2] < coords[0]) {
	            //minx gt maxx than I invert values
	            var minx = coords[2];
	            var maxx = coords[0];
	            coords[0] = minx;
	            coords[2] = maxx;
	        }
	        if(coords[1] < coords[3]){
	            //miny gt maggiore than I invert values
	            var miny = coords[1];
	            var maxy = coords[3];
	            coords[3] = miny;
	            coords[1] = maxy;
	        }
	    }
	    this.kaMap.triggerEvent(KAMAP_QUERY, type, coords);
	    
	    this.startx = this.endx = this.starty = this.endy = null;
	    this.drawZoomBox();
	}        
	return false;
	    
};