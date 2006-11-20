/**********************************************************************
 *
 * $Id: overlayLayer.js,v 1.1 2006/02/21 19:03:34 lbecchi Exp $
 *
 * purpose: an Object Overlay class 
 *
 * author: Lorenzo Becchi & Andrea Cappugi
 *
 * TODO:
 *   - many things ...
 * 
 **********************************************************************
 *
 * Copyright (c) 2005, Lorenzo Becchi & Andrea Cappugi
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

 
 function _overlayLayer( szName, bVisible, opacity, imageformat, bQueryable, scales,sessionID)
 {
    _layer.apply(this,[szName,bVisible,opacity,imageformat,bQueryable,scales]);
    this.bWidthHeight = false; //track adding width/height
    this.sessionId=sessionID;

    for (var p in _layer.prototype)
    {
        if (!_overlayLayer.prototype[p])
            _overlayLayer.prototype[p]= _layer.prototype[p];
    }

 }


_overlayLayer.prototype.setTile = function(img)
{
    var szForce = '';
    var szLayers = '';
    if (arguments[1])
        szForce = '&force=true';
    var szGroup = "&g="+img.layer.domObj.id;
    var szScale = '&s='+this._map.aScales[this._map.currentScale];
   var szSessionId='&sessionId='+this.sessionId;
    // dynamic imageformat
    var szImageformat = '';
    var image_format = '';
    if (img.layer.imageformat && img.layer.imageformat != '')
    {
        image_format = img.layer.imageformat;
        szImageformat = '&i='+image_format;
    }
 
    var l = safeParseInt(img.style.left) + this._map.kaMap.xOrigin;
    var t = safeParseInt(img.style.top) + this._map.kaMap.yOrigin;
    var src = this._map.kaMap.server+
              "/XMLOverlay/tileOverlay.php"+
              '?t='+t+
              '&l='+l+
              szScale+szForce+szGroup+szImageformat+szSessionId;
 
     if ((this.isIE4) && (image_format.toLowerCase() == "png24"))
     {
         //apply png24 hack for IE
         img.style.visibility = 'hidden';
         img.src = this._map.kaMap.aPixel.src;
         img.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='"+src+"', sizingMethod='scale')";
     }
     else
     {
         if (img.src != src)
         {
             img.style.visibility = 'hidden';
             img.src = this._map.kaMap.server+
                   "/XMLOverlay/tileOverlay.php"+
                   '?t='+t+
                   '&l='+l+
                   szScale+szForce+szGroup+szImageformat+szSessionId;
         }
     }
}