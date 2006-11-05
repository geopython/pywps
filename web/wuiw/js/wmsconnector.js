/**********************************************************************
 * 
 * purpose: init sequence for DHTML interface
 *
 * authors: Luca Casagrande (...) and Lorenzo Becchi (lorenzo@ominiverdi.com)
 * some code got from: Paul Spencer wms connector for ka-Map.
 * TODO:
 *   - a lot...
 * 
 **********************************************************************
 *
 * Copyright (C) 2006 ominiverdi.org
 *  
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *  
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 **********************************************************************/
function wmsConnector(console) {
	initDHTMLAPI();
    this.server;
	this.ajax = new Ajax;
    this.baseURL;
    this.aServer = new Array();
    this.console = console;
    this.formObj;//obj to draw form fields
    this.version = '1.0.0';
    this.sessionId;
	
	//GEO vars
	this.extent;	
	this.srs;
	this.pCoords;//pixel coords
	this.gCoords;//geo coords	
	this.agCoords= new Array();//geo coords	array

	this.XMLcode = '';//temporaneo per metterci su il GML della feature

 };
 
 wmsConnector.prototype.addServer = function (title, url){
	 this.aServer.push([title,url]);
 };
 
 
 wmsConnector.prototype.drawInitForm = function (objId){
	 
	this.formObj = getRawObject(objId);
	//set title
	var h2 = document.createElement('h2');
	h2.innerHTML = 'WMS connector';
	this.formObj.appendChild(h2);
	//set description
	var p = document.createElement('p');
	p.innerHTML = 'Use the select box here below to choose a server. Wait for remote response.';
	this.formObj.appendChild(p);
	
	var form = document.createElement('form');
	form.name='connector';
	form.action='#';
	
	//Make server select
	var select = document.createElement('select');
	select.name = 'wmsServerList';
	select.id = 'wmsServerList';
//	select.wmsConnector=this;
	select.onchange = this.connect2server;
	var j = 0;
	var opt = new Option( 'select a server', '', true, true );
	select[j++] = opt;
	for(i=0;i<this.aServer.length;i++) {
		select[j++] = new Option(this.aServer[i][0],this.aServer[i][1],false,false);
	}
	form.appendChild(select);
	var input = document.createElement('input');
	input.type='button';
	input.value='go';
	input.wmsConnector=this;
	input.onclick=this.connect2server;
	//form.appendChild(input);
	this.formObj.appendChild(form);
 };
 
 
 wmsConnector.prototype.connect2server = function (){
	 var self = wmsConnector;
	 var select = getRawObject('wmsServerList');
	 
	 var url = select[select.selectedIndex].value;
	 
	 if(url.length>0) {
		 this.baseURL = url;
	 } else {
		 alert('select a server first');
		 return;
	 } 
    if (this.baseURL.indexOf('?') == -1)
    {
        this.baseURL = this.baseURL + '?';
    }
    else
    {
        if (this.baseURL.charAt( this.baseURL.length - 1 ) == '&')
            this.baseURL = this.baseURL.slice( 0, -1 );
    }
	
    this.baseURL = this.baseURL+ "&service=WMS";
    this.baseURL = this.baseURL +  "&version="+self.version;
    this.baseURL = this.baseURL + "&request=getCapabilities";
    var connector = 'tools/proxy/proxy_xml.php?';
    var myURL = connector + 'owsURL='+myurlencode(this.baseURL);
	self.waitStart();
    self.ajax.doGet(myURL, self.parseCapabilities,'xml');
 
 };
 
 
 wmsConnector.prototype.parseCapabilities = function (xml){
	 //var tot = szText.getElemtentsByTagName('Process');
	 //alert(typeof xml);
	 var self = wmsConnector;
	 if(typeof xml=='object'){
		 //alert(xml);
		 var aProcess = xml.getElementsByTagName('Layer');
		 if(aProcess.length>0){
			// alert(this.id);
			 self.drawLayersForm(xml);
		 } else {
				alert('no Layers availalbe on this server');
		 }
	 } else {
		alert('connection error: response is not an object');
	 }
 };
 
 
 wmsConnector.prototype.drawLayersForm = function(xml){
	 	var self= wmsConnector;
		
		//get Extent (to implent BoundingBox alternative) 
		var bbox = xml.getElementsByTagName('LatLonBoundingBox')[0];
		self.extent = [bbox.getAttribute('minx'),bbox.getAttribute('miny'),bbox.getAttribute('maxx'),bbox.getAttribute('maxy')];
		var myextent = getRawObject('wmsExtent');
		if( myextent)myextent.parentNode.removeChild(myextent);
		var p = document.createElement('p');
		p.innerHTML = 'map extent: '+ self.extent;
		p.id = 'wmsExtent';
		self.formObj.appendChild(p);
		
		//get map SRS (shoud be layer related)
		self.srs = xml.getElementsByTagName('SRS')[0].textContent;
		var mywmssrs = getRawObject('wmsSRS');
		if( mywmssrs)mywmssrs.parentNode.removeChild(mywmssrs);
		var p = document.createElement('p');
		p.innerHTML = 'SRS: '+ self.srs;
		p.id = 'wmsSRS';
		self.formObj.appendChild(p);
		
		
		//get Layers
		var aProcess = xml.getElementsByTagName('Layer');
		/*var myp = getRawObject('wmsLayerP');
		if( myp)myp.parentNode.removeChild(myp);
		var p = document.createElement('p');
		p.innerHTML = 'choose a Process';
		p.id = 'wmsLayerP';
		self.formObj.appendChild(p);*/
		var myselect = getRawObject('wmsLayerList');
		if( myselect)myselect.parentNode.removeChild(myselect);
		var select = document.createElement('select');
		select.name = 'wmsLayerList';
		select.onchange = this.getWmsLayer;
		select.id = 'wmsLayerList';
		var j = 0;
		var opt = new Option( 'select a Layer', '', true, true );
		select[j++] = opt;
		for(i=0;i<aProcess.length;i++){
			var processes = aProcess[i].getElementsByTagName('Name');
			//alert(processes[0].textContent);//nodeValue,localName,tagName,textContent
			var name = processes[0].textContent;
			select[j++] = new Option(name,name,false,false);
		}
		self.formObj.appendChild(select);
		/*var input = document.createElement('input');
		input.type='button';
		input.value='go';
		input.processes=aProcess;
		input.onclick=this.getWmsLayer;
		self.formObj.appendChild(input);*/
		
		self.waitEnd();

 };
 
 
  wmsConnector.prototype.getWmsLayer = function (){
	  var self = wmsConnector;
	  var select = getRawObject('wmsLayerList');
	  var process = trim(select[select.selectedIndex].value);
	  
	   var select2 = getRawObject('wmsServerList');
	 var url = select2[select2.selectedIndex].value;
	 
	 if(process.length>0) {
		 this.baseURL = url;
	 } else {
		 alert('select a layer first');
		 return;
	 }
	
	 if (this.baseURL.indexOf('?') == -1)
    {
        this.baseURL = this.baseURL + '?';
    }
    else
    {
        if (this.baseURL.charAt( this.baseURL.length - 1 ) == '&')
            this.baseURL = this.baseURL.slice( 0, -1 );
    }
	this.baseURL = this.baseURL + "&SERVICE=WMS&REQUEST=getmap&WIDTH=640&HEIGHT=480&VERSION="+ self.version;
    this.baseURL = this.baseURL +  "&layers="+process ;
    var connector = 'tools/proxy/proxy_inline.php?';
    var myURL = connector + 'owsURL='+myurlencode(this.baseURL);
    //myURL = this.wmsConnector.addRequestParameter(myURL, 'com', "&com=getCapabilities" );
    
	//self.ajax.doGet(myURL, self.parseProcesses);
	self.waitStart();
	 getRawObject('outimg').src = myURL;
	 getRawObject('outimg').onload = self.waitEnd;
	 getRawObject('outimg').onclick = self.getCoords;
  };
  
  
  //get coords from click event on the map
 wmsConnector.prototype.getCoords =  function (e){
	  var self = wmsConnector;

	 e = (e)?e:((event)?event:null);
    if (e.button==2) {
        return;
    } else {
        var x = e.pageX || (e.clientX +
             (document.documentElement.scrollLeft || document.body.scrollLeft));
        var y = e.pageY || (e.clientY +
             (document.documentElement.scrollTop || document.body.scrollTop));
        
		//set coords
		self.pCoords =[x,y];
        self.gCoords = self.pix2geo(x,y);
        self.agCoords.push(self.gCoords);
		
		//stupid demo code to show clicked points
		var mypoints = getRawObject('mypoints');
		if( mypoints)mypoints.parentNode.removeChild(mypoints);
		var p = document.createElement('p');
		p.innerHTML = 'first click coords:' + self.agCoords[0]  + '<br> last click coords: '+ self.gCoords;
		p.id = 'mypoints';
		self.formObj.appendChild(p);
		
		//event propagation
        e.cancelBubble = true;
        e.returnValue = false;
        if (e.stopPropogation) e.stopPropogation();
        if (e.preventDefault) e.preventDefault();
        return false;
	}
}

//trasform coords from image pixel space to map geo space
wmsConnector.prototype.pix2geo =  function (pX,pY){
	  var self = wmsConnector;

	var minX = self.extent[0];
	var minY = self.extent[3];
	var maxX = self.extent[2];
	var maxY = self.extent[1];
	var dX = maxX - minX;
	var dY = maxY - minY;
	var imgW = getObjectWidth('outimg');
	var imgH = getObjectHeight('outimg');
	//(gX-minX):pX=dX:imgW;

	var gX = parseInt(minX*1000)/1000 + pX * dX/imgW;
    var gY = parseInt(minY*1000)/1000 + pY * dY/imgH;
    gX = parseInt(gX*1000)/1000;
    gY = parseInt(gY*1000)/1000;
return [gX, gY];
    
	
}

//trasform coords from image pixel space to map geo space
wmsConnector.prototype.waitStart =  function (){
	self = wmsConnector;
	var parent = getRawObject('output');
	var wait = getRawObject('wait');
	if( wait)wait.parentNode.removeChild(wait);
	var div = document.createElement('div');
	div.id = 'wait';
	div.innerHTML ='downloading... please wait';
	parent.insertBefore(div,parent.firstChild);
}

//trasform coords from image pixel space to map geo space
wmsConnector.prototype.waitEnd =  function (){
	self = wmsConnector;
	var wait = getRawObject('wait');
	if( wait)wait.parentNode.removeChild(wait);
}
