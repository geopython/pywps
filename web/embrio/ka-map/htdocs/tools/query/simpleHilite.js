/**********************************************************************
 * 
 * purpose: build a simple hilite system for serach end query systems          
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
 * simple hilite
 *
 * recive map name,layer name and extent and hilite requested shape 
 *     
 *****************************************************************************/
function simpleHilite( oKaMap ) {
 	
 	this.kaMap=oKaMap; 
 	this.qId=0;
 	this.qLayer=null;
 	this.sessionId=null;
};

simpleHilite.prototype.query=function(map,layer,extents,searchString,shapeIndex,tileIndex){
  
  
  
   if (this.kaMap.sessionId)  szSessionIdP="&sessionId="+this.kaMap.sessionId;
    else szSessionIdP="";
    
    
   var params="map="+map+"&layer="+layer+"&id="+this.qId +szSessionIdP;
   params += "&extents="+extents+"&searchstring="+searchString;
   params += "&sIndex="+shapeIndex+"&tIndex="+tileIndex;
 	//alert(params);
 	//showContent('tools/query/simpleHilite.php?'+params);
   
  if (this.qLayer==null){
      this.createLayer();
    } else {
    for (i=0;i<this.qLayer.scales.length;i++)this.qLayer.scales[i]=1;
     this.qLayer.setVisibility( true );
     this.kaMap.triggerEvent( KAMAP_SCALE_CHANGED, this.kaMap.getCurrentScale()); 
     this.qLayer.setLayer(layers,this.qId);
    }
   call('tools/query/simpleHilite.php?'+params, this, this.queryResult);
  
};
simpleHilite.prototype.queryResult=function(szResult ){
 
 	eval(szResult);
	if(queryResult==0){ 
		
       this.kaMap.sessionId  = this.sessionId;
	   var cMap = this.kaMap.getCurrentMap().name;
	   this.kaMap.paintLayer(this.qLayer);
	    	    
     	this.qId++;
     	
     }else{
//     	if(this.kaMap.getCurrentMap().getLayer("queryLayer")) this.kaMap.removeMapLayer("queryLayer");
		alert("No results for this query!");
	 }
 };
simpleHilite.prototype.createLayer=function(){
 
          
     this.qLayer= new _queryLayer("queryLayer",true,100,'PNG',false,layers,this.qId);
     this.kaMap.addMapLayer(this.qLayer);
 	 
     var legend=this.kaMap.getRawObject("group_queryLayer");
    /* if(legend){
 		    
     var button= document.createElement('img');
     button.src=this.kaMap.server+"/images/legend_x.png";
     button.title="Remove Layer";
     button.alt="Remove Layer";
     button.qM=this;
     button.onclick = _queryManager_queryOnClick;
     legend.getElementsByTagName('tr')[0].appendChild(button);
     }*/
  
};
simpleHilite_queryOnClick=function(){
  
     for (i=0;i<this.qM.qLayer.scales.length;i++)this.qM.qLayer.scales[i]=0;
     this.qM.qLayer.setVisibility( false );
     this.qM.kaMap.triggerEvent( KAMAP_SCALE_CHANGED, this.qM.kaMap.getCurrentScale() ); 
       if(this.qM.resultDiv )  this.qM.injectResult('');
 };
 