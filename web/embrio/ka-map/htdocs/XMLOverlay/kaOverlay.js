/**********************************************************************
 *
 * $Id: kaOverlay.js,v 1.5 2006/03/06 11:04:04 lbecchi Exp $
 *
 * purpose: an Object Overlay class
 *
 * author: Lorenzo Becchi & Andrea Cappugi, Piergiorgio Navone
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

function kaOverlay( oKaMap )
{
    kaTool.apply( this, [oKaMap] );
    this.name = 'kaOverlay';
	
	this.XMLloaded = false;
	
	this.overlayLayers= new Array();

	this.output;
	this.sessionId="";
	this.topLeft;
	this.imgWidth;
	this.imgHeight;
	this.imageMap="";

    for (var p in kaTool.prototype)
    {
        if (!kaOverlay.prototype[p]) 
            kaOverlay.prototype[p]= kaTool.prototype[p];
    }
    


	// The list of overlay points
	this.ovrObjects = new Array();
	
	// Register for events
    this.kaMap.registerForEvent( KAMAP_SCALE_CHANGED, this, this.scaleChanged );
    this.kaMap.registerForEvent( KAMAP_EXTENTS_CHANGED, this, this.reCenter );
	

	
}

/**
 * Act when scale change
 */
kaOverlay.prototype.scaleChanged = function( eventID, mapName ) {
// 	if (this.ovrObjects == null) return;
// 	for (var i=0; i < this.ovrObjects.length; i++) {
// 		this.ovrObjects[i].rescale();
// 	}
//	this.draw();

	this.reCenter();


}
kaOverlay.prototype.reCenter = function() {
	if(getRawObject('theInsideLayer') && getRawObject('imageMapLayer') && getRawObject('mapCodeDiv')){
		var imageMapLayer = getRawObject('imageMapLayer');
		var mapCodeDiv = getRawObject('mapCodeDiv');

		var defaultExtents = myKaMap.getCurrentMap().defaultExtents;
		var currentExtents = myKaMap.getCurrentMap().currentExtents;
		var geoExtents = myKaMap.getGeoExtents();
	
		var insideLayerLeft = myKaMap.theInsideLayer.style.left;
		var insideLayerTop = myKaMap.theInsideLayer.style.top;
		var xOrigin = myKaMap.xOrigin;
		var yOrigin = myKaMap.yOrigin;
		
		
		var topLeft = myKaMap.geoToPix( defaultExtents[0], defaultExtents[3] );
		topLeft[0] = topLeft[0] - xOrigin;
		topLeft[1] = topLeft[1] - yOrigin;
		this.topLeft = topLeft;
// 		alert(topLeft[0]+"><"+imageMapLayer.style.left);
// 		alert(topLeft[1]+"><"+imageMapLayer.style.top);
	
		var bottomRight = myKaMap.geoToPix( defaultExtents[2], defaultExtents[1] );
		bottomRight[0] = bottomRight[0] - xOrigin;
		bottomRight[1] = bottomRight[1] - yOrigin;
	
		var imgWidth =  bottomRight[0] - topLeft[0];
		this.imgWidth = imgWidth;
		var imgHeight = bottomRight[1] - topLeft[1];
		this.imgHeight = imgHeight;
		
		imageMapLayer.style.width = this.imgWidth+"px";
		imageMapLayer.style.height = this.imgHeight+"px";
		imageMapLayer.style.top = this.topLeft[1]+"px";
		imageMapLayer.style.left = this.topLeft[0]+"px";

		mapCodeDiv.style.width = this.imgWidth+"px";
		mapCodeDiv.style.height = this.imgHeight+"px";
	}
}

/**
 * Load XML from the server and update the overlay.
 *
 * xml_url	URL of th XML with points to plot
 */
kaOverlay.prototype.loadXml = function(string) {

	this.output= string;
	this.XMLloaded = true;	
	eval(string);
//	alert(this.sessionId);
	this.draw();
}


kaOverlay.prototype.init = function(url){
	//calcolo la posizione degli oggetti
	var defaultExtents = myKaMap.getCurrentMap().defaultExtents;
	var currentExtents = myKaMap.getCurrentMap().currentExtents;
	var mapName = myKaMap.getCurrentMap().name;
	var geoExtents = myKaMap.getGeoExtents();

	var insideLayerLeft = myKaMap.theInsideLayer.style.left;
	var insideLayerTop = myKaMap.theInsideLayer.style.top;
	var xOrigin = myKaMap.xOrigin;
	var yOrigin = myKaMap.yOrigin;
	

	var topLeft = myKaMap.geoToPix( defaultExtents[0], defaultExtents[3] );
	topLeft[0] = topLeft[0] - xOrigin;
	topLeft[1] = topLeft[1] - yOrigin;
	this.topLeft = topLeft;

	var bottomRight = myKaMap.geoToPix( defaultExtents[2], defaultExtents[1] );
	bottomRight[0] = bottomRight[0] - xOrigin;
	bottomRight[1] = bottomRight[1] - yOrigin;

	var imgWidth =  bottomRight[0] - topLeft[0];
	this.imgWidth = imgWidth;
	var imgHeight = bottomRight[1] - topLeft[1];
	this.imgHeight = imgHeight;

	
	//Chiamo il layer
	var xmlUrl = this.kaMap.server+"XMLOverlay/xmlgetpolygon.php";
	var stringaUrl = 
"XMLOverlay/overlay.php?xmlUrl="+xmlUrl+"&mapName="+mapName+"&sessionId="+this.sessionId+"&imgWidth="+imgWidth+"&imgHeight="+imgHeight;
// 	stringaUrl = 'XMLOverlay/overlay.php';
//	alert (stringaUrl);

	call(stringaUrl,this,this.loadXml);

}


/**
 * Load XML from the server and update the overlay.
 *
 * xml_url	URL of th XML with points to plot
 */
kaOverlay.prototype.draw = function() {

	// aggiungi i layer al viewport
	for(i=0;i<this.overlayLayers.length;i++){
		myKaMap.addMapLayer( this.overlayLayers[i] );
		
	}
	

	//disegna livello con mappa

	var insideLayerDomObj = getRawObject('theInsideLayer');
	
	div = document.createElement( 'div' );
	div.id = 'imageMapLayer';
	div.className = 'imageMapLayer';
 	div.setAttribute('style','position:absolute;z-index:100;background-color:transparent;');
    
	image = document.createElement( 'img' );
	image.src = 'images/transparent_pix.png';
//     image.src = 'images/tool_zoomin_1.png';
	image.id = 'imageMapImage';
	image.setAttribute('border','0');
 	image.setAttribute('style', 'position:absolute;z-index:2;width:'+this.imgWidth+'px;height:'+this.imgHeight+'px;');
	image.setAttribute('usemap','#overlayMap');


	/*
		<MAP name="map1">
		<Area href="index.html" shape="rect" coords="0,0,118,28" alt="home page">
		<Area href="contactus.html" shape="rect" coords="118,0,184,28" alt="contact us">
		</MAP>
	*/

	//create element
	mapCodeDiv = document.createElement( 'div' );
	mapCodeDiv.id = 'mapCodeDiv';
	mapCodeDiv.setAttribute('style', 'position:absolute;z-index:2;left:0;top:0;');

	div.appendChild( mapCodeDiv );


	div.appendChild( image );

	insideLayerDomObj.appendChild( div );
	
	this.reCenter();
	
	//insert image map code in the apposite div

// 	getRawObject('mapCodeDiv').innerHTML =  this.imageMap;
 	getRawObject('mapCodeDiv').innerHTML = this.output + this.imageMap;
//	getRawObject('mapCodeDiv').innerHTML = fakeMap;

}

kaOverlay.prototype.clear = function(){

	this.XMLloaded = false;
	this.output = null;
	this.sessionId= null;

	if(getRawObject('theInsideLayer') && getRawObject('imageMapLayer'))getRawObject('theInsideLayer').removeChild(getRawObject('imageMapLayer'));


	for(i=0;i<this.overlayLayers.length;i++){
		myKaMap.removeMapLayer( this.overlayLayers[i].name );
	}

	this.overlayLayers= new Array();

//	myKaMap.triggerEvent(KAMAP_LAYERS_CHANGED,myKaMap.currentMap);
}

kaOverlay.prototype.myOnClick = function() {
	
	alert('testo');
}

kaOverlay.prototype.showInfo = function(obj) {
	
 //	alert(obj.mionome);// <- non funge
	var string = "id: "+ obj.id + " | alt: "+ obj.alt + " | title: "+ obj.title;
	alert( string );
}

