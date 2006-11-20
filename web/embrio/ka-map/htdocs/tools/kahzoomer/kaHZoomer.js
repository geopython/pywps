/**********************************************************************
 *
 * $Id: kaHZoomer.js,v 1.1 2006/06/25 14:48:21 lbecchi Exp $
 *
 * purpose: a sliding zoom control intended to be put in the map.
 * The zoom control is horizontal.
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original kaZoomer code was written by DM Solutions Group.
 *
 * kaHZoomer created from kaZoomer by David Badke, Humanities 
 * Computing and Media Centre, University of Victoria.
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
 * kaHZoomer
 *
 * class to handle the zoom overlay
 *
 * oKaMap - the ka-Map instance to draw the zoomer on
 *
 *****************************************************************************/
function kaHZoomer(oKaMap, doOpacity)
{
    this.kaMap = oKaMap;
    this.useOpacity = doOpacity;
    //get the viewport
    this.domObj = oKaMap.domObj;    
    //configure slider.
    this.nZoomImageWidth = 17;
    
//    this.opacity = 50;
    
    this.left = 3;
    this.top = 3;
    this.right = null;
    this.bottom = null;
    
    this.zoomControlObj = null;

    //prototypes
    this.draw = kaHZoomer_draw;
    this.update = kaHZoomer_update;
    this.setPosition = kaHZoomer_setPosition;
    this.show = kaHZoomer_show;
    this.hide = kaHZoomer_hide;
    
    this.kaMap.registerForEvent( KAMAP_MAP_INITIALIZED, this, this.draw );
}

// Move the zoom control.

function kaHZoomer_setPosition( left, top, right, bottom )
{
    this.left = left;
    this.top = top;
    this.right = right;
    this.bottom = bottom;
    
    if (this.zoomControlObj != null)
    {
        if (this.left != null)
        {
            this.zoomControlObj.style.left = this.left + 'px';
        }
        else if (this.right != null)
        {
            this.zoomControlObj.style.right = this.right + 'px';
        }
        if (this.top != null)
        {
            this.zoomControlObj.style.top = this.top + 'px';
        }
        else if (this.bottom != null)
        {
            this.zoomControlObj.style.bottom = this.bottom + 'px';
        }
    }
}

// Show the zoom control.

function kaHZoomer_show() {
	if (this.zoomControlObj != null)
		this.zoomControlObj.style.display = 'block';
}

// Hide the zoom control.

function kaHZoomer_hide() {
	if (this.zoomControlObj != null)
		this.zoomControlObj.style.display = 'none';
}

//handle a map zoom change from another tool
function kaHZoomer_update()
{
    
    var nThumbWidth = dd.elements.zoomTrack.div.elementWidth;
    var nTrackLeft = dd.elements.zoomTrack.x;
    
    var oKaMap = dd.elements.zoomTrack.div.kaHZoomer.kaMap;
    var oMap = oKaMap.getCurrentMap();
    var nCurrentScale = parseInt(oMap.currentScale) + 1; //array is zero based
    var nScales = oMap.getScales().length;
    var nTrackWidth = this.nZoomImageWidth * nScales;
    var nPos = ((nCurrentScale - 1) * nThumbWidth);
    dd.elements.zoomThumb.moveTo(nTrackLeft + nPos, dd.elements.zoomThumb.y);
}

//set up the slider UI.
function kaHZoomer_draw()
{
    //get scale info for the current map.
    var oMap = this.kaMap.getCurrentMap();
    var nScales = oMap.getScales().length;
    var nCurrentScale = oMap.currentScale;
    var nTrackWidth = this.nZoomImageWidth * nScales;
    var nTrackMaxPosition = this.nZoomImageWidth * (nScales - 1);
    var nInitialPosition = dd.Int(this.nZoomImageWidth * 
                                  (nCurrentScale - 1)+17);
    //widget images
    var szThumbImg = 'images/slider_button_h.png';
    var szTrackLeftImg = 'images/slider_tray_leftb.png';
    var szTrackRightImg = 'images/slider_tray_rightb.png';
    
    //container div
    
    this.zoomControlObj = document.createElement('div');
    this.zoomControlObj.id = 'zoomControl';
    this.zoomControlObj.style.position = 'absolute';
    if (this.left != null)
    {
        this.zoomControlObj.style.left = this.left + 'px';
    }
    else if (this.right != null)
    {
        this.zoomControlObj.style.right = this.right + 'px';
    }
    if (this.top != null)
    {
        this.zoomControlObj.style.top = this.top + 'px';
    }
    else if (this.bottom != null)
    {
        this.zoomControlObj.style.bottom = this.bottom + 'px';
    }
    this.zoomControlObj.style.height = 17 + "px";
    this.zoomControlObj.style.width = (nTrackWidth + 2 * this.nZoomImageWidth + 6) + "px";
    
    if (this.useOpacity) {
	    this.zoomControlObj.style.opacity = this.opacity/100;
	    this.zoomControlObj.style.mozOpacity = this.opacity/100;
	    this.zoomControlObj.style.filter = "Alpha(opacity="+this.opacity+")";    
    }
    this.zoomControlObj.style.cursor = 'auto';    
    this.zoomControlObj.style.zIndex = 300;
    this.zoomControlObj.onmouseover = kaHZoomer_onmouseover;
    this.zoomControlObj.onmouseout = kaHZoomer_onmouseout;
    this.zoomControlObj.kaHZoomer = this;
    this.kaMap.domObj.appendChild(this.zoomControlObj);
    
    //draw the widget
    var oZoomTrack = document.createElement( 'div' );
    oZoomTrack.id = 'zoomTrack';
    oZoomTrack.kaHZoomer = this;
    oZoomTrack.style.position = 'absolute';
    oZoomTrack.style.left = '22px';
    oZoomTrack.style.top = '0px';
    oZoomTrack.style.width = parseInt(nTrackWidth) + 'px';
    oZoomTrack.style.height = '17px';
    oZoomTrack.style.backgroundColor = "#acacac";
    oZoomTrack.style.backgroundImage = "url(images/slider_tray_fill_hb.png)";
    oZoomTrack.style.backgroundPosition = "top left";
    oZoomTrack.elementWidth = this.nZoomImageWidth;
    oZoomTrack.onclick = kaHZoomer_zoomTo;
    oZoomTrack.title = 'Click to zoom, or drag slider';
    this.zoomControlObj.appendChild(oZoomTrack);
    
    var oZoomThumb = document.createElement( 'div' );
    oZoomThumb.id = 'zoomThumb';
    oZoomThumb.style.position = 'absolute';
    oZoomThumb.style.left = '0px';
    oZoomThumb.style.top = '0px';
    oZoomThumb.style.height = '17px';
    oZoomThumb.style.width = '17px';
    oZoomThumb.style.backgroundColor = "#888888";
    oZoomThumb.title = 'Drag to zoom';
    oZoomThumb.innerHTML = '<img src="' + szThumbImg +'" border="0" width="17" height="17">';
    this.zoomControlObj.appendChild(oZoomThumb);

    var oZoomTrackLeft = document.createElement( 'div' );
    oZoomTrackLeft.id = 'zoomTrackLeft';
    oZoomTrackLeft.style.position = 'absolute';
    oZoomTrackLeft.style.top = '0px';
    oZoomTrackLeft.style.left = '19px';
    oZoomTrackLeft.style.height = '17px';
    oZoomTrackLeft.style.width = '3px';
    oZoomTrackLeft.innerHTML = '<img src="' + szTrackLeftImg +'" border="0" width="3" height="17">';
    this.zoomControlObj.appendChild(oZoomTrackLeft);
    
    var oZoomTrackRight = document.createElement( 'div' );
    oZoomTrackRight.id = 'zoomTrackRight';
    oZoomTrackRight.style.position = 'absolute';
    oZoomTrackRight.style.top = '0px';
    oZoomTrackRight.style.left = 21 + nTrackWidth + 'px';
    oZoomTrackRight.style.height = '17px';
    oZoomTrackRight.style.width = '3px';
    oZoomTrackRight.innerHTML = '<img src="' + szTrackRightImg +'" border="0" width="3" height="17">';
    this.zoomControlObj.appendChild(oZoomTrackRight);

    //add +/- labels
    var oZoomIn = document.createElement('div');
    oZoomIn.id = 'zoomIn';
    oZoomIn.style.position = 'absolute';
    oZoomIn.style.top = '0px';
    oZoomIn.style.left = 26 + nTrackWidth + 'px';
    oZoomIn.style.width = '17px';
    oZoomIn.style.height = '17px';
    oZoomIn.kaHZoomer = this;
    oZoomIn.onclick = kaHZoomer_zoomIn;
    oZoomIn.title = 'Zoom in';
    oZoomIn.innerHTML= "<img src='images/slider_button_zoomin.png' border='0' width='17' height='17'>";
    this.zoomControlObj.appendChild(oZoomIn);

    var oZoomOut = document.createElement('div');
    oZoomOut.id = 'zoomOut';
    oZoomOut.style.position = 'absolute';
    oZoomOut.style.left = '0px';
    oZoomOut.style.top = '0px';
    oZoomOut.style.width = '17px';
    oZoomOut.style.height = '17px';
    oZoomOut.kaHZoomer = this;
    oZoomOut.onclick = kaHZoomer_zoomOut;
    oZoomOut.title = 'Zoom out';
    oZoomOut.innerHTML= "<img src='images/slider_button_zoomout.png' border='0' width='17' height='17'>";
    this.zoomControlObj.appendChild(oZoomOut);

    //set up drag and drop
    ADD_DHTML('zoomThumb'+MAXOFFLEFT+0+MAXOFFRIGHT+nTrackMaxPosition+HORIZONTAL);
    ADD_DHTML('zoomTrack'+NO_DRAG);

    dd.elements.zoomThumb.moveTo(dd.elements.zoomTrack.x + nInitialPosition, dd.elements.zoomTrack.y );
    dd.elements.zoomThumb.setZ(dd.elements.zoomTrack.z+1);

    dd.elements.zoomTrack.addChild('zoomThumb');

    dd.elements.zoomThumb.defx = dd.elements.zoomTrack.x;
    dd.elements.zoomThumb.defy = dd.elements.zoomTrack.y;
    
    dd.elements.zoomThumb.my_DropFunc = kaHZoomer_DropFunc;
    
    this.kaMap.registerForEvent( KAMAP_SCALE_CHANGED, this, this.update );
}

//wz_dragdrop.js overriden function for responding to a release of the slider
function kaHZoomer_DropFunc()
{
    //move thumb to closest scale marker
    var nTrackLeft = dd.elements.zoomTrack.x;
    
    var nThumbLeft = dd.elements.zoomThumb.x - nTrackLeft;
    var nThumbWidth = dd.elements.zoomTrack.div.elementWidth;
    
    var nNearestIndex = Math.round(nThumbLeft / nThumbWidth);
    dd.elements.zoomThumb.moveTo(nTrackLeft + (nNearestIndex*nThumbWidth),dd.elements.zoomThumb.y);

    //perform zoom
    var oKaMap = dd.elements.zoomTrack.div.kaHZoomer.kaMap;
    var oMap = oKaMap.getCurrentMap();
    var nCurrentScale = oMap.getScales()[nNearestIndex];
    oKaMap.zoomToScale(nCurrentScale);
}

//zoom to the level clicked in the track
function kaHZoomer_zoomTo( e )
{
    e = (e)?e:((event)?event:null);
    var nClickLeft = (e.layerX)?e.layerX:e.offsetX;
    //find current track width
    var okaHZoomer = dd.elements.zoomTrack.div.kaHZoomer;
    var oKaMap = okaHZoomer.kaMap;
    var oMap = oKaMap.getCurrentMap();
    var nScales = oMap.getScales().length;
    var nTrackWidth = dd.Int(okaHZoomer.nZoomImageWidth) * nScales;
    
    //zoom to closest scale
    var nNearestIndex = Math.floor(nClickLeft / nTrackWidth * nScales);
    var nNewScale = oMap.getScales()[nNearestIndex];
    oKaMap.zoomToScale(nNewScale);
}

function kaHZoomer_onmouseover( e )
{
	if (this.useOpacity) {
    this.style.opacity = 1;
    this.style.mozOpacity = 1;
    this.style.filter = "Alpha(opacity=100)";
	}
}

function kaHZoomer_onmouseout( e )
{
	if (this.useOpacity) {
    this.style.opacity = this.kaHZoomer.opacity/100;
    this.style.mozOpacity = this.kaHZoomer.opacity/100;
    this.style.filter = "Alpha(opacity="+this.kaHZoomer.opacity+")";
	}
}

function kaHZoomer_zoomIn()
{
    this.kaHZoomer.kaMap.zoomIn();
}

function kaHZoomer_zoomOut()
{
    this.kaHZoomer.kaMap.zoomOut();
}

function kaHZoomer_alert()
{
    alert('here');
}
