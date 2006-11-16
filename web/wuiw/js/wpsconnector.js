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
function wpsConnector(console) {
	initDHTMLAPI();
    this.server;
	this.ajax = new Ajax;
    this.baseURL;
    this.aServer = new Array();
    this.console = console;
    this.formObj;//obj to draw form fields
    this.version = '0.4.0';
    this.sessionId;
	
	//data sources Connector Object
	this.owsConnector = owsConnector;

	//temp XML storer
	this.XMLcode = '';

 };
 
 wpsConnector.prototype.addServer = function (title, url){
	 this.aServer.push([title,url]);
 };
 
 
 wpsConnector.prototype.drawInitForm = function (objId){
	 
	this.formObj = getRawObject(objId);
	//set title
	var h2 = document.createElement('h2');
	h2.innerHTML = 'WPS connector';
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
	select.name = 'wpsserverlist';
	select.id = 'wpsserverlist';
//	select.wpsConnector=this;
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
	input.onclick=this.connect2server;
	//form.appendChild(input);
	this.formObj.appendChild(form);
 };
 
 
 wpsConnector.prototype.connect2server = function (){
	 var self = wpsConnector;
	 var select = getRawObject('wpsserverlist');
	 
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
	
    this.baseURL = this.baseURL+ "&service=wps";
    this.baseURL = this.baseURL + "&request=GetCapabilities";
    this.baseURL = this.baseURL +  "&version="+self.version;

    var connector = 'tools/proxy/proxy_xml.php?';
    var myURL = connector + 'owsURL='+myurlencode(this.baseURL);
	self.waitStart();
    self.ajax.doGet(myURL, self.parseCapabilities,'xml');
 
 };
 
 
 wpsConnector.prototype.parseCapabilities = function (xml){
	 //var tot = szText.getElemtentsByTagName('Process');
	 //alert(typeof xml);
	 var self = wpsConnector;
	 if(typeof xml=='object'){
		 //alert(xml);
		 var aProcess = xml.getElementsByTagName('Process');
		 if(aProcess.length>0){
			// alert(this.id);
			 self.drawProcessForm(xml);
		 } else {
				alert('no Processes availalbe on this server');
		 }
	 } else {
		alert('connection error: response is not an object');
	 }
 };
 
 
 wpsConnector.prototype.drawProcessForm = function(xml){
	 	var self= wpsConnector;
	 	var aProcess = xml.getElementsByTagName('Process');
		 
		var myp = getRawObject('pProcess');
		if( myp)myp.parentNode.removeChild(myp);
		var p = document.createElement('p');
		p.innerHTML = 'choose a Process';
		p.id = 'pProcess';
		self.formObj.appendChild(p);
		var myselect = getRawObject('processlist');
		if( myselect)myselect.parentNode.removeChild(myselect);
		var select = document.createElement('select');
		select.name = 'processlist';
		select.onchange = this.getProcess;
		select.id = 'processlist';
		var j = 0;
		var opt = new Option( 'select a Process', '', true, true );
		select[j++] = opt;
		for(i=0;i<aProcess.length;i++){
			var processes = aProcess[i].getElementsByTagName('Identifier');
			//alert(processes[0].textContent);//nodeValue,localName,tagName,textContent
			var name = processes[0].textContent;
			select[j++] = new Option(name,name,false,false);
		}
		self.formObj.appendChild(select);
		/*var input = document.createElement('input');
		input.type='button';
		input.value='go';
		input.processes=aProcess;
		input.onclick=this.getProcess;
		//self.formObj.appendChild(input);*/
		self.waitEnd();

 };
 
 
  wpsConnector.prototype.getProcess = function (){
	  var self = wpsConnector;
	  var select = getRawObject('processlist');
	  var process = trim(select[select.selectedIndex].value);
	  
	   var select2 = getRawObject('wpsserverlist');
	 var url = select2[select2.selectedIndex].value;
	 
	 if(process.length>0) {
		 this.baseURL = url;
	 } else {
		 alert('select a process first');
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
	this.baseURL = this.baseURL + "&service=wps&request=DescribeProcess&version="+ self.version;
    this.baseURL = this.baseURL +  "&identifier="+process ;
    var connector = 'tools/proxy/proxy_xml.php?';
    var myURL = connector + 'owsURL='+myurlencode(this.baseURL);
    //myURL = this.wpsConnector.addRequestParameter(myURL, 'com', "&com=getCapabilities" );
    self.waitStart();
	self.ajax.doGet(myURL, self.parseProcesses,'xml');
	 
  };
  
  
  wpsConnector.prototype.parseProcesses = function(xml){
	  var self = wpsConnector;
	 if(typeof xml=='object'){
		 //alert(xml);
		 var aProcess = xml.getElementsByTagName('ProcessDescription');
		 if(aProcess.length>0){
			// alert(this.id);
			 self.drawProcessDescription(xml);
		 } else {
				alert('no Processes availalbe on this server');
		 }
	 } else {
		alert('connection error: response is not an object');
	 }
	  
  };
  
   wpsConnector.prototype.drawProcessDescription = function (xml) {
	   var self = wpsConnector;
	   var description = getRawObject('description');
	   
	   var identifier = xml.getElementsByTagName('Identifier')[0].textContent;
	   var title = xml.getElementsByTagName('Title')[0].textContent;
	   var labstract = xml.getElementsByTagName('Abstract')[0].textContent;
	   
	   var myh2 = getRawObject('myh2');
		if( myh2)myh2.parentNode.removeChild(myh2);
	   var h2 = document.createElement('h2');
	   h2.innerHTML = 'Identifier: ' + identifier;
	   h2.id = 'myh2';
	   description.appendChild(h2);
	   //clean and add subtitle
	   var myh3 = getRawObject('myh3');
	   if( myh3)myh3.parentNode.removeChild(myh3);
	   var h3 = document.createElement('h3');
	   h3.innerHTML = 'Title: ' + title;
	   h3.id = 'myh3';
	   description.appendChild(h3);
	   //clean and add paragraph
	   var myp = getRawObject('myp');
	   if( myp)myp.parentNode.removeChild(myp);
	   var p = document.createElement('p');
	   p.innerHTML = labstract;
	   p.id = 'myp';
	   description.appendChild(p);
	   self.waitEnd();

	  //draw form for this function

	  var hr = document.createElement('hr');
	  
	  //here I have to put a function to create the form dom object 
	  //keep informations from metadata inside XML object
	  var processForm = self.buildFormFromMetadata( xml );
	  self.formObj.appendChild(hr);
	  var input = document.createElement('input');
		input.type='button';
		input.value='execute';
		input.onclick=this.wpsExecute;
		self.formObj.appendChild(input);
	  //appendChild(p);
	  //
   };

   wpsConnector.prototype.buildFormFromMetadata = function( xml ){
	   //create object container
	   var domObj = document.createElement('div');
	   domObj.id='formContainer';
	   
	   var self = wpsConnector;
	   //get Metadata
	   var aMetadata = xml.getElementsByTagName('metadata');
	   //select metatada with interface="formInput"
	   for(i=0;i<aMetadata.length;i++){
		   var metadata = aMetadata[i];
		   var metaType = metadata.getAttribute('type');
		   if(metaType=='formInput'){
			   //set all values
		 	  var description = metadata.textContent;
		   }
	   }
	   return domObj;
   };
   
   wpsConnector.prototype.wpsExecute = function(){
	   var self = wpsConnector;
	  var select = getRawObject('processlist');
	  var process = trim(select[select.selectedIndex].value);
	  
	   var select2 = getRawObject('wpsserverlist');
	 var url = select2[select2.selectedIndex].value;
	 
	 if(process.length>0) this.baseURL = url;
	 else { 
		 alert('select a process first'); return;
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
		//?service=wps&version=0.4.0&request=Execute
		//&Identifier=visibility2&datainputs=....
		//&status=true&store=true
		var datainputs = 'x,603456,y,4922763,maxdist,1000,observer,3';
		this.baseURL = this.baseURL + "&service=wps&request=Execute&version="+ self.version;
		this.baseURL = this.baseURL +  "&identifier="+process ;
		this.baseURL = this.baseURL +  "&datainputs="+datainputs ;
		this.baseURL = this.baseURL +  "&status=true&store=true" ;
		var connector = 'tools/proxy/proxy_xml.php?';
		var myURL = connector + 'owsURL='+myurlencode(this.baseURL);
		//self.waitStart();
		self.ajax.doGet(myURL, self.parseExecute,'xml');
   }

wpsConnector.prototype.parseExecute = function (xml){
	 //var tot = szText.getElemtentsByTagName('Process');
	 //alert(typeof xml);
	 var self = wpsConnector;
	 if(typeof xml=='object'){
		 //alert(xml);
		 var aProcess = xml.getElementsByTagName('ProcessOutputs');
		 if(aProcess.length>0){
			// alert(this.id);
			 self.drawExecuteOut(xml);
		 } else {
				alert('no ProcessOutputs available on this server');
		 }
	 } else {
		alert('connection error: response is not an object');
	 }
 };
 wpsConnector.prototype.drawExecuteOut = function (xml){
	 var self= wpsConnector;
	 var ComplexValueReference = xml.getElementsByTagName('ComplexValueReference');
	 var outFormat = ComplexValueReference[0].getAttribute('format');
	 var outReference = ComplexValueReference[0].getAttribute('ows:reference');
	 alert(' Image url: ' + outReference + ' | image path: ' + outFormat );
	 getRawObject('outimg').src = 'tools/proxy/proxy_mime.php?mime='+ unescape('image/png').replace(/\+/g," ") + '&wpsURL='+unescape(outReference).replace(/\+/g," ");
	 getRawObject('debug').innerHTML = '<a href="tools/proxy/proxy_mime.php?mime='+ unescape('image/png').replace(/\+/g," ") + '&wpsURL='+unescape(outReference).replace(/\+/g," ")+'" target="_blank">proxied image (not working)</a> <a href="'+outReference+'" target="_blank">result image (working)</a>';
 } 
//trasform coords from image pixel space to map geo space
wpsConnector.prototype.waitStart =  function (){
	self = wpsConnector;
	var parent = getRawObject('output');
	var wait = getRawObject('wait');
	if( wait)wait.parentNode.removeChild(wait);
	var div = document.createElement('div');
	div.id = 'wait';
	div.innerHTML ='downloading... please wait';
	parent.insertBefore(div,parent.firstChild);
}

wpsConnector.prototype.addOwsConnector =  function (owsConnector){
		self = wpsConnector;
		self.owsConnector= owsConnector;
}
//trasform coords from image pixel space to map geo space
wpsConnector.prototype.waitEnd =  function (){
	self = wpsConnector;
	var wait = getRawObject('wait');
	if( wait)wait.parentNode.removeChild(wait);
}
