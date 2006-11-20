/**********************************************************************
 *
 * $Id: wfsConnector.js,v 1.5 2006/09/09 12:05:17 lbecchi Exp $
 *
 * purpose: add WFS features to ka-Map (gub 1490)
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
 * _wfsConnector - spiega bene
 *
 * To use wfsConnector:
 * 
 * 1) add a script tag to your page:
 * 
 * <script type="text/javascript" src="wfsConnector.js"></script>
 *
 * 2) create a new instance of _wfsConnector
 *
 * var l = new _wfsConnector( szName, bVisible, opacity, imageformat, bQueryable, 
 *                   server, version, layers, srs);
 *
 * 3) add it to the map
 *
 * ???? myKaMap.addMapLayer( l );
 *
 * For instance, assuming you have a form to input the parameters required:
 *
 * function addWFSData()
 * {
 *     var f = document.forms.wfs;
 *     var szName = f.wfsName.value;
 *     var server = f.wfsServer.value;
 *     var version = "1.0.0";
 *     var layers = f.wfsLayers.value;

 *     var wfsConn = new _wfsConnector( szName, server, version, layers);

 * }
 *
 *****************************************************************************/
 
 function _wfsConnector( oKaMap, szID, server, version,epsg)
 {
    //_layer.apply(this,[szName,bVisible,opacity,imageformat,bQueryable]);
    this.server = server;
    this.kaMap = oKaMap;
    this.wfsObj=this.kaMap.getRawObject(szID);
    this.version = (version && version != '') ? version : '1.0.0';
    this.layers = '';
    this.baseURL = this.server;
    this.sessionId='';
    this.connector='';
    this.epsg= epsg;
  
    this.toolTip = new kaToolTip( this.kaMap );
    var offsetX=-6;//offset dell'immagine rispetto alle coordinate del punto
	var offsetY=-19;//serve per centrare l'immagine rispetto al punto
	this.toolTip.setTipImage('images/tip-red.png',offsetX,offsetY);

	this.points;
	this.lines;
	this.polygons;

	this.XMLcode = '';//temporaneo per metterci su il GML della feature
	
	//PG kaXMLOverlay instance

//	this.myDrawingCanvas = new kaXmlOverlay( this.kaMap, 250 );

	var idx = 100;//lo zindex del canvas
	this.canvas = this.kaMap.createDrawingCanvas( idx );
	
     /*		
     * make sure the server url is terminated with a ? or not a & so we can
     * append the rest of the request without having to worry about a
     * correctly formatted url
     */
    if (this.baseURL.indexOf('?') == -1)
    {
        this.baseURL = this.baseURL + '?';
    }
    else
    {
        if (this.baseURL.charAt( this.baseURL.length - 1 ) == '&')
            this.baseURL = this.baseURL.slice( 0, -1 );
    }

    /*
     * required components of WMS 1.0.0 are:
     * VERSION set to version or 1.1.1 if version is empty
     * REQUEST - set to GetMap if not in the server URL
     * TYPENAME - set to layers if not in the server URL
     * SRS - set to srs if not in the server URL
     * BBOX - ?????
     * OUTPUTFORMAT = GML2
     *
     * Optional components are:
     *
     * TRANSPARENT - set to ON if not in the server URL
     * BGCOLOR - do not add this, it will interfer with transparency
     * EXCEPTIONS - set to in image if not in the server URL
     * TIME - not supported in this code, add to server URL yourself
     * ELEVATION - not supported in this code, add to server URL yourself
     * SLD (SLD only) - not supported in this code, add to server URL yourself
     * WFS (SLD only) - not supported in this code, add to server URL yourself
     */
     
    this.baseURL = this.addRequestParameter(this.baseURL, 'service', "&service=WFS" );
    this.baseURL = this.addRequestParameter(this.baseURL, 'request', "&request=GetCapabilities" );
    this.baseURL = this.addRequestParameter(this.baseURL, 'version', "&version="+this.version );
    //this.addRequestParameter( 'typename', "&typename=" + escape(this.layers) );
/*    this.addRequestParameter( 'srs', "&srs=" + this.srs );
    this.addRequestParameter( 'styles', "&styles=" );
    this.addRequestParameter( 'format', "&format=" + this.imageformat );
    this.addRequestParameter( 'transparent', '&transparent=true' );
    this.addRequestParameter( 'exceptions', '&exceptions=application/vnd.ogc.se-inimage' );*/

    this.connector = 'tools/wfs/wfs_connector.php?';
    var myURL = this.connector + 'wfsURL='+encodeMyHtml(this.baseURL);
    myURL = this.addRequestParameter(myURL, 'com', "&com=getCapabilities" );
 //   document.getElementById('toolbar').innerHTML = this.connector;//DEBUG
  
    call(myURL,this, this.init);
 	this.kaMap.registerForEvent( KAMAP_MAP_INITIALIZED, this, this.clearPoints );
    this.kaMap.registerForEvent( KAMAP_SCALE_CHANGED, this, this.extentChanged );
  //  this.kaMap.registerForEvent( KAMAP_EXTENTS_CHANGED, this, this.extentChanged );
 
 
 };
 
/** 
 * wmsLayer.addRequestParameter( name, parameter )
 *
 * add a parameter to the baseURL safely by checking to see if the parameter
 * exists already.  This is an internal function not intended to be used
 * by other code.
 */
_wfsConnector.prototype.addRequestParameter = function(url, name, parameter )
{

    if ((url) && url.indexOf( name ) == -1)
    {
        return url + parameter;
    }
};

_wfsConnector.prototype.init = function(szResult)
{

  eval(szResult);
  
  getRawObject('wfsMessage').innerHTML = 'now choose a Feature';
  /* qua dietro ripulire l'interfaccia*/
};

_wfsConnector.prototype.extentChanged = function()
{

  this.toolTip.move();
};

_wfsConnector.prototype.draw = function(szResult)
{
//document.getElementById('toolbar').innerHTML = szResult;//DEBUG
//  alert(szResult);
	
	var feature='';
	
	eval(szResult);
	
	getRawObject('wfsMessage').innerHTML = 'enjoy! '+this.points.length+' points displayed';
 if(this.points){
	
	
		
	for(var i=0;i<this.points.length;i++){
 		var point = this.points[i];
 		//PG kaXmlOverlay CLASS
 		// Id, x ,y 
 		/*var pm = this.myDrawingCanvas.addNewPoint(point[0], point[1], point[2]);
		pm.div.onmouseover=this.onmouseover;
		//pm.div.onmouseout=this.onmouseout;
		pm.div.style.cursor='pointer';
		pm.feature = feature;
		pm.connector=this;
		var s = new kaXmlSymbol();
		s.size = 10;
		s.color = 'rgb(200,10,50)';
		pm.addGraphic(s);
		var l = new kaXmlLabel();
		l.py = -2;
		l.text = "ID="+point[0];
		l.fsize = "8px";*/
//		pm.addGraphic(l);
		var img = document.createElement('img');
		img.src = 'images/tip-green.png';
		img.pid = point[0];
		img.onmouseover=this.onmouseover;
		img.style.cursor='pointer';
		img.feature = feature;
		img.connector=this;
		var obj = img;
		var lon = point[1];
		var lat = point[2];
		img.lon = lon;
		img.lat = lat;
		this.kaMap.addObjectGeo( this.canvas, lon, lat, obj );
		
		
 	}  

 };
 
 
//  if(this.lines){
//   // TO BE IMPLEMENTED
//   
//  }
//  
//   if(polygons){
//   // TO BE IMPLEMENTED
//   
//  }
 
 
};
_wfsConnector.prototype.onmouseout = function(e)
{
 e = (e)?e:((event)?event:null);
/*var msgBox =getRawObject('msgBox');
msgBox.style.top='-300px';
msgBox.style.left='0px';*/

//this.point.connector.toolTip.move();
};
_wfsConnector.prototype.onmouseover = function(e)
{
 e = (e)?e:((event)?event:null);
//var msgBox =getRawObject('msgBox');
//msgBox.innerHTML='WAIT A MOMENT :-)';
var conn=this.connector;

/*
var y =(e.clientY);
var x =(e.clientX);
conn.toolTip.setText('WAIT A MOMENT... Connecting');

conn.toolTip.move(x,y);
*//*
var a = conn.kaMap.adjustPixPosition( x,y );
var p = conn.kaMap.pixToGeo( a[0],a[1] );
conn.toolTip.setText('WAIT A MOMENT... Connecting');*/
conn.toolTip.moveGeo(this.lon,this.lat);

var url=conn.kaMap.server+"tools/wfs/wfs_connector.php?";
url=conn.addRequestParameter(url, 'sessionId', "&sessionId="+conn.sessionId );
url=conn.addRequestParameter(url, 'featureId', "&featureId="+this.pid );
url=conn.addRequestParameter(url, 'features', "&features="+this.feature );
url=conn.addRequestParameter(url, 'com', "&com=query" );
call(url,conn,conn.getInfo);
};
_wfsConnector.prototype.getInfo = function(szResult)
{
	eval(szResult);
	this.toolTip.recenter(this.toolTip.domObj);
};

_wfsConnector.prototype.clearPoints = function()
{
	//this.myDrawingCanvas.removePoint();
	this.kaMap.removeDrawingCanvas(this.canvas);
};


_wfsConnector.prototype.getFeatures = function(sessionId,features)
{
  /*???*/
  var featURL = this.server;
  featURL = this.addRequestParameter(featURL, 'service', "&service=WFS" );
  featURL =   this.addRequestParameter(featURL, 'request', "&request=GetFeature" );
  featURL =   this.addRequestParameter(featURL, 'version', "&version="+this.version );
  featURL =   this.addRequestParameter(featURL, 'typename', "&typename="+features );
 
  myURL = this.connector + 'wfsURL='+encodeMyHtml(featURL);
  myURL =   this.addRequestParameter(myURL, 'sessionId', "&sessionId="+this.sessionId );
  myURL =   this.addRequestParameter(myURL, 'com', "&com=getFeature" );
  myURL =   this.addRequestParameter(myURL, 'epsg', "&epsg="+this.epsg );
   //document.getElementById('legend').innerHTML = myURL;//DEBUG
   
  call(myURL,this, this.draw);
  
};



function encodeMyHtml(string) {
  encodedHtml = escape(string);
  encodedHtml = encodedHtml.replace(/\//g,"%2F");
  encodedHtml = encodedHtml.replace(/\?/g,"%3F");
  encodedHtml = encodedHtml.replace(/=/g,"%3D");
  encodedHtml = encodedHtml.replace(/&/g,"%26");
  encodedHtml = encodedHtml.replace(/@/g,"%40");
  return encodedHtml;
  } ;
function urlDecode(sz){

return sz;
return unescape(sz).replace(/\+/g," ");

};
