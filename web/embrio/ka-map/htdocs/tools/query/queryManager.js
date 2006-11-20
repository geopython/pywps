/**********************************************************************
 * $Id: queryManager.js,v 1.5 2006/07/12 16:22:57 acappugi Exp $
 * 
 *
 * purpose: build a generalized query manager class (bug 1508)
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
 * queryManager
 *
 * used manage the query system!! 
 *  
 *  type: 0 point query | 1 box query | 2 alphanumeric query
 *  query result: 
 *****************************************************************************/
function _queryManager( oKaMap ) {
 	
 	this.kaMap=oKaMap; 
 	if(arguments[1]) this.resultDiv=this.kaMap.getRawObject(arguments[1]);
 	this.qId=0;
 	this.qLayer=null;
 	this.sessionId=null;
 	this.init();
 	this.kaMap.registerForEvent( KAMAP_QUERY, this,  this.spatialQuery);
};
 _queryManager.prototype.init=function(){
 /*inserisco l'oggetto kaMpa in uno spam*/
 	var sp= document.createElement('span');
 	sp.qM= this;
 	sp.id="qKamap";
 	document.getElementsByTagName('body')[0].appendChild(sp);
};
 _queryManager.prototype.spatialQuery=function(eventID, queryType, coords ){
  
    var szLayers = '';
    var layers = this.kaMap.getCurrentMap().getQueryableLayers();
    if(layers.length==0) {
     alert("No queryable layers at this scale and extent");
     return;
    }
    szLayers="";
    for (var i=0;i<(layers.length-1);i++) {
        szLayers +=  layers[i].name+",";
     } 
     szLayers +=  layers[(layers.length-1)].name+",";
    
    if (this.qLayer==null){
      this.createLayer();
    }
    else {
    for (i=0;i<this.qLayer.scales.length;i++)this.qLayer.scales[i]=1;
     this.qLayer.setVisibility( true );
     this.kaMap.triggerEvent( KAMAP_SCALE_CHANGED, this.kaMap.getCurrentScale()); 
     this.qLayer.setLayer(layers,this.qId);
    }

    var extent = this.kaMap.getGeoExtents();
    var scale = this.kaMap.getCurrentScale();
    var cMap = this.kaMap.getCurrentMap().name;
    if (this.kaMap.sessionId)  szSessionIdP="&sessionId="+this.kaMap.sessionId;
    else szSessionIdP="";
	var params='map='+cMap+'&q_type='+queryType+'&scale='+scale+'&groups='+szLayers+'&coords='+coords+'&extent='+extent[0]+'|'+extent[1]+'|'+extent[2]+'|'+extent[3]+szSessionIdP+"&id="+this.qId;
	call('tools/query/query.php?'+params, this, this.queryResult);
};
_queryManager.prototype.queryResult=function(szResult ){
 
 	eval(szResult);
	if(queryResult==0)
	{ 
		
       this.kaMap.sessionId  = this.sessionId;
	   var cMap = this.kaMap.getCurrentMap().name;
	   this.kaMap.paintLayer(this.qLayer);
	    if(this.resultDiv ){

	    call('tools/query/queryTableXSL.php?sessionId='+this.sessionId+'&id='+this.qId+'&map='+cMap+'&output=table',this,this.injectResult);
	    }else  {
        //if resultdiv doesn't exist    
	    WOOpenWin( 'Query', 'tools/query/queryTableXSL.php?sessionId='+this.sessionId+'&id='+this.qId+'&map='+cMap+'&output=html', 'resizable=yes,scrollbars=yes,width=600,height=400' );
		
	    }
 
   
     	this.qId++;
     }else{
     	if(this.kaMap.getCurrentMap().getLayer("queryLayer")) this.kaMap.removeMapLayer("queryLayer");
		alert("No results for this query!");
	 }
 };
  _queryManager.prototype.injectResult=function(szResult){
	 	     
      this.resultDiv.innerHTML=szResult;
 };
 _queryManager.prototype.createLayer=function(){
 
          
     this.qLayer= new _queryLayer("queryLayer",true,100,'PNG',false,layers,this.qId);
     this.kaMap.addMapLayer(this.qLayer);
 	 
     var legend=this.kaMap.getRawObject("group_queryLayer");
     if(legend){
 		    
     var button= document.createElement('img');
     button.src=this.kaMap.server+"/images/legend_x.png";
     button.title="Remove Layer";
     button.alt="Remove Layer";
     button.qM=this;
     button.onclick = _queryManager_queryOnClick;
     legend.getElementsByTagName('tr')[0].appendChild(button);
     }
  
};
 _queryManager_queryOnClick=function(){
  
     for (i=0;i<this.qM.qLayer.scales.length;i++)this.qM.qLayer.scales[i]=0;
     this.qM.qLayer.setVisibility( false );
     this.qM.kaMap.triggerEvent( KAMAP_SCALE_CHANGED, this.qM.kaMap.getCurrentScale() ); 
       if(this.qM.resultDiv )  this.qM.injectResult('');
 };
 
  _queryManager.prototype.zoomToSelected=function(mix,miny,maxx,maxy){
  
  
   this.kaMap.zoomToExtents(mix,miny,maxx,maxy);
  
  
  }