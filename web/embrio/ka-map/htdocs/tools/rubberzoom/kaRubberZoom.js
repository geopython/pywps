/**********************************************************************
 *
 * $Id: kaRubberZoom.js,v 1.4 2006/07/20 12:04:32 lbecchi Exp $
 *
 * purpose: a rubber zoom.
 *
 * author: Lorenzo Becchi and Paul Spencer (pspencer@dmsolutions.ca) (bug 1494)
 *
 * TODO:
 * 
 *   - 
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
 * <script type="text/javascript" src="kaRubberZoom.js"></script>
 * 
 * 2) create a new instance of kaRubberZoom
 * 
 * myKaRubberZoom = new kaRubberZoom( myKaMap );
 * 
 *
 *****************************************************************************/



/**
 * kaRubberZoom constructor
 *
 * construct a new kaRubberZoom object of a given type for a given kaMap instance
 *
 * oKaMap - a kaMap instance
 *
 * type - int, one of KAMAP_POINT_QUERY or KAMAP_RECT_QUERY.  If the type is
 *        KAMAP_POINT_QUERY then only point queries are allowed.  If the type
 *        is KAMAP_RECT_QUERY then point or rectangle queries are possible.
 */
function kaRubberZoom( oKaMap) {
    kaTool.apply( this, [oKaMap] );
    this.name = 'kaRubberZoom';
    this.cursor = 'help';
    
    //this is the HTML element that is visible
    this.domObj = document.createElement( 'div' );
    this.domObj.style.position = 'absolute';
    this.domObj.style.top = '0px';
    this.domObj.style.left = '0px';
    this.domObj.style.width = '1px';
    this.domObj.style.height = '1px';
    this.domObj.style.zIndex = 100;
    this.domObj.style.visibility = 'hidden';
    this.domObj.style.border = '1px solid blue';
    this.domObj.style.backgroundColor = 'white';
    this.domObj.style.opacity = 0.50;
    this.domObj.style.mozOpacity = 0.50;
    this.domObj.style.filter = 'Alpha(opacity=50)';
    this.kaMap.theInsideLayer.appendChild( this.domObj );

    this.startx = null;
    this.starty = null;
    this.endx = null;
    this.endy = null;
    this.bMouseDown = false;
    
    
    for (var p in kaTool.prototype) {
        if (!kaRubberZoom.prototype[p])
            kaRubberZoom.prototype[p]= kaTool.prototype[p];
    }
};

/*
 * draw a box representing the query region.
 *
 * kaRubberZoom maintains the query region in four variables.  The variables are
 * assumed to be in pixel coordinates and are used to position the box.  If
 * any of the coordinates are null, clear the query box.
 */
kaRubberZoom.prototype.drawZoomBox = function() {
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
    } else {
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
 * kaRubberZoom.onmouseout( e )
 *
 * called when the mouse leaves theInsideLayer.  Terminate the query
 *
 * e - object, the event object or null (in ie)
 */
kaRubberZoom.prototype.onmouseout = function(e) {
    e = (e)?e:((event)?event:null);
    if (!e.target) e.target = e.srcElement;
    if (e.target.id == this.kaMap.domObj.id) {
        this.bMouseDown = false;
        this.startx = this.endx = this.starty = this.endy = null;
        this.drawZoomBox();
        return kaTool.prototype.onmouseout.apply(this, [e]);
    }
};

/**
 * kaRubberZoom.onmousemove( e )
 *
 * called when the mouse moves over theInsideLayer.
 *
 * e - object, the event object or null (in ie)
 */
kaRubberZoom.prototype.onmousemove = function(e) {
    e = (e)?e:((event)?event:null);
    
    if (!this.bMouseDown) {
        return false;
    }
    
    var x = e.pageX || (e.clientX +
          (document.documentElement.scrollLeft || document.body.scrollLeft));
    var y = e.pageY || (e.clientY +
                (document.documentElement.scrollTop || document.body.scrollTop));
    //if (this.type == KAMAP_RECT_QUERY) {
        var aPixPos = this.adjustPixPosition( x, y );
        
        this.endx=-aPixPos[0];
        this.endy=-aPixPos[1];
        
        this.drawZoomBox();
   // }
    return false;
}
;
/**
 * kaRubberZoom.onmousedown( e )
 *
 * called when a mouse button is pressed over theInsideLayer.
 *
 * e - object, the event object or null (in ie)
 */
kaRubberZoom.prototype.onmousedown = function(e) {
    e = (e)?e:((event)?event:null);
    if (e.button==2) {
        return this.cancelEvent(e);
    } else {
        if (this.kaMap.isIE4) document.onkeydown = kaTool_redirect_onkeypress;
        document.onkeypress = kaTool_redirect_onkeypress;
        
        this.bMouseDown=true;
        var x = e.pageX || (e.clientX +
              (document.documentElement.scrollLeft || document.body.scrollLeft));
        var y = e.pageY || (e.clientY +
                    (document.documentElement.scrollTop || document.body.scrollTop));
        var aPixPos = this.adjustPixPosition( x,y );
        this.startx=this.endx=-aPixPos[0];
        this.starty=this.endy=-aPixPos[1];
        
        this.drawZoomBox();
        
        e.cancelBubble = true;
        e.returnValue = false;
        if (e.stopPropogation) e.stopPropogation();
        if (e.preventDefault) e.preventDefault();
        return false;
    }
};

/**
 * kaRubberZoom.onmouseup( e )
 *
 * called when a mouse button is clicked over theInsideLayer.
 *
 * e - object, the event object or null (in ie)
 */
kaRubberZoom.prototype.onmouseup = function(e) {
    e = (e)?e:((event)?event:null);
    
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
    //this.kaMap.triggerEvent(KAMAP_QUERY, type, coords);
    
    this.startx = this.endx = this.starty = this.endy = null;
    this.drawZoomBox();
    //(minx, miny, maxx, maxy)
    
    if(coords[2] && coords[0] && coords[3] && coords[1]){
    		//Rubber Zoom
    		this.kaMap.zoomToExtents(coords[0],coords[1],coords[2],coords[3]  );
    	} else if (coords[0] && coords[1]){
    		//single click
    		this.kaMap.zoomIn();
    		this.kaMap.zoomTo(coords[0],coords[1]);
    	}
    return false;
};