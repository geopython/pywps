/**********************************************************************
 *
 * $Id: kaWinManager.js,v 1.2 2006/06/12 11:17:10 lbecchi Exp $
 *
 * purpose:  simulate a windows manager for all tool in the viewport (bug 1471)
 *         
 *
 * author: Lorenzo Becchi & Andrea Cappugi
 *
 * TODO:
 *   - 
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
 * kaWinManager - 
 *
 * To use kaWinManager:
 * 
 * 1) select a div to work as your Window Manager:
 * 
 *   var kaWinMan = new kaWinManager('viewport');
 * 
 * 2) create a new instance of a Window (kaWinManager)
 * 
 *   var win1 = kaWinMan.createWin('myToolbar');			
 * 
 * 3) set values for your Window 
 * params: Title (string), top left x (int), top left y (int), width (int), height  (int), 
 * resizable (boolean), draggable (boolean), min width (int), min height (int)
 * 
 *   myToolbarWin.setValues('Toolbar',20,20,200,200,true.true);
 * 
 * 4) inport an existing dom object (ex: a div) into your window:
 * 
 *   myToolbarWin.pushContent(getRawObject('toolbar'));
 * 
 * or set an inner text:
 *
 * myToolbarWin.setContent('a string');
 *
 *****************************************************************************/
 function kaWinManager( id )
 {
    //set the frame div 
	this.desktop = getRawObject( id );
	
	this.windows=new Array();
	this.activeWindow=null;

	this.minZindex = 10;

 };


kaWinManager.prototype.createWin = function( id ){
	for(var i=0;i<this.windows.length;i++){
		if(this.windows[i].id==id){
			alert('id already in use');
			return
		}
		
	}
	var newWin = new kaWindow(id,this);
	newWin.position = this.minZindex+this.windows.length;
	this.windows[this.windows.length]= newWin;
	return newWin;
};

kaWinManager.prototype.getWin = function( id ){
	for(var i=0;i<this.windows.length;i++){
			if(this.windows[i].id==id)
				return this.windows[i];
	}
};

kaWinManager.prototype.setActive = function (window) {
	this.activeWindow = window;
	this.positionChanged(window,this.windows.length+this.minZindex);
	
	for( var i=0; i<this.windows.length; i++ ) {
		this.windows[i].domObj.parent.setZindex(this.windows[i].position);
	}
};
kaWinManager.prototype.positionChanged = function ( window , position ) {
	var prevPos = window.parent.position;
	if(prevPos==position) return;
	if(prevPos<position){
		for( var i=0; i<this.windows.length; i++ ) {
			var win = this.windows[i];
			if(win!=window && win.domObj.parent.position > prevPos && win.domObj.parent.position<=position){
				win.domObj.parent.position--;
			}
		}
	} else {
		for( var i=0; i<this.windows.length; i++ ) {
			var win = this.windows[i];
			if(win!=window && win.domObj.parent.position < prevPos && win.domObj.parent.position>=position){
				win.domObj.parent.position++;
			}
		}
	}
	window.parent.position = position;
};

kaWinManager.prototype.setBackgroundImage = function ( src,x,y,w,h ) {
	
	
	this.imgObj = document.createElement('img');
	this.imgObj.id='kaBackImg';
	this.imgObj.src= src; 
	this.imgObj.style.position='absolute'; 
	this.imgObj.style.left=x+'px'; 
	this.imgObj.style.top=y+'px'; 
	this.imgObj.style.width= w + 'px'; 
	this.imgObj.style.height= h + 'px'; 
	this.imgObj.style.zIndex= 0; 
	this.desktop.appendChild( this.imgObj );
};
/******************
* Window Object 
*******************/
function kaWindow(id,winManager){
	this.domObj = null;//domObj init
	this.winManager = winManager;
	this.title = null;
	this.active = null;
	this.position = null;
	this.expanded = true;//is a window is full expanded or rolled up (default: true)
	//this.resizable=false;//if a window can be resized (default: false)
	this.resizing=false;// while a window is resised
	//this.draggable=true;//if a window can be dragged (default: true)
	
	this.pushedObj = null;//the domObj that has, or not, been 'pushed' inside.
	
	for(var i=0;i<this.winManager.windows.length;i++){
		if(this.winManager.windows[i].id==id){
			this.domObj = this.winManager.windows[i];
		}
	}
	
	if(!this.domObj) {
		this.domObj = document.createElement('div');
		this.domObj.parent=this;
		this.domObj.id= id;
		this.domObj.overflow= 'none';
		this.domObj.onclick=this.setActive;
		this.domObj.omousedown=this.setActive;
		
                this.winManager.desktop.appendChild( this.domObj );
	}
	
	
	return this;
};
kaWindow.prototype.setValues = function(title,x,y,w,h,resizable,draggable,minW,minH) {
	var headerHeight = 20;
	var footerHeight = 10;
	this.title = title;
	this.active = true;
	this.expanded = true;
	this.minW=(minW)?minW:100;
	this.minH=(minH)?minH:100;

	this.resizable=resizable;
	this.draggable=draggable;
	
	var initialized=(this.domObj.firstChild)?true:false;

	this.x = x;
	this.y = y;
	this.w = w;
	this.h = h;
	
	//set framebox
	this.domObj.style.position = 'absolute';
	this.domObj.style.left = x+'px';
	this.domObj.style.top = y+'px';
	this.domObj.style.height = h + 'px' ;
	this.domObj.style.width = w + 'px';
	this.domObj.style.zIndex = this.winManager.windows.length+this.winManager.minZindex;

	//set header
	this.headerObj = document.createElement('div');
	this.headerObj.className='kaWinHeader'; 
	this.headerObj.style.position='absolute'; 
	this.headerObj.style.top='0px'; 
	this.headerObj.style.width= w + 'px'; 
	this.headerObj.style.height= headerHeight + 'px'; 
	
		//set header title
		this.headerTitle = document.createElement('span');
		this.headerTitle.className='kaWinHeaderTitle'; 
		this.headerTitle.style.position='absolute'; 
		this.headerTitle.innerHTML= title ; 
		this.headerTitle.style.top= '0px' ; 
		this.headerTitle.style.left= '-2px' ; 
		this.headerTitle.style.width= '100%' ; 
		this.headerTitle.style.height= headerHeight-4+'px' ; 
		this.headerObj.appendChild( this.headerTitle );
		
		//set header mask (to avoid title selection)
		this.headerMask = document.createElement('div');
		this.headerMask.className='kaWinHeaderTitle'; 
		this.headerMask.style.position='absolute'; 
		this.headerMask.style.width='100%'; 
		this.headerMask.style.height= headerHeight-4+'px' ;
		this.headerMask.window= this ;
		if(this.draggable){
			this.headerMask.onmousedown= this.startDrag; 
			this.headerMask.onmouseup = this.stopDrag; 
			/*this.headerTitle.onmousemove = this.resizeMove; 
			this.headerTitle.onmouseout = this.resizeStop; */
			if (this.headerMask.captureEvents) {
			   this.headerMask.captureEvents(Event.MOUSEDOWN);
			   this.headerMask.captureEvents(Event.MOUSEUP);
			  /* this.headerTitle.captureEvents(Event.MOUSEMOVE);
			   this.headerTitle.captureEvents(Event.MOUSEOUT);*/
			}
		}
		this.headerObj.appendChild( this.headerMask );
		
		//set header button
		this.headerButton = document.createElement('span');
		this.headerButton.className='kaWinHeaderExpanderToggler'; 
		this.headerButton.style.position='absolute'; 
		this.headerButton.style.right= '1px' ; 
		this.headerButton.style.top= '0px' ; 
		this.headerButton.style.width= '10px' ; 
		this.headerButton.style.height= 7+'px' ; 
		this.headerButton.window= this ; 
		this.headerButton.onclick= this.toggleExpanded ; 
		this.headerObj.appendChild( this.headerButton );
	this.domObj.appendChild( this.headerObj );
	//set body
	this.bodyObj = document.createElement('div');
	this.bodyObj.className='kaWinBody'; 
	this.bodyObj.style.position='absolute'; 
	this.bodyObj.style.top=headerHeight+'px'; 
	this.bodyObj.style.width= w + 'px'; 
	this.bodyObj.style.height= (h - footerHeight - headerHeight) + 'px'; 
	this.domObj.appendChild( this.bodyObj );
	//set footer
	this.footerObj = document.createElement('div');
	this.footerObj.className='kaWinFooter'; 
	this.footerObj.style.position='absolute'; 
	this.footerObj.style.top=(headerHeight+parseInt(this.bodyObj.style.height))+'px'; 
	this.footerObj.style.width= w + 'px'; 
	this.footerObj.style.height= footerHeight + 'px'; 
		//set header button
		this.footerButton = document.createElement('span');
		this.footerButton.className='kaWinFooterResizer'; 
		this.footerButton.style.position='absolute'; 
		this.footerButton.style.right= '1px' ; 
		this.footerButton.style.top= '-1px' ; 
		this.footerButton.style.width= footerHeight+'px' ; 
		this.footerButton.style.height= footerHeight+'px' ; 
		this.footerButton.window= this ; 
				
		this.footerButton.onmousedown= this.resize; 
		this.footerButton.onmouseup = this.resizeStop; 
		this.footerButton.onmousemove = this.resizeMove; 
		//this.footerButton.onmouseout = this.resizeStop; 
	
		if (this.footerButton.captureEvents) {
		   this.footerButton.captureEvents(Event.MOUSEDOWN);
		   this.footerButton.captureEvents(Event.MOUSEUP);
		   this.footerButton.captureEvents(Event.MOUSEMOVE);
		  // this.footerButton.captureEvents(Event.MOUSEOUT);
		}
		

	if(this.resizable)this.footerObj.appendChild( this.footerButton );
	this.domObj.appendChild( this.footerObj );	
};


kaWindow.prototype.duplicateContent = function( obj ){
	 this.bodyObj.appendChild(obj.cloneNode(true));
};

kaWindow.prototype.setContent = function( text ){
	if(this.pushedObj) this.pushedObj.innerHTML = text;
	else this.bodyObj.innerHTML = text;
};
kaWindow.prototype.setTitle = function( text ){
	this.domObj.firstChild.firstChild.innerHTML = text;
};
kaWindow.prototype.setZindex = function( z ){
	this.position=z;
	this.domObj.style.zIndex = z;
};

kaWindow.prototype.resize = function( e ){
	
	var thisWindow=this.window;
    e = (e)?e:((event)?event:null);   
     
     thisWindow.resizing=true;
     thisWindow.initX=e.clientX;
     thisWindow.initY=e.clientY;
	 
    document.onmousemove = thisWindow.resizeMove ;
    document.onmouseup   = thisWindow.resizeStop;
	//document.onmouseout     = thisWindow.resizeStop;
	if (document.captureEvents) {	   
		   document.captureEvents(Event.MOUSEUP);
		   document.captureEvents(Event.MOUSEMOVE);
		  //document.captureEvents(Event.MOUSEOUT);
	}
		
	document.win=thisWindow;
    e=null;
};

kaWindow.prototype.resizeMove  = function( e ){
	
    var thisWindow=(this.window)?this.window:this.win;
	e = (e)?e:((event)?event:null); 
	var xMov = 0;
	var yMov = 0;
    if(thisWindow.resizing) {
		if(thisWindow.initX!=e.clientX)  xMov=(thisWindow.initX-e.clientX);
		if(thisWindow.initY!=e.clientY)  yMov=(thisWindow.initY-e.clientY);

        var oX=thisWindow.initX;
        var oY=thisWindow.initY;

		var startW= thisWindow.w; 
		var startH=thisWindow.h;

		var thisBody=thisWindow.bodyObj;
		var thisHeader=thisWindow.headerObj;
		var thisFooter=thisWindow.footerObj;
		var startW=thisWindow.domObj.style.width;
		var startWindowH=thisWindow.domObj.style.height;
		var startBodyH=thisWindow.bodyObj.style.height;
		var startH=thisWindow.domObj.style.height;
                var startFooterTop=thisWindow.footerObj.style.top;	

        	
		var newW = (parseInt(startW)-xMov);
		var newH = (parseInt(startH)-yMov);
		var newWindowH = (parseInt(startWindowH)-yMov);
		var newBodyH = (parseInt(startBodyH)-yMov);
		var newFooterTop = (parseInt(startFooterTop)-yMov);

		if(newW>=thisWindow.minW){
			thisWindow.domObj.style.width=thisBody.style.width=thisHeader.style.width=thisFooter.style.width=newW+'px';
		}
		if(newH>=thisWindow.minH){
	        thisWindow.domObj.style.height=newWindowH+'px';
			thisBody.style.height=newBodyH+'px';
			thisFooter.style.top=newFooterTop+'px';
		}
		
		if(thisBody.firstChild){
			if(newW>=thisWindow.minW)thisBody.firstChild.style.width= newW-2 +'px'; 
			if(newH>=thisWindow.minH)thisBody.firstChild.style.height= newBodyH-3 +'px'; 
		}
	
		//reset init positions
		thisWindow.initX=e.clientX;
		thisWindow.initY=e.clientY;
    }
};
kaWindow.prototype.resizeStop  = function( e ){
	var thisWindow=(this.window)?this.window:this.win;
	if(thisWindow.resizing) {
		document.onmousemove = null ;
		document.onmouseup   = null;
 		document.onmouseuout   = null;
		document.win=null;
		e = (e)?e:((event)?event:null); 
        thisWindow.resizing=false;
        //dirty stuff just for kaMap. to be reimplemented
        if(myKaMap) myKaMap.resize();
    }
};
kaWindow.prototype.toggleExpanded  = function(){
	if(this.window.expanded) {
		this.window.bodyObj.style.display='none';
		this.window.footerObj.style.display='none';
		this.window.domObj.style.height='10px';
		this.window.headerButton.style.height= 16+'px' ;
		
	} else { 
		this.window.bodyObj.style.display='block';
		this.window.footerObj.style.display='block';
		this.window.domObj.style.height=this.window.h+'px';
		this.window.headerButton.style.height= 7+'px' ;
	}
	this.window.expanded=(this.window.expanded)?false:true;

};

kaWindow.prototype.setActive = function(){
	this.parent.winManager.setActive(this);
};

kaWindow.prototype.pushContent = function( obj ){
	var pushedObj = obj;
	var targetObj = this.bodyObj;
	this.pushedObj = obj;
	targetObj.appendChild(pushedObj);
	pushedObj.style.position = 'absolute';
	pushedObj.style.height = parseInt(targetObj.style.height)-3+'px';
	pushedObj.style.width = parseInt(targetObj.style.width)-2+'px';
	pushedObj.style.top = 0;
	pushedObj.style.left = 0;
	pushedObj.className = targetObj.className;
};
kaWindow.prototype.startDrag = function(  ){
	var minX=0;
	var maxX=parseInt(getObjectWidth(this.window.winManager.desktop))-153;
	var minY=0;
	var maxY=parseInt(getObjectHeight(this.window.winManager.desktop))-23;
	//Drag.init(sensible obj, obj to drag, minX,maxX,minY,maxY)
	Drag.init(this,this.window.domObj,0,maxX,0,maxY);
};
kaWindow.prototype.stopDrag = function(  ){

};

