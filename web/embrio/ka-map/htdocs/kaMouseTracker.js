/**********************************************************************
 *
 * $Id: kaMouseTracker.js,v 1.1 2006/07/20 13:47:11 pspencer Exp $
 *
 * purpose: a simple tool for tracking mouse movement over the map
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
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
 * <script type="text/javascript" src="kaMouseTracker.js"></script>
 * 
 * 2) create a new instance of kaMouseTracker
 * 
 * myTracker = new kaMouseTracker( myKaMap );
 * myTracker.activate();
 * 
 * 3) listen for the tracker event 
 * 
 * myKaMap.registerForEvent( KAMAP_MOUSE_TRACKER, null, myMouseMoved );
 * 
 * 4) and do something when the user requests a query
 * 
 * function myMouseMoved( eventID, coords )
 * {
 *     var pos = 'lon: ' + coords.x + ', lat: ' + coords.y;
 *     document.getElementById('mousePosition').innerHTML = pos;
 * }
 * 
 * Mouse position is reported in the coordinate system of the map.
 *
 *****************************************************************************/

// the mouse tracker event id
var KAMAP_MOUSE_TRACKER = gnLastEventId ++;

/**
 * kaMouseTracker constructor
 *
 * construct a new kaMouseTracker object for a given kaMap instance
 *
 * oKaMap - a kaMap instance
 */
function kaMouseTracker( oKaMap ) {
    kaTool.apply( this, [oKaMap] );
    this.name = 'kaMouseTracker';
    this.bInfoTool = true;
    
    for (var p in kaTool.prototype) {
        if (!kaMouseTracker.prototype[p])
            kaMouseTracker.prototype[p]= kaTool.prototype[p];
    }
};

/**
 * kaMouseTracker.onmousemove( e )
 *
 * called when the mouse moves over theInsideLayer.
 *
 * e - object, the event object or null (in ie)
 */
kaMouseTracker.prototype.onmousemove = function(e) {
    e = (e)?e:((event)?event:null);
    
    var x = e.pageX || (e.clientX +
          (document.documentElement.scrollLeft || document.body.scrollLeft));
    var y = e.pageY || (e.clientY +
                (document.documentElement.scrollTop || document.body.scrollTop));
    var a = this.adjustPixPosition( x,y );
    var p = this.kaMap.pixToGeo( a[0], a[1] );
    this.kaMap.triggerEvent(KAMAP_MOUSE_TRACKER, {x:p[0], y:p[1]});
    return false;
};