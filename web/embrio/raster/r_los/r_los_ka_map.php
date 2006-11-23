<?php

/**********************************************************************
 *
 * purpose: an AJAX interface to Pywps
 *
 * authors: Luca Casagrande (...) and Lorenzo Becchi (lorenzo@ominiverdi.com)
 *
 *   - it should work like this (jachym suggestion): 
 *		1) user will set the server address 
 *		2) webinterface would getcapabilities - all the processes offered by the server 
 * 		3) user would choose some process 
 * 		4) web interface would describe process and create input form for the user
 * 
 *   TODO:
 * 		- tranlate all comments in english
 * 		- stick to the planned interface
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

/*if(file_exists('include/config.php')) include('include/config.php');
else die('create your include/config.php using include/config.php.dist as template');
*/
// Crea l'oggetto map per il mapfile specificato

	//$map = ms_newMapObj($map_path.$map_file);

// Crete first image
    /*
	$map_id = sprintf("%0.6d",rand(0,999999));
	$image_name = "pywps".$map_id.".png";
	$image_url=$img_rel_path.$image_name;
	$image=$map->draw();
	$image->saveImage($img_path.$image_name);*/
?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<title>PyQPS r.los  by ominiverdi.org</title>
		<script type="text/javascript" src="js/startUp_kamap.js"></script>
		<script type="text/javascript" src="../../ka-map/htdocs/DHTMLapi.js"></script>
		<script type="text/javascript" src="../../ka-map/htdocs/xhr.js"></script>
		<script type="text/javascript" src="../../ka-map/htdocs/kaMap.js"></script>
		<script type="text/javascript" src="../../ka-map/htdocs/kaTool.js"></script>
		<script type="text/javascript" src="../../ka-map/htdocs/wz_dragdrop.js"></script>
		<script type="text/javascript" src="../../ka-map/htdocs/kaZoomer.js"></script>
		
		
		<script type="text/javascript" src="../../ka-map/htdocs/tools/query/queryLayer.js"></script>
		<script type="text/javascript" src="../../ka-map/htdocs/tools/wps/wpsManager.js"></script>
		<script type="text/javascript" src="../../ka-map/htdocs/tools/wps/wpsLayer.js"></script>
		
		<script type="text/javascript">
		var myKaMap = null;
		var queryParams = null;
		SET_DHTML();
		
		//interface vars
		var canvas; //show appended objects
		
		//MODULE VARS
		var module_path = 'mod/mod_r_los.php';
		var identifier = 'visibility2';//Identifier name for WPS service
		var wpsCache = '/home/doktoreas/pywps.ominiverdi.org/subversion/trunk/web/tmp/';
				
		
		//WPS manager
		var wpsManager;
		
		
		/**
		 * parse the query string sent to this window into a global array of key = value pairs
		 * this function should only be called once
		 */
		function parseQueryString()
		{
			queryParams = [];
			var s=window.location.search;
			if (s!='')
			{
				s=s.substring( 1 );
				var p=s.split('&');
				for (var i=0;i<p.length;i++)
				{
					var q=p[i].split('=');
					queryParams[q[0]]=q[1];
				}
			}
		}
		
		/**
		 * get a query value by key.  If the query string hasn't been parsed yet, parse it first.
		 * Return an empty string if not found
		 */
		function getQueryParam(p)
		{
			if (!queryParams)
			{
				parseQueryString();
			}
			if (queryParams[p])
				return queryParams[p];
			else 
				return '';
		}
		
		function myOnLoad()
		{
			initDHTMLAPI();
			
			var map = getQueryParam('map');
			var extents = getQueryParam('extents');
			var cps = getQueryParam('cps');
			
			myKaMap = new kaMap( 'viewport' );
			var kaNav = new kaNavigator( myKaMap );
			kaNav.activate();
			myKaZoomer = new kaZoomer(myKaMap); 
			//myKaMap.resize();//??? maybe not needed
			myKaMap.registerForEvent( KAMAP_MAP_INITIALIZED, null, myMapInitialized );
			myKaMap.registerForEvent( KAMAP_SCALE_CHANGED, null, myScaleChanged );
			myKaMap.registerForEvent( KAMAP_MAP_CLICKED, null, myMapClicked );
			myKaMap.registerForEvent( WPS_LAYER_PAINTING, null, waitEnd );

			myKaMap.initialize( map, extents, cps );
		}
		function myMapInitialized(){
			/* Embrio startup*/
				//set img object
				outimg = document.getElementById('outimg');
				//outimg.onmousedown = getCoords;
				//get params
				map_extent = document.getElementById('map_extent').value;
				map_extent = map_extent.split(',');
				height_extent = document.getElementById('height_extent').value.split(',');
				height_unit = parseInt((height_extent[1]-height_extent[0])/steps*100)/100;
				distance_extent = document.getElementById('distance_extent').value.split(',');
				distance_unit = parseInt((distance_extent[1]-distance_extent[0])/steps*100)/100;
				
				//print ranges
				getRawObject('observer_range').innerHTML = height_extent[0] + ' -&gt; ' + height_extent[1]; 
				getRawObject('maxdist_range').innerHTML = distance_extent[0] + ' -&gt; ' + distance_extent[1]; 
				
				//update selects
				var maxdist = getRawObject('maxdist');
				var observer = getRawObject('observer');
				var height = parseInt(height_extent[0]);
				var distance = parseInt(distance_extent[0]);
				for(i=0;i<=steps;i++) {
					if(i==steps){
						height = parseInt(height_extent[1]);
						distance = parseInt(distance_extent[1]);
						maxdist[i] = new Option(distance,distance,false,false);
						observer[i] = new Option(height,height,false,false);
					} else{  
						maxdist[i] = new Option(distance,distance,false,false);
						observer[i] = new Option(height,height,false,false);
					}
					
					height = parseInt((height + height_unit)*100)/100;
					distance = parseInt(distance + distance_unit);
				}
				
				//set button event
				getRawObject('go').onclick = runPywps;
				
				//create drawing canvas
				canvas = myKaMap.createDrawingCanvas('10');
		}
		function myScaleChanged(eventID, scale){
		}
		function myMapClicked(eventID, coords){
			//alert(coords[0]+ ' ' + coords[1]);
			setFields(coords[0],coords[1]);
			
			//empty pins
			myKaMap.removeAllObjects(canvas);
			//create the pin obj
			var pinDiv = document.createElement('div');
			pinDiv.id = 'pinDiv';
			var pinImg = document.createElement('img');
			pinImg.src = '../../ka-map/htdocs/images/tip-yellow.png';
			pinImg.style.position = 'absolute';
			pinImg.style.top = '-19px';
			pinImg.style.left = '-6px';
			pinDiv.appendChild(pinImg);
			myKaMap.addObjectGeo( canvas, coords[0], coords[1], pinDiv );
		}
		</script>
		<link href="../../css/screen.css" rel="stylesheet" type="text/css" media="all">
		<style type="text/css">
			#viewport {
			  position: absolute;
			  top:10px;
			  left:10px;
			  width: 640px;
			  height: 480px;
			  background-color: #f0f0f0;
			  overflow: hidden;
			  border: 1px solid #000000;
			  cursor: move;
			  -moz-box-sizing: border-box;
			}
			 #outimg {
					position:absolute;
					top:10px;
					left:200px;
			}
		</style>
	</head>
	<body onload="myOnLoad();">
        
<div id="header">
	<h1>GRASS Buffer module</h1>
	<p>
	<strong>r.los</strong> generates a raster map output in which the cells that are visible from a user-specified observer location are marked with integer values that represent the vertical angle (in degrees) required to see those cells (viewshed).
    	</p>
	<p><strong>Usage:</strong> click on map to set <em>coords</em>. Use selects to change <em>distance</em> and
	<em>height</em> params.<br>
	Then click on <strong>Go!</strong> button to see overlayed output.
	</p>
</div>
<div id="output">

</div>
<div id="viewport">
</div>
<div  id="params">
<form method="post" action="<?php echo $PHP_SELF; ?>">
	<fieldset>
	<legend>Params</legend>
        <label>X:</label><span id="xvalue_span">0</span> 
		<input type="hidden" name="xvalue" id="xvalue" size="20" maxlength="40" value="599043" />		
        <label>Y:</label><span id="yvalue_span">0</span> 
		<input type="hidden" name="yvalue" id="yvalue" size="20" maxlength="40" value="4921752" />
		<p><label>Max distance where check visibility:<br> (range <span id="maxdist_range"></span>)</label>
		<!--<input type="text" name="maxdist" size="20" maxlength="40" value="" />-->
		<select name="maxdist" id="maxdist">
		</select></p>
		<p><label>Height of the observer:<br> (range <span id="observer_range"></span>)</label>
		<!--<input type="text" name="observer" size="20" maxlength="40" value="" />-->
		<select name="observer" id="observer">
		</select></p>
		<input type="button" name="submit" id="go" value="Go!" />
	</fieldset>
	
	<!-- 
		INTERFACE PARAMS
		this hidden fields for interface params 
	-->
	<input type="hidden" name="map_extent" id="map_extent" value="588913.043478,4915200.000000,610066.956522,4928010.000000">
	<input type="hidden" name="distance_extent" id="distance_extent" value="500,1500">
	<input type="hidden" name="height_extent" id="height_extent" value="1,3">
	
	<img id="outimg" src="" width="200" height="100" />
</form>
</div>
<div id="console">
<textarea name="console" id="consolearea">
</textarea>
</div>
</body>
</html>
