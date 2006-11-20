/**********************************************************************
 * $Id: queryLayer.js,v 1.1 2006/06/25 17:40:39 lbecchi Exp $
 * 
 *
 * purpose: build a generalized queryLayer class (bug 1508)
 *         
 *
 * author:  Andrea Cappugi & Lorenzo Becchi 
 *
 * TODO:
 *   - all
 * 
 **********************************************************************
 *
 * Copyright (c)  2006, ominiverdi.org
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
 * queryLayer
 *
 * Implement the query layer!! 
 *  
 * 
 *
 *****************************************************************************/
function _queryLayer( szName, bVisible, opacity, imageformat, bQueryable,layers,id) {
    _layer.apply(this,[{name:szName,visible:bVisible,opacity:opacity,imageformat:imageformat,queryable:bQueryable}]);
 
 this.setGroups(layers);
 this.id=id;
 for (var p in _layer.prototype) {
        if (!_queryLayer.prototype[p])
            _queryLayer.prototype[p]= _layer.prototype[p];
    }
 };
 _queryLayer.prototype.setLayer = function(layers,id) {
 this.setGroups(layers);
 this.id=id;
 };
 _queryLayer.prototype.setGroups=function(layers){
  
  var szLayers="";
 
 for (i=0;i<layers.length-1;i++)szLayers +=layers[i].name+",";
 szLayers +=layers[layers.length-1].name;
 this.l=szLayers;
 };
 _queryLayer.prototype.setTile = function(img) {
    var l = safeParseInt(img.style.left) + this._map.kaMap.xOrigin;
    var t = safeParseInt(img.style.top) + this._map.kaMap.yOrigin;
    // dynamic imageformat
    var szImageformat = '';
    var image_format = '';
    if (this.imageformat && this.imageformat != '') {
        image_format = this.imageformat;
        szImageformat = '&i='+image_format;
    }
    if(this.tileSource == 'cache') {
        var metaLeft = Math.floor(l/(this._map.kaMap.tileWidth * this._map.kaMap.metaWidth)) * this._map.kaMap.tileWidth * this._map.kaMap.metaWidth;
        var metaTop = Math.floor(t/(this._map.kaMap.tileHeight * this._map.kaMap.metaHeight)) * this._map.kaMap.tileHeight * this._map.kaMap.metaHeight;
        var metaTileId = 't' + metaTop + 'l' + metaLeft;
        var groupsDir = (this.l != '') ? this.l.replace(/\W/g, '_') : 'def';
        var cacheDir = this._map.kaMap.webCache + this._map.name + '/' + this._map.aScales[this._map.currentScale] + '/' + groupsDir + '/def/' + metaTileId;
        var tileId = "t" + t + "l" + l;
        // the following conversion of image format to image extension
        // works for JPEG, GIF, PNG, PNG24 - others may need different treatment
        var imageExtension = this.imageformat.toLowerCase().replace(/[\de]/g, '');
        var src = cacheDir + "/" + tileId + "." + imageExtension;
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
        
//        var szGroup = '&g='+img.layer.domObj.id;
         var szGroup = '&g='+this.l;
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
            var src = this._map.kaMap.server +
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
            var src = this._map.kaMap.server +
            "/tools/query/tile_query.php" +
            q + 'map=' + this._map.name +
            '&t=' + t +
            '&l=' + l +
            szScale + szForce + szGroup + szImageformat + szTimestamp + szVersion;
        }
    }
    if (img.src != src) {
        img.style.visibility = 'hidden';
        img.src = src+"&sessionId="+this._map.kaMap.sessionId+"&id="+this.id;
    }
};