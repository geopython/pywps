/**********************************************************************
 *
 * $Id: kaToolTip.js,v 1.3 2006/08/08 20:51:35 lbecchi Exp $
 *
 * purpose: manage simple tool tips for ka-Map (bug 1374)
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
 * kaToolTip - 
 *
 * To use kaToolTip:
 * 
 * 1) add a script tag to your page:
 * 
 *   <script type="text/javascript" src="tools/kaToolTip.js"></script>
 * 
 * 2) create a new instance of kaToolTip
 * 
 *   var toolTip = new kaToolTip( oMap);
 * 
 * 3) if you want you can set an image (as the tip pointer)
 * 
 *   var offsetX=-6;//offset to move the image left-right
 *   var offsetY=-19;//offset to move the image top-bottom
 *   toolTip.setTipImage('images/tip-red.png',offsetX,offsetY);
 * 
 * 4) Set text
 * 
 *   toolTip.setText('Some text inside the tooltip');
 * 
 * 6) add it to the map
 * 
 *   toolTip.move(x,y);  //pixel coords
 * 
 * or by geo coords:
 * 
 *  toolTip.moveGeo(x,y); //geo coords
 * 
 * 7) hide the tooltip
 * 
 *  toolTip.move();
 * 
 *
 * 
 *
 *****************************************************************************/
 
 function kaToolTip( oKaMap ){
    this.kaMap = oKaMap;
    
    this.image = null;

    this.domObj = null;
    
    this.viewport = this.kaMap.domObj;
    
    this.visible= false;
    
    this.init();


 };
 
/**
 * wmsLayer.addRequestParameter( name, parameter )
 *
 * add a parameter to the baseURL safely by checking to see if the parameter
 * exists already.  This is an internal function not intended to be used
 * by other code.
 */
kaToolTip.prototype.init = function(){
	this.domObj = document.createElement('div');
	this.domObj.setAttribute('id', 'toolTip');
	
	this.minZindex = 1;
	this.coordX = null;
	this.coordY = null;
	
	
	this.viewport.appendChild(this.domObj);	
	this.domObj.style.position='absolute';

	/*Style features*/
	this.move();
	this.domObj.toolTip=this;
	this.domObj.style.zIndex=this.minZindex;

	
	/*Position features*/
	//this.domObj.onclick=this.onclick;
	
	this.setText('Wait a moment please!');
	this.kaMap.registerForEvent( KAMAP_MAP_CLICKED, this, this.onclick );
	this.kaMap.registerForEvent( KAMAP_EXTENTS_CHANGED, this, this.extentChanged );
	

};


kaToolTip.prototype.onclick=function(e){
 e = (e)?e:((event)?event:null);
this.move();

};

kaToolTip.prototype.setText = function(text){
	
	this.domObj.innerHTML = text;
		
};
kaToolTip.prototype.setInnerObj = function(obj){
	this.domObj.innerHTML = '';
	this.domObj.appendChild(obj);
		
};

kaToolTip.prototype.setTipImage = function(url,offsetX,offsetY){
	offsetX = (offsetX)?offsetX:0;
	offsetY = (offsetX)?offsetY:0;
	image = document.createElement('img');
	image.src=url;
	image.setAttribute('id', 'toolTipImage');
	image.style.position='absolute';
	image.style.zIndex=this.minZindex++;
	image.style.top='-200px';
	image.style.left='-200px';
	image.offsetX=offsetX;
	image.offsetY=offsetY;
	
	this.image = 	image;
	
	
	this.viewport.appendChild(image);
	
	
};

//move the tooltip using geo coords
kaToolTip.prototype.moveGeo = function(){
//(int [x],int [y])
	var x = parseInt(arguments[0]);
	var	y = parseInt(arguments[1]);
	var pixPos = this.kaMap.geoToPix(x,y);
	var nPixPos = this.kaMap.currentTool.adjustPixPosition( pixPos[0]*(-1), pixPos[1]*(-1) );
	var newX =nPixPos[0];
	var newY = nPixPos[1];
	
	this.move(newX,newY);
};

//move the tooltip in pixel space
kaToolTip.prototype.move = function(){
 
 // (int [x],int [y],bool [noRecenter])
 	var x = 0;
	var y = 0;
	var aPixPos = 0;
	var geoPix = 0;
	var noRecenter = false;
	
	if(arguments.length<2){
		

		/*original position*/
		//this.domObj.style.top='-'+getObjectHeight(this.domObj)+'px';
		//this.domObj.style.left= '-'+getObjectWidth(this.domObj)+'px';
		
		this.visible = false;
		
		this.domObj.style.top='-10000px';
		this.domObj.style.left= '-10000px';
		
		aPixPos = this.kaMap.currentTool.adjustPixPosition( parseInt(x) , parseInt(y) );
		var geoCoords = this.kaMap.pixToGeo( aPixPos[0],aPixPos[1]);
		this.coordX = geoCoords[0];
		this.coordY = geoCoords[1];
		
		//if(this.image)this.image.style.top = '-'+getObjectHeight(this.domObj)+'px';
		//if(this.image)this.image.style.left = '-'+getObjectWidth(this.domObj)+'px';
		if(this.image)this.image.style.top = '-100000px';
		if(this.image)this.image.style.left = '-100000px';
		//alert('move to 0');
	
	} else {
		
		x = parseInt(arguments[0]);
		y = parseInt(arguments[1]);
		
		this.visible = true;
		
		//alert('move to:' + x +' ' + y);
		
		aPixPos = this.kaMap.currentTool.adjustPixPosition( parseInt(x) , parseInt(y) );
		var geoCoords = this.kaMap.pixToGeo( aPixPos[0],aPixPos[1]);
		this.coordX = geoCoords[0];
		this.coordY = geoCoords[1];
		
		//alert('coords: '+this.coordX + ' ' +this.coordY);
		
		this.domObj.style.top=y-10+'px';//
		this.domObj.style.left=x-(getObjectWidth(this.domObj)/2)+'px';
		if(this.image)this.image.style.top = (y+this.image.offsetY)+'px';
		if(this.image)this.image.style.left = (x+this.image.offsetX)+'px';
		
		//adesso calcolo se il div sta dentro il viewport 
	 	if((arguments[2])&&arguments[2]==true)noRecenter = true;
	 	if(!noRecenter)this.recenter(this.domObj);	
	}
	

};

kaToolTip.prototype.adjustPosition = function(x,y){
 
var ny =parseInt(this.domObj.style.top)+y;
var nx =parseInt(this.domObj.style.left)+x;
	    
		this.domObj.style.top=ny+'px';//
		this.domObj.style.left=nx+'px';
		if(this.image)this.image.style.top = (parseInt(this.image.style.top)+y)+'px';
		if(this.image)this.image.style.left =(parseInt(this.image.style.left)+x)+'px';


};

kaToolTip.prototype.recenter=function(tip){


	//misuro le diemensioni in pix del tip
	var tipWidth = getObjectWidth(tip);
	var tipHeight = getObjectHeight(tip);
	var tipTop = parseInt(tip.style.top);
	var tipLeft= parseInt(tip.style.left);
	
	//prendo i dati del viewport
	var viewportWheight = tip.toolTip.kaMap.viewportHeight; 
	var viewportWidth   = tip.toolTip.kaMap.viewportWidth;
	//calcolo le posizioni di ogni angolo del tip sul viewport
	
	var topSlide=1;
	var leftSlide=1;
	if((tipTop+tipHeight)>viewportWheight) topSlide=(tipTop+tipHeight)-viewportWheight;
	
	if((tipLeft+tipWidth)>viewportWidth) leftSlide=(tipLeft+tipWidth)-viewportWidth;
	if(tipLeft<0) leftSlide=tipLeft-20;
	if(tipTop<0) topSlide=tipTop-20;
	if(topSlide!=1 || leftSlide!=1){
		
		 tip.toolTip.kaMap.slideBy(-(leftSlide+10), -(topSlide+10));
		  
		 tip.toolTip.adjustPosition(-(leftSlide+10), -(topSlide+10));
	 }

};


kaToolTip.prototype.extentChanged=function(){
	
	
	var pixPos = this.kaMap.geoToPix(this.coordX,this.coordY);
	var nPixPos = this.kaMap.currentTool.adjustPixPosition( pixPos[0]*(-1), pixPos[1]*(-1) );
	var newX =nPixPos[0];
	var newY = nPixPos[1];

	if(this.visible)this.move(newX,newY,true);
};


function encodeMyHtml(string) {
  encodedHtml = escape(string);
  encodedHtml = encodedHtml.replace("/","%2F");
  encodedHtml = encodedHtml.replace(/\?/g,"%3F");
  encodedHtml = encodedHtml.replace(/=/g,"%3D");
  encodedHtml = encodedHtml.replace(/&/g,"%26");
  encodedHtml = encodedHtml.replace(/@/g,"%40");
  return encodedHtml;
};
  
function urlDecode(sz){
	return unescape(sz).replace(/\+/g," ");
};
