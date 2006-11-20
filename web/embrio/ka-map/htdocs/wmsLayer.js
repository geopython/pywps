/**********************************************************************
 *
 * $Id: wmsLayer.js,v 1.4 2006/04/27 20:02:51 pspencer Exp $
 *
 * purpose: an alternate layer type that can render directly from a
 *          WMS rather than from the tile cache
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * TODO:
 *   - implementation is very preliminary, missing SRS at least
 *   - layers added don't show up in the legend ...
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
 * _wmsLayer - a special type of layer object that represents a WMS layer.  It 
 *             is special because this layer renders directly from the WMS
 *             server rather than through a tile caching service.
 *
 * To use _wmsLayer:
 * 
 * 1) add a script tag to your page:
 * 
 * <script type="text/javascript" src="wmsLayer.js"></script>
 *
 * 2) create a new instance of _wmsLayer
 *
 * var l = new _wmsLayer( szName, bVisible, opacity, imageformat, bQueryable, 
 *                   server, version, layers, srs);
 *
 * 3) add it to the map
 *
 * myKaMap.addMapLayer( l );
 *
 * For instance, assuming you have a form to input the parameters required:
 *
 * function addWMSLayer()
 * {
 *     var f = document.forms.wms;
 *     var szName = f.wmsName.value;
 *     var bVisible = true;
 *     var opacity = 100;
 *     var imageformat = "image/png";
 *     var bQueryable = true;
 *     var server = f.wmsServer.value;
 *     var version = "1.1.1";
 *     var layers = f.wmsLayers.value;
 *     var srs = f.wmsSRS.value;
 *     var l = new _wmsLayer( szName, bVisible, opacity, imageformat, bQueryable, 
 *                      server, version, layers, srs);
 *     myKaMap.addMapLayer( l );
 * }
 *
 *****************************************************************************/
 
 function _wmsLayer( szName, bVisible, opacity, imageformat, bQueryable, 
                     server, version, layers, srs) {
    _layer.apply(this,[{name:szName,visible:bVisible,opacity:opacity,imageformat:imageformat,queryable:bQueryable}]);
    this.server = server;
    this.version = (version && version != '') ? version : '1.1.1';
    this.layers = layers;
    this.srs = srs;
    this.bWidthHeight = false; //track adding width/height
    
    this.baseURL = this.server;
    /* 
     * make sure the server url is terminated with a ? or not a & so we can
     * append the rest of the request without having to worry about a
     * correctly formatted url
     */
    if (this.baseURL.indexOf('?') == -1) {
        this.baseURL = this.baseURL + '?';
    } else {
        if (this.baseURL.charAt( this.baseURL.length - 1 ) == '&')
            this.baseURL = this.baseURL.slice( 0, -1 );
    }

    /*
     * required components of WMS 1.1.1 are:
     * VERSION set to version or 1.1.1 if version is empty
     * REQUEST - set to GetMap if not in the server URL
     * LAYERS - set to layers if not in the server URL
     * STYLES - not supported in this code, add to server URL yourself
     * SRS - set to srs if not in the server URL
     * BBOX - set dynamically by setTile()
     * WIDTH - set to tile height if not in the server URL
     * HEIGHT - set to tile width if not in the server URL
     * FORMAT - set to imageformat if not in the server URL
     *
     * Optional components are:
     *
     * TRANSPARENT - set to ON if not in the server URL
     * BGCOLOR - do not add this, it will interfer with transparency
     * EXCEPTIONS - set to in image if not in the server URL
     * TIME - not supported in this code, add to server URL yourself
     * ELEVATION - not supported in this code, add to server URL yourself
     * SLD (SLD only) - not supported in this code, add to server URL yourself
     * WFS (SLD only) - not supported in this code, add to server URL yourself
     */
     
    this.addRequestParameter( 'service', "&service=WMS" );
    this.addRequestParameter( 'request', "&request=GetMap" );
    this.addRequestParameter( 'version', "&version="+this.version );
    this.addRequestParameter( 'layers', "&layers=" + escape(this.layers) );
    this.addRequestParameter( 'srs', "&srs=" + this.srs );
    this.addRequestParameter( 'styles', "&styles=" );
    this.addRequestParameter( 'format', "&format=" + this.imageformat );
    this.addRequestParameter( 'transparent', '&transparent=true' );
    this.addRequestParameter( 'exceptions', '&exceptions=application/vnd.ogc.se-inimage' );
    
    for (var p in _layer.prototype) {
        if (!_wmsLayer.prototype[p])
            _wmsLayer.prototype[p]= _layer.prototype[p];
    }
};
 
/**
 * wmsLayer.addRequestParameter( name, parameter )
 *
 * add a parameter to the baseURL safely by checking to see if the parameter
 * exists already.  This is an internal function not intended to be used
 * by other code.
 */
_wmsLayer.prototype.addRequestParameter = function( name, parameter ) {
    if (this.baseURL.indexOf( name ) == -1) {
        this.baseURL = this.baseURL + parameter;
    }
};

_wmsLayer.prototype.setTile = function(img) {
    var url = this.baseURL;
    var km = this._map.kaMap;
    
    //only do this once - we don't have _map when the layer is initialized
    if (!this.bWidthHeight) {
        this.addRequestParameter( 'width', '&width='+km.tileWidth );
        this.addRequestParameter( 'height', '&height='+km.tileHeight );
    }
    
    var l = km.cellSize * (safeParseInt(img.style.left) + km.xOrigin);
    var t = -1*km.cellSize * (safeParseInt(img.style.top) + km.yOrigin);
    var r = l + km.cellSize * km.tileWidth;
    var b = t - km.cellSize * km.tileHeight;
    
    url = url + "&BBOX=" + l + "," + b + "," + r + "," + t;
    
    if (img.src != url) {
        img.style.visibility = 'hidden';
        img.src = url;
     }
};