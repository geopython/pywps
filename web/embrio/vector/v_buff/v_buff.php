<?php
 /**********************************************************************
 *
 * purpose: a connector v.buff GRASS function
 *
 * authors: Luca Casagrande (luca.casagrande@gmail.com) and Lorenzo Becchi (lorenzo@ominiverdi.com)
 *
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

if(file_exists('include/config.php')) include('include/config.php');
else die('create your include/config.php using include/config.php.dist as template');

$map = ms_newMapObj($map_path.$map_file);

// Creating first image
    
$map_id = sprintf("%0.6d",rand(0,999999));
$image_name = "pywps".$map_id.".png";
$image_url=$img_rel_path.$image_name;
$image=$map->draw();
$image->saveImage($img_path.$image_name);


?>
<html>
<head>
	<title>PyWPS v.buffer example by ominiverdi.org</title>
	<script type="text/javascript" src="../../js/xhr.js"></script>
	<script type="text/javascript" src="js/startUp.js"></script>
	<link href="../../css/screen.css" rel="stylesheet" type="text/css" media="all">
</head>
<body>


<div id="header">
	<h1>GRASS Buffer module (v.buffer)</h1>
	<p>
	Create a buffer around features of given type (areas must contain centroid).
	</p> 
	

	</p>
	<p><strong>Usage:</strong> click on map to set <em>coords</em> of the centroid. manually insert the  <em>radius</em> 
	 param.<br>
	Then click on <strong>Go!</strong> button to see overlayed output.
	</p>
</div>
 

<div id="output">
<img id="outimg" src="<?=$image_url;?>" width="640" height="480" />
</div>
        
<div  id="params">
	<form method="post" action="<?php echo $script_name;?>">
	<fieldset>
	<legend>Params</legend>
	
	<label>X:</label><span id="xvalue_span">0</span> 
	<input type="hidden" name="xvalue" id="xvalue" size="20" maxlength="40" value="599043" />		
	
	<label>Y:</label><span id="yvalue_span">0</span> 
	<input type="hidden" name="yvalue" id="yvalue" size="20" maxlength="40" value="4921752" />
	
	
	<p>
	Radius:<br />
	<input type=text name="radius"  id="radius" size="20" maxlength="4" value="1000" max="3000" />
	</p>
	
	
	<input type="button" name="submit" id="go" value="Go!" />
	</fieldset>
	<!-- 
		INTERFACE PARAMS
		this hidden fields for interface params 
	-->
	<input type="hidden" name="map_extent" id="map_extent" value="588913.043478,4915200.000000,610066.956522,4928010.000000">
 </form>
 </div>
 <div id="console">
 </div>
</body>
</html>
	

