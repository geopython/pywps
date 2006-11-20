/**********************************************************************
 *
 * $Id: kaScalebar.js,v 1.6 2006/02/07 03:19:55 pspencer Exp $
 *
 * purpose: a mapserver-based scalebar.  This still works but is more
 *          or less deprecated by scalebar (Tim Shcaub)
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original kaScalebar code was written by DM Solutions Group.
 *
 * TODO:
 * 
 *  - remove from cvs because Tim's kick's ass!
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
 * kaScalebar
 *
 * internal class to handle the scalebar
 *
 * oKaMap - the ka-Map instance to draw the scalebar for
 * szID - string, the id of a div that will contain the scalebar
 *
 *****************************************************************************/
function kaScalebar(oKaMap, szID /*, szWidth, szHeight */)
{
    this.kaMap = oKaMap;
    this.domObj = this.kaMap.getRawObject(szID);
    
    if (arguments.length > 2)
    {
        szWidth = arguments[2];
    }
    else
    {
        szWidth = this.kaMap.getObjectWidth(szID);
    }
    if (arguments.length > 3)
    {
        szHeight = arguments[3];
    }
    else
    {
        szHeight = this.kaMap.getObjectHeight(szID);
    }
      
      
    
    //create an image to hold the scalebar
    this.domImg = document.createElement( 'img' );
    this.domImg.width = szWidth;
    this.domImg.height = szHeight;
    this.domImg.style.width = szWidth + 'px';
    this.domImg.style.height = szHeight + 'px';
    this.domImg.src = this.kaMap.aPixel.src;
    this.domObj.appendChild( this.domImg );
    
    //prototypes
    this.update = kaScalebar_update;
    
    this.kaMap.registerForEvent( KAMAP_SCALE_CHANGED, this, this.update );
    this.kaMap.registerForEvent( KAMAP_MAP_INITIALIZED, this, this.update );
}

function kaScalebar_update()
{
    var scale = this.kaMap.getCurrentScale();
    this.domImg.src = this.kaMap.server + '/scalebar.php?map='+
                      this.kaMap.currentMap+'&scale='+scale;
}
