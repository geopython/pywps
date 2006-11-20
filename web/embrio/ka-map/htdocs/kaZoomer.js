/**********************************************************************
 *
 * $Id: kaZoomer.js,v 1.2 2006/02/07 03:19:55 pspencer Exp $
 *
 * purpose: a sliding zoom control intended to be put in the map
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original kaZoomer code was written by DM Solutions Group.
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
 * kaZoomer
 *
 * class to handle the zoom overlay
 *
 * oKaMap - the ka-Map instance to draw the zoomer on
 *
 *****************************************************************************/
function kaZoomer(oKaMap)
{
    this.kaMap = oKaMap;
    //get the viewport
    this.domObj = oKaMap.domObj;    
    //configure slider.
    this.nZoomImageHeight = 17;
    
    this.opacity = 50;
    
    this.left = 3;
    this.top = 3;
    this.right = null;
    this.bottom = null;
    
    this.zoomControlObj = null;

    //prototypes
    this.draw = kaZoomer_draw;
    this.update = kaZoomer_update;
    
    this.kaMap.registerForEvent( KAMAP_MAP_INITIALIZED, this, this.draw );
}

function kaZoomer_setPosition( left, top, right, bottom )
{
    this.left = left;
    this.top = top;
    this.right = right;
    this.bottom = bottom;
    
    if (this.zoomControlObj != null)
    {
        if (this.left != null)
        {
            oZoomControl.style.left = this.left + 'px';
        }
        else if (this.right != null)
        {
            oZoomControl.style.right = this.right + 'px';
        }
        if (this.top != null)
        {
            oZoomControl.style.top = this.top + 'px';
        }
        else if (this.bottom != null)
        {
            oZoomControl.style.bottom = this.bottom + 'px';
        }
    }
}

//handle a map zoom change from another tool
function kaZoomer_update()
{
    
    var nThumbHeight = dd.elements.zoomTrack.div.elementHeight;
    var nTrackTop = dd.elements.zoomTrack.y;
    
    var oKaMap = dd.elements.zoomTrack.div.kaZoomer.kaMap;
    var oMap = oKaMap.getCurrentMap();
    var nCurrentScale = parseInt(oMap.currentScale) + 1; //array is zero based
    var nScales = oMap.getScales().length;
    var nTrackHeight = this.nZoomImageHeight * nScales;
    var nPos = (nScales-nCurrentScale)*nThumbHeight;
    dd.elements.zoomThumb.moveTo(dd.elements.zoomThumb.x,nTrackTop + nPos);
}

//set up the slider UI.
function kaZoomer_draw()
{
    //get scale info for the current map.
    var oMap = this.kaMap.getCurrentMap();
    var nScales = oMap.getScales().length;
    var nCurrentScale = oMap.currentScale;
    var nTrackHeight = this.nZoomImageHeight * nScales;
    var nTrackMaxPosition = this.nZoomImageHeight * (nScales - 1);
    var nInitialPosition = dd.Int(this.nZoomImageHeight * 
                                  (nScales - nCurrentScale - 1));
    //widget images
    var szThumbImg = '../../ka-map/htdocs/images/slider_button.png';
    var szTrackTopImg = '../../ka-map/htdocs/images/slider_tray_top.png';
    var szTrackBottomImg = '../../ka-map/htdocs/images/slider_tray_bottom.png';
    
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
    this.zoomControlObj.style.width = 17 + "px";
    this.zoomControlObj.style.height = (nTrackHeight + 2 * this.nZoomImageHeight + 6) + "px";
    this.zoomControlObj.style.opacity = this.opacity/100;
    this.zoomControlObj.style.mozOpacity = this.opacity/100;
    this.zoomControlObj.style.filter = "Alpha(opacity="+this.opacity+")";    this.zoomControlObj.style.cursor = 'auto';    
    this.zoomControlObj.style.zIndex = 300;
    this.zoomControlObj.onmouseover = kaZoomer_onmouseover;
    this.zoomControlObj.onmouseout = kaZoomer_onmouseout;
    this.zoomControlObj.kaZoomer = this;
    this.kaMap.domObj.appendChild(this.zoomControlObj);
    
    //draw the widget
    var oZoomTrack = document.createElement( 'div' );
    oZoomTrack.id = 'zoomTrack';
    oZoomTrack.kaZoomer = this;
    oZoomTrack.style.position = 'absolute';
    oZoomTrack.style.left = '0px';
    oZoomTrack.style.top = '20px';
    oZoomTrack.style.height = parseInt(nTrackHeight) + 'px';
    oZoomTrack.style.width = '17px';
    oZoomTrack.style.backgroundColor = "#acacac";
    oZoomTrack.style.backgroundImage = "url(../../ka-map/htdocs/images/slider_tray_fill.png)";
    oZoomTrack.elementHeight = this.nZoomImageHeight;
    oZoomTrack.onclick = kaZoomer_zoomTo;
    this.zoomControlObj.appendChild(oZoomTrack);
    
    var oZoomThumb = document.createElement( 'div' );
    oZoomThumb.id = 'zoomThumb';
    oZoomThumb.style.position = 'absolute';
    oZoomThumb.style.height = '17px';
    oZoomThumb.style.width = '17px';
    oZoomThumb.style.backgroundColor = "#888888";
    oZoomThumb.innerHTML = '<img src="' + szThumbImg +'" border="0" width="17" height="17">';
    this.zoomControlObj.appendChild(oZoomThumb);

    var oZoomTrackTop = document.createElement( 'div' );
    oZoomTrackTop.id = 'zoomTrackTop';
    oZoomTrackTop.style.position = 'absolute';
    oZoomTrackTop.style.left = '0px';
    oZoomTrackTop.style.top = '17px';
    oZoomTrackTop.style.width = '17px';
    oZoomTrackTop.style.height = '3px';
    oZoomTrackTop.innerHTML = '<img src="' + szTrackTopImg +'" border="0" width="17" height="3">';
    this.zoomControlObj.appendChild(oZoomTrackTop);
    
    var oZoomTrackBottom = document.createElement( 'div' );
    oZoomTrackBottom.id = 'zoomTrackBottom';
    oZoomTrackBottom.style.position = 'absolute';
    oZoomTrackBottom.style.left = '0px';
    oZoomTrackBottom.style.top = 20 + nTrackHeight + 'px';
    oZoomTrackBottom.style.width = '17px';
    oZoomTrackBottom.style.height = '3px';
    oZoomTrackBottom.innerHTML = '<img src="' + szTrackBottomImg +'" border="0" width="17" height="3">';
    this.zoomControlObj.appendChild(oZoomTrackBottom);

    //add +/- labels
    var oZoomIn = document.createElement('div');
    oZoomIn.id = 'zoomIn';
    oZoomIn.style.position = 'absolute';
    oZoomIn.style.top = '0px';
    oZoomIn.style.left = '0px';
    oZoomIn.style.width = '17px';
    oZoomIn.style.height = '17px';
    oZoomIn.kaZoomer = this;
    oZoomIn.onclick = kaZoomer_zoomIn;
    oZoomIn.innerHTML= "<img src='../../ka-map/htdocs/images/slider_button_zoomin.png' border='0' width='17' height='17'>";
    this.zoomControlObj.appendChild(oZoomIn);

    var oZoomOut = document.createElement('div');
    oZoomOut.id = 'zoomOut';
    oZoomOut.style.position = 'absolute';
    oZoomOut.style.top = 23 + nTrackHeight + 'px';
    oZoomOut.style.left = '0px';
    oZoomOut.style.width = '17px';
    oZoomOut.style.height = '17px';
    oZoomOut.kaZoomer = this;
    oZoomOut.onclick = kaZoomer_zoomOut;
    oZoomOut.innerHTML= "<img src='../../ka-map/htdocs/images/slider_button_zoomout.png' border='0' width='17' height='17'>";
    this.zoomControlObj.appendChild(oZoomOut);

    //set up drag and drop
    ADD_DHTML('zoomThumb'+MAXOFFTOP+0+MAXOFFBOTTOM+nTrackMaxPosition+VERTICAL);
    ADD_DHTML('zoomTrack'+NO_DRAG);

    dd.elements.zoomThumb.moveTo(dd.elements.zoomTrack.x, dd.elements.zoomTrack.y + nInitialPosition);
    dd.elements.zoomThumb.setZ(dd.elements.zoomTrack.z+1);

    dd.elements.zoomTrack.addChild('zoomThumb');

    dd.elements.zoomThumb.defx = dd.elements.zoomTrack.x;
    dd.elements.zoomThumb.defy = dd.elements.zoomTrack.y;
    
    dd.elements.zoomThumb.my_DropFunc = kaZoomer_DropFunc;
    
    this.kaMap.registerForEvent( KAMAP_SCALE_CHANGED, this, this.update );
}

//wz_dragdrop.js overriden function for responding to a release of the slider
function kaZoomer_DropFunc()
{
    //move thumb to closest scale marker
    var nTrackTop = dd.elements.zoomTrack.y;
    
    var nThumbTop = dd.elements.zoomThumb.y - nTrackTop;
    var nThumbHeight = dd.elements.zoomTrack.div.elementHeight;
    
    var nNearestIndex = Math.round(nThumbTop / nThumbHeight);
    dd.elements.zoomThumb.moveTo(dd.elements.zoomThumb.x,nTrackTop +(nNearestIndex*nThumbHeight));

    //perform zoom
    var oKaMap = dd.elements.zoomTrack.div.kaZoomer.kaMap;
    var oMap = oKaMap.getCurrentMap();
    var nCurrentScale = oMap.getScales()[oMap.aScales.length - nNearestIndex - 1];
    oKaMap.zoomToScale(nCurrentScale);
}

//zoom to the level clicked in the track
function kaZoomer_zoomTo( e )
{
    e = (e)?e:((event)?event:null);
    var nClickTop = (e.layerY)?e.layerY:e.offsetY;
    //find current track height
    var oKaZoomer = dd.elements.zoomTrack.div.kaZoomer;
    var oKaMap = oKaZoomer.kaMap;
    var oMap = oKaMap.getCurrentMap();
    var nScales = oMap.getScales().length;
    var nTrackHeight = dd.Int(oKaZoomer.nZoomImageHeight) * nScales;
    
    //zoome to closest scale
    var nNearestIndex = Math.floor(nClickTop / nTrackHeight * nScales);
    var nNewScale = oMap.getScales()[oMap.aScales.length - nNearestIndex - 1];
    oKaMap.zoomToScale(nNewScale);
}

function kaZoomer_onmouseover( e )
{
    this.style.opacity = 1;
    this.style.mozOpacity = 1;
    this.style.filter = "Alpha(opacity=100)";
}

function kaZoomer_onmouseout( e )
{
    this.style.opacity = this.kaZoomer.opacity/100;
    this.style.mozOpacity = this.kaZoomer.opacity/100;
    this.style.filter = "Alpha(opacity="+this.kaZoomer.opacity+")";
}

function kaZoomer_zoomIn()
{
    this.kaZoomer.kaMap.zoomIn();
}

function kaZoomer_zoomOut()
{
    this.kaZoomer.kaMap.zoomOut();
}

function kaZoomer_alert()
{
    alert('here');
}
