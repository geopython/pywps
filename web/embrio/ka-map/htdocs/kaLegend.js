/**********************************************************************
 *
 * $Id: kaLegend.js,v 1.36 2006/06/28 01:04:16 pspencer Exp $
 *
 * purpose: a structured legend that supports grouped layers, visibility, 
 *          expand/collapse, and queryability
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original kaLegend code was written by DM Solutions Group.  Lorenzo
 * Becchi and Andrea Cappugi contributed a bunch of code too!
 *
 * TODO:
 * 
 *   - drag and drop layer re-ordering would be nice, see script.alicio.us
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
 * To use kaLegend:
 * 
 * 1) add a script tag to your page:
 * 
 * <script type="text/javascript" src="kaLegend.js"></script>
 *
 * 2) add a <div> element to your page to contain the legend.  The div must
 *    have a unique id:
 *
 * <div id="legend"></div>
 * 
 * 3) create a new instance of kaLegend and pass it the id of the div:
 * 
 * myKaLegend = new kaLegend( 'legend' );
 *
 * and that's it :)
 * 
 *****************************************************************************/

/******************************************************************************
 * kaLegend
 * 
 * internal class to handle the legend.
 * 
 * oKaMap - the ka-Map object to attach to.
 * szID - string, the id of a div that will contain the legend
 * bStatic - boolean, true to use static legends, false to use dynamic legends
 *
 *****************************************************************************/
function kaLegend(oKaMap, szID, bStatic, options) {
    this.kaMap = oKaMap;
    this.domObj = this.kaMap.getRawObject(szID);
    this.type = (bStatic)?'static':'dynamic';
    this.expanders = [];
    this.queryCBs = [];

    this.urlBase = this.kaMap.server;
    this.urlBase += (this.urlBase!=''&&this.urlBase.substring(-1)!='/')?'':'/';

    this.showQueryCBs = true;    

    if (this.type == 'static') {
        this.domImg = document.createElement( 'img' );
        this.domImg.src = this.kaMap.aPixel.src;
        this.domObj.appendChild( this.domImg );
    } else {
        this.domObj.innerHTML = '&nbsp;';
    }
    this.showVisibilityControl = true;
    this.showQueryControl = true;
    this.showOpacityControl = true;
    this.showOrderControl = true;
    
    if (typeof options != 'undefined') {
        this.showVisibilityControl = typeof options.visibility != 'undefined' ? options.visibility : true;
        this.showQueryControl = typeof options.query != 'undefined' ? options.query : true;
        this.showOpacityControl = typeof options.opacity != 'undefined' ? options.opacity : true;
        this.showOrderControl = typeof options.order != 'undefined' ? options.order : true;
    }

    this.kaMap.registerForEvent( KAMAP_SCALE_CHANGED, this, this.update );
    this.kaMap.registerForEvent( KAMAP_MAP_INITIALIZED, this, this.update );
    this.kaMap.registerForEvent( KAMAP_LAYERS_CHANGED, this, this.draw );
    this.kaMap.registerForEvent( KAMAP_LAYER_STATUS_CHANGED, this, this.update );
};

kaLegend.prototype.update = function(eventID)
{
    var url = '';
    if (this.type == 'static') {
        this.domImg.src = 'legend.php?map=' + 
                          this.kaMap.currentMap + 
                          '&scale='+this.kaMap.getCurrentScale();
    } else {
        if (eventID == KAMAP_MAP_INITIALIZED) {
            while(this.domObj.childNodes.length > 0) {
                this.domObj.removeChild(this.domObj.childNodes[0]);
            } this.draw();
                
        } else if (eventID == KAMAP_SCALE_CHANGED) {
            var oMap = this.kaMap.getCurrentMap();
            var aLayers = oMap.getAllLayers();
            var s = this.kaMap.getCurrentScale();
            for (var i in aLayers) {
                var oLayer = aLayers[i];
                var oImg = this.kaMap.getRawObject( 'legendImg_' + oLayer.name);
                
                if (oImg) {
                    //added by Lorenzo
                    var oParent = oImg.parentNode; 
                    var tId = oImg.id;
                    var tVisibility = oImg.visibility;
                    oParent.removeChild(oImg);
                    oImg = document.createElement('img');
                    oImg.id = tId;
                    oImg.title = tId;
                    oImg.visibility = tVisibility;
                    oImg.src = 'legend.php?map=' + 
                               this.kaMap.currentMap + '&scale=' + s + '&g=' + 
                               oLayer.name;
                    oParent.appendChild(oImg);
                    expander = getRawObject('expander_'+oLayer.name);
                    expander.expandable = oImg;
                    expander.expanded = true;
                    kaLegend_expander.apply( expander );
                }
                //added by cappu
                this.setOnOffLayer(oLayer);
            }
        } else if (eventID == KAMAP_LAYER_STATUS_CHANGED) {
			var layer = arguments[1];
			for (var i=0; i<this.queryCBs.length; i++) {
				if (this.queryCBs[i].oLayer == layer) {
					this.queryCBs[i].checked = layer.visible;
				}
			}
		}
    }
};

/**
 * legend.draw( szContents )
 *
 * render the contents of a legend template into a div
 */
kaLegend.prototype.draw = function() {
/*modificato da kappu non trova url corretto se non lo metto anche qui*/
    this.urlBase = this.kaMap.server;
    this.urlBase += (this.urlBase!=''&&this.urlBase.substring(-1)!='/')?'':'/';

    var oMap = this.kaMap.getCurrentMap();

    this.expanders = [];
    this.queryCBs = [];

    if (this.domObj.childNodes.length == 0) {
        this.domObj.appendChild(this.createHeaderHTML());
    }

    var aLayers = oMap.getAllLayers();
    for (var i=(aLayers.length-1);i>=0;i--) {
        if (aLayers[i].kaLegendObj == null) {
            this.createLayerHTML( aLayers[i] );
        } else {
            try{this.domObj.removeChild( aLayers[i].kaLegendObj );}
            catch(e){};
        }
    }

    for (var i=(aLayers.length-1);i>=0;i--) {
        this.domObj.appendChild( aLayers[i].kaLegendObj );
    }

    if (this.kaMap.isIE4) {
        for(var i=0; i<this.queryCBs.length; i++) {
            this.queryCBs[i].checked = this.queryCBs[i].oLayer.visible;
        }
    }
    return;
};

kaLegend.prototype.createHeaderHTML = function() {
    var d, t, tb, tr, td, img;

    d = document.createElement( 'div' );
    d.className = 'kaLegendTitle';

    t = document.createElement( 'table' );

    t.setAttribute('width','226px');
    t.setAttribute('cellPadding', "0");
    t.setAttribute('cellSpacing', "0");
    t.setAttribute('border', "0");

    tb = document.createElement( "tbody" );

    tr = document.createElement( 'tr' );

    td = document.createElement( 'td' );
    td.style.width='26px';
    img = document.createElement( 'img' );
    img.src = '../../ka-map/htdocs/images/expand.png';
    img.alt = 'expand all';
    img.title = 'expand all';
    img.kaLegend = this;
    img.onclick = kaLegend_expandAll;
    td.appendChild( img );
    
    img = document.createElement( 'img' );
    img.src = '../../ka-map/htdocs/images/collapse.png';
    img.alt = 'collapse all';
    img.title = 'collapse all';
    img.kaLegend = this;
    img.onclick = kaLegend_collapseAll;
    td.appendChild( img );
    
    tr.appendChild( td );

    td = document.createElement( 'td' );
    td.appendChild(document.createTextNode( 'Layers' ));

    tr.appendChild( td );
    tb.appendChild(tr);
    t.appendChild(tb);
    d.appendChild(t);
    return d;
};

kaLegend.prototype.createLayerHTML = function( oLayer ) {
    var d, t, tb, tr, td, expander, cb, img, name;

    d = document.createElement( 'div' );
    d.id = 'group_' + oLayer.name;
    d.className = "kaLegendLayer";
    d.oLayer=oLayer;
    name = oLayer.name;
    if (name == '__base__') {
        name = 'Base';
    }

    t = document.createElement('table');
    t.setAttribute('width','226');
    t.setAttribute('cellPadding', "0");
    t.setAttribute('cellSpacing', "0");
    t.setAttribute('border', "0");

    tb = document.createElement( 'tbody' );
    tr = document.createElement('tr');
    td = document.createElement('td');
    td.setAttribute( "width", "9");
    
    expander = document.createElement( 'img' );
    expander.src = '../../ka-map/htdocs/images/collapse.png';
    expander.layerName = oLayer.name;
    expander.id = 'expander_'+oLayer.name;
    expander.onclick = kaLegend_expander;
    expander.expanded = true;
    
    this.expanders.push( expander );
    
    td.appendChild( expander );
    
    tr.appendChild(td);
    
    // layer visibility checkboxes
    // TODO: convert to images
    if (this.showVisibilityControl) {
        td = document.createElement('td');
        td.width = '22';
        if (oLayer.name != '__base__') {
            cb = document.createElement( 'input' );
            cb.type = 'checkbox';
            cb.name = 'layerVisCB';
            cb.value = oLayer.name;
            cb.checked = oLayer.visible;
            cb.kaLegend = this;
            cb.oLayer = oLayer;
            cb.onclick = kaLegend_toggleLayerVisibility;
            this.queryCBs.push(cb);
            td.appendChild( cb );
        }
        else {
            td.innerHTML = '&nbsp;';
        }
        tr.appendChild(td);
    }
	
	var oMap = this.kaMap.getCurrentMap();
    var aLayers = oMap.getAllLayers();
	
	//Choose if you want base element to be movable (comment on line or the other)
	//not movable
    //if (oLayer.name != '__base__')
	// movable	 
    if (aLayers.length > 1) {
        //OPACITY IMAGES
        if (this.showOpacityControl) {
            td = document.createElement('td');
            td.width = '19';
            img = document.createElement( 'img' );
            img.src = '../../ka-map/htdocs/images/sun_white.png';
            img.width = '7';
            img.alt = "Decrease layer opacity";
            img.title = "Decrease layer opacity";
            img.style.cursor ='crosshair';
            img.kaLegend = this;
            img.oLayer = oLayer;
            img.onclick = kaLegend_opacityDown;
            td.appendChild( img );
            img = document.createElement( 'img' );
            img.src = '../../ka-map/htdocs/images/sun_grey.png';
            img.width = '7';
            img.style.marginLeft = '2px';
            img.alt = "Increase layer opacity";
            img.title = "Increase layer opacity";
            img.style.cursor ='crosshair';
            img.kaLegend = this;
            img.oLayer = oLayer;
            img.onclick = kaLegend_opacityUp;
            td.appendChild( img );
            tr.appendChild(td);
        }
        if (this.showOrderControl) {
            //SHIFT LAYERS UP DOWN
            td = document.createElement('td');
            td.width = '10';
            td.style.padding = '1px';
        
            img = document.createElement( 'img' );
            img.src = '../../ka-map/htdocs/images/arrow_up.png';
            img.width = '10';
            img.height = '8';
            img.style.marginBottom = '2px';
            img.alt = "Shift Layer Up";
            img.title = "Shift Layer Up";
            img.style.cursor ='crosshair';
            img.kaLegend = this;
            img.oLayer = oLayer;
            img.myDiv = d;
            img.onclick = kaLegend_moveLayerUp;
            td.appendChild( img );
        
            img = document.createElement( 'img' );
            img.src = '../../ka-map/htdocs/images/arrow_down.png';
            img.width = '10';
            img.height = '8';
            img.alt = "Shift Layer Down";
            img.title = "Shift Layer Down";
            img.style.cursor ='crosshair';
            img.kaLegend = this;
            img.oLayer = oLayer;
            img.myDiv = d;
            img.onclick = kaLegend_moveLayerDown;
            td.appendChild( img );
        
            tr.appendChild(td);
        }
    }

    if (this.showQueryControl) {
        //layer queryable images
        td = document.createElement('td');
        td.width = '14';
    
        img = document.createElement( 'img' );
        img.width = '14';
        img.height = '14';
        if (oLayer.queryable) {
            if (oLayer.isQueryable()) {
                img.src = '../../ka-map/htdocs/images/icon_query_on.png';
            } else {
                img.src = '../../ka-map/htdocs/images/icon_query_off.png';
            }
            img.onmouseover = kaLegend_queryOnMouseOver;
            img.onmouseout = kaLegend_queryOnMouseOut;
            img.onclick = kaLegend_queryOnClick;
            img.oLayer = oLayer;
        } else {
            img.src = '../../ka-map/htdocs/images/icon_query_x.png';
        }
        
        td = document.createElement( 'td' );
        td.appendChild(img);
        td.width = '16';
        tr.appendChild(td);
    }
    td = document.createElement( 'td' );
    td.innerHTML = name;
    tr.appendChild(td);
    tb.appendChild(tr);
    
    t.appendChild( tb );
    d.appendChild(t);
    
    img = document.createElement( 'img' );
    img.id = 'legendImg_' + oLayer.name;
    img.src = this.urlBase +  'legend.php?map='+this.kaMap.currentMap+'&scale='+this.kaMap.getCurrentScale()+'&g='+oLayer.name;
	/*modificato da kappu, nel cvs dimentica di aggiungere immagine */ 
	d.appendChild(img);
    expander.expandable = img;
    oLayer.kaLegendObj = d;
    kaLegend_expander.apply( expander );
	//adedd by cappu
	this.setOnOffLayer(oLayer,oLayer.isVisible);   
};

function kaLegend_toggleLayerQueryable() {
    this.kaLegend.kaMap.setLayerQueryable( this.value, this.checked );
};

function kaLegend_queryOnMouseOver() {
    if (this.oLayer.queryable) {
        this.src = '../../ka-map/htdocs/images/icon_query_over.png';
    }
};

function kaLegend_queryOnMouseOut() {
    if (this.oLayer.queryable) {
        if (this.oLayer.isQueryable()) {
            this.src = '../../ka-map/htdocs/images/icon_query_on.png';
        } else {
            this.src = '../../ka-map/htdocs/images/icon_query_off.png';
        }
    }
};

function kaLegend_queryOnClick() {
    if (this.oLayer.queryable) {
        if (this.oLayer.isQueryable()) {
            this.oLayer.setQueryable( false );
            this.src = '../../ka-map/htdocs/images/icon_query_off.png';
        } else {
            this.oLayer.setQueryable( true );
            this.src = '../../ka-map/htdocs/images/icon_query_on.png';
        }
    }
};

function kaLegend_toggleLayerVisibility() {
    this.kaLegend.kaMap.setLayerVisibility( this.value, this.checked );
};

function kaLegend_expander() {
    this.expanded = !this.expanded;
    
    this.src = (this.expanded)?'../../ka-map/htdocs/images/collapse.png':'../../ka-map/htdocs/images/expand.png';
    this.expandable.style.display = (this.expanded)?'block':'none';
};

function kaLegend_expandAll() {
    var kaLeg = this.kaLegend;
    for (var i=0; i<kaLeg.expanders.length; i++) {
        kaLeg.expanders[i].expanded = false;
        kaLegend_expander.apply( kaLeg.expanders[i] );
    }
};

function kaLegend_collapseAll() {
    var kaLeg = this.kaLegend;
    if (kaLeg.expanders) {
        for (var i=0; i<kaLeg.expanders.length; i++) {
            kaLeg.expanders[i].expanded = true;
            kaLegend_expander.apply( kaLeg.expanders[i] );
        }
    }
};


function kaLegend_opacityDown() {
    var opc;
    opc=this.oLayer.opacity-10;
    this.kaLegend.kaMap.setLayerOpacity(this.oLayer.name, opc );  
};

function kaLegend_opacityUp() {    
    var opc;
    opc=this.oLayer.opacity+10;
    this.kaLegend.kaMap.setLayerOpacity(this.oLayer.name, opc );
};

/*added by cappu used to hide layer not visible at current scala*/
kaLegend.prototype.setOnOffLayer = function(l) {
    if (l.isVisible()) {
        if (l.kaLegendObj) {
            l.kaLegendObj.style.display='block';        
        } 
    } else {
        if(l.kaLegendObj) {
            l.kaLegendObj.style.display='none';
        }
    }
};

/**
* kaLegend_moveLayerDown 
* About a specific Group of layer, it moves the corresponding Legend div and 
*  the Viewport div to the next one
* @private 
* @author Lorenzo Becchi
*/

function kaLegend_moveLayerDown() {
    var myLayer= this.oLayer;
    var leg=this.myDiv.parentNode;
    var myDiv = this.myDiv;
    var lowerDiv = findLowerDiv(myDiv);
    
    if(lowerDiv && lowerDiv.className=='kaLegendLayer') {
        //search correspondant checbox to prevent IE uncheck on move bug
        var aCheckbox = document.getElementsByTagName('input');
        var checkboxStatusUp=null;
        var checkboxStatusDown=null;
        var checkboxUp=null;
        var checkboxDown=null;
        for(var i=0;i<aCheckbox.length;i++) {
            var inputTag = aCheckbox[i];
            if(inputTag.value == myDiv.id.replace(/\bgroup_/, '')) {
                checkboxUp = inputTag;
                checkboxStatusUp = checkboxUp.checked;
            }
            if(inputTag.value == lowerDiv.id.replace(/\bgroup_/, '')) {
                checkboxDown =inputTag;
                checkboxStatusDown = inputTag.checked;
            }
        }
        
        // move legend group div  (need to do it two allow hidden layers syncing)
        var proxyMy = myDiv.cloneNode(true);
        var proxyLower = lowerDiv.cloneNode(true);
        myDiv.parentNode.insertBefore( proxyMy , myDiv );
        myDiv.parentNode.insertBefore( proxyLower , lowerDiv );
        myDiv.parentNode.replaceChild( lowerDiv , proxyMy );
        myDiv.parentNode.replaceChild( myDiv , proxyLower );
        
        //confirm checbox status to prevent IE uncheck on move bug
        if(checkboxUp)checkboxUp.checked = checkboxStatusUp;
        if(checkboxDown)checkboxDown.checked = checkboxStatusDown;
	
		//added by cappu,set zindex order of div layer in vieport
		for  (i=0,n=leg.childNodes.length;i< leg.childNodes.length;i++) {
			var child= leg.childNodes[i];
			if(child && child.className=='kaLegendLayer') {
				child.oLayer.zIndex=(n);
				n--;
			}
		}
		
		//call function to redrow
		this.kaLegend.kaMap.setMapLayers();
    } else {
        alert('this layer can\'t go farther down');
    } 
};

/**
 * kaLegend_moveLayerUp
 * About a specific Group of layer, it moves the corresponding Legend div and 
 * the  Viewport div to the previous one
 * @private 
 * @author Lorenzo Becchi
 */
function kaLegend_moveLayerUp() {
    var myLayer= this.oLayer;
    var leg=this.myDiv.parentNode;
    var myDiv = this.myDiv;
    var upperDiv = findUpperDiv(myDiv);
    
     if(upperDiv && upperDiv.className=='kaLegendLayer') {
        //search correspondant checbox to prevent IE uncheck on move bug
        var aCheckbox = document.getElementsByTagName('input');
        var checkboxStatusUp=null;
        var checkboxStatusDown=null;
        var checkboxUp=null;
        var checkboxDown=null;
        for(var i=0;i<aCheckbox.length;i++) {
            var inputTag = aCheckbox[i];
            if(inputTag.value == upperDiv.id.replace(/\bgroup_/, '')) {
                checkboxUp = inputTag;
                checkboxStatusUp = checkboxUp.checked;
            }
            if(inputTag.value == myDiv.id.replace(/\bgroup_/, '')) {
                checkboxDown =inputTag;
                checkboxStatusDown = inputTag.checked;
            }
        }
        
        // switch legend groups div (need to do it two allow hidden layers syncing)
        var proxyMy = myDiv.cloneNode(true);
        var proxyUpper = upperDiv.cloneNode(true);      
        myDiv.parentNode.insertBefore( proxyMy , myDiv );
        myDiv.parentNode.insertBefore( proxyUpper , upperDiv );
        myDiv.parentNode.replaceChild( upperDiv , proxyMy );
        myDiv.parentNode.replaceChild( myDiv , proxyUpper );
        
        //confirm checbox status to prevent IE uncheck on move bug
        if(checkboxUp)checkboxUp.checked = checkboxStatusUp;
        if(checkboxDown)checkboxDown.checked = checkboxStatusDown;
		
		//added by cappu,set zindex order of div layer in vieport
		for  (i=0,n=leg.childNodes.length;i< leg.childNodes.length;i++) {
		    var child= leg.childNodes[i];
		    if(child && child.className=='kaLegendLayer') {
				child.oLayer.zIndex=(n);
				n--;
			}
		}
		//call function to redrow
		this.kaLegend.kaMap.setMapLayers();
    } else {
        alert('this layer can\'t go farther up');
    }
};

/**
* findLowerDiv
* find recursively nextSibling in legend list
* @private 
* @author Lorenzo Becchi
*/
function findLowerDiv(div) {
	lDiv = div.nextSibling;
	if(lDiv && lDiv.className=='kaLegendLayer' && lDiv.style.display=='none') {
		findLowerDiv(lDiv);
	}
	return lDiv;
};
/**
* findUpperDiv
* find recursively previousSibling in legend list
* @private 
* @author Lorenzo Becchi
*/
function findUpperDiv(div){
	uDiv = div.previousSibling;
	if(uDiv && uDiv.className=='kaLegendLayer' && uDiv.style.display=='none'){
		findUpperDiv(uDiv);
	}
	return uDiv;
}