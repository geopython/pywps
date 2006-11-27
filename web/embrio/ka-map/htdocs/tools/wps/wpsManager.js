/**********************************************************************
 * 
 * purpose: print a layer on the fly that  shows wps outputs          
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
 * wpsManager
 *
 * needs kaMap object
 *     
 *****************************************************************************/
function wpsManager( oKaMap ) {
 	
 	this.kaMap=oKaMap; 
 	this.qId=0;
 	this.qLayer=null;
 	this.sessionId=null;
 	this.wpsCache='';
	this.wpsUrl = '';
	this.sldUrl = '';
	
	this.identifier='';
	this.map='';
};
/******************************************************************************
 * setWpsCache
 *
 * require path to wps cache dir
 *     
 *****************************************************************************/
wpsManager.prototype.setWpsCache=function(dir){
 	this.wpsCache= dir;	
};
/******************************************************************************
 * setWpsURL
 *
 * require URL to WPS cgi executable
 *     
 *****************************************************************************/
wpsManager.prototype.setWpsURL=function(url){
 	this.wpsUrl= url;	
};
/******************************************************************************
 * setWpsURL
 *
 * require URL to WPS cgi executable
 *     
 *****************************************************************************/
wpsManager.prototype.setSldURL=function(url){
 	this.sldUrl= url;	
};
/******************************************************************************
 * query
 *
 * needs map name,extents,identifier,datainputs. Then it prepares the call
 * to wpsManager.php
 *****************************************************************************/
wpsManager.prototype.query=function(map,extents,identifier,datainputs){

  this.identifier = identifier;
  this.map = map;
  
   if (this.kaMap.sessionId)  szSessionIdP="&sessionId="+this.kaMap.sessionId;
    else szSessionIdP="";
    
    
   var params="map="+map+szSessionIdP+"&id="+this.qId;
   params += "&extents="+extents+"&identifier="+identifier;
   params += "&datainputs="+datainputs;
   params += "&wpsCache="+this.wpsCache;
   params += "&wpsUrl="+this.urlencode(this.wpsUrl);
   params += "&sldUrl="+this.urlencode(this.sldUrl);
 	//alert(params);
 	//showContent('tools/query/wpsManager.php?'+params);
   
  if (this.qLayer==null){
      this.createLayer();
    } else {
    for (i=0;i<this.qLayer.scales.length;i++)this.qLayer.scales[i]=1;
     this.qLayer.setVisibility( true );
     this.kaMap.triggerEvent( KAMAP_SCALE_CHANGED, this.kaMap.getCurrentScale()); 
     this.qLayer.setLayer(this.identifier,this.qId);
    }
   call(this.kaMap.server + '/tools/wps/wpsManager.php?'+params, this, this.queryResult);
  
};
/******************************************************************************
 * queryResult
 *
 * manage the ajax call output from query
 *     
 *****************************************************************************/
wpsManager.prototype.queryResult=function(szResult ){
	if (szResult.substr(0, 1) != "/") {
        alert(szResult);
        return false;
    }
	//alert(szResult);
 	eval(szResult);
	
	if(queryResult==0){ 
		
       this.kaMap.sessionId  = this.sessionId;
	   var cMap = this.kaMap.getCurrentMap().name;
	   
	   this.kaMap.paintLayer(this.qLayer);	   
	   
	    //this.kaMap.triggerEvent( WPS_LAYER_PAINTING, 'wait for layer to be displayed' ); 
     	this.qId++;
		return true;
     	
     }else{
//     	if(this.kaMap.getCurrentMap().getLayer("queryLayer")) this.kaMap.removeMapLayer("queryLayer");
		alert("No results for this query!");
		return false;
	 }
 };
 /******************************************************************************
 * createLayer
 *
 * create a kaMap layer
 *     
 *****************************************************************************/
wpsManager.prototype.createLayer=function(){
 
          
     this.qLayer= new _wpsLayer(this.identifier,true,100,'PNG',false,this.identifier,this.qId);
     this.kaMap.addMapLayer(this.qLayer);
	 //alert('layer to add:' +this.identifier);
 	 /*
     var legend=this.kaMap.getRawObject("group_wpsLayer");
     if(legend){
 		    
     var button= document.createElement('img');
     button.src=this.kaMap.server+"/images/legend_x.png";
     button.title="Remove Layer";
     button.alt="Remove Layer";
     button.qM=this;
     button.onclick = _queryManager_queryOnClick;
     legend.getElementsByTagName('tr')[0].appendChild(button);
     }*/
  
};
 /******************************************************************************
 * createLayer
 *
 * create a kaMap layer
 *     
 *****************************************************************************/
wpsManager.prototype.urlEncode=function(string){
	encodedHtml = escape(string);
	encodedHtml = encodedHtml.replace("/","%2F");
	encodedHtml = encodedHtml.replace(/\?/g,"%3F");
	encodedHtml = encodedHtml.replace(/=/g,"%3D");
	encodedHtml = encodedHtml.replace(/&/g,"%26");
	encodedHtml = encodedHtml.replace(/@/g,"%40");
	return encodedHtml;
}