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

// Creo la prima immagine
    
$map_id = sprintf("%0.6d",rand(0,999999));
$image_name = "pywps".$map_id.".png";
$image_url=$img_rel_path.$image_name;
$image=$map->draw();
$image->saveImage($img_path.$image_name);

// Il form viene inviato

if (isset($_POST['submit']))
    	{
// Verifica l esattezza dei parametri inseriti

$maxradius = 3000;

if ($_POST['radius'] > $maxradius) {
      die ("In this example, radius can't be greater of $maxradius.Please use suggested value.");
   
   } elseif ($_POST['x']  < 589435 ||  $_POST['y']  < 4914010 || $_POST['x']  > 609527 ||  $_POST['y'] >  4928060) {
     die("The point it's outside the extent. Please use suggested value.");
     
     }else
   {
      
//Crea il file contenente le coordinate
        
	$input_id = sprintf("%0.6d",rand(0,999999));
        $input_name = "input".$input_id.".txt";
        $input_url=$img_path.$input_name;
  	$x=$_POST['x'];
	$y=$_POST['y'];
        $array_cord = array($x,$y);
        $coord = implode(",", $array_cord);
	file_put_contents($input_url,$coord);

//Crea la richiesta per pywps
    
   $stringa_query = $cgi_executable."?service=wps&version=0.4.0&request=Execute&Identifier=buffer&";
    $array = array('point',$input_url,'radius',$_POST['radius']);
    $comma_separated = implode(",", $array);
    $stringa_query .= "datainputs=";
    $stringa_query .= $comma_separated;
    $stringa_query .= "&status=true&store=true";

//L'indirizzo completo Ã¨ terminato, estraggo il nome del file    
//TODO: questa parte va debuggata cos“ com' fa un po' acqua
    $dom = new DOMDocument();
    $dom->load($stringa_query);
    $CVR = $dom->getElementsByTagName('ComplexValueReference');
    $nodo = $CVR->item(0)->getAttribute('reference');
    
// Estrae il nome del file
    $aNodo = explode('/',$nodo);
    $filename = end($aNodo);
    $pywps_outputPath.=$filename;

// Aggiorna il mapfile con il file creato e visualizza il layer
   $layer = ms_newLayerObj($map);
   $layer->set('name', "buffer");
   $layer->set('status', MS_DEFAULT );
   $layer->set('connection', $pywps_outputPath);
   $layer->set('type', MS_LAYER_POLYGON);
   $layer->set('transparency',"50");
   $layer->set('connectiontype',MS_OGR);  
        $class = ms_newClassObj($layer);
	$style = ms_newStyleObj($class);
        $style=$class->getStyle(0);
	$style->color->setRGB( 255,0,0);
        

// Creo l'immagine

    $map_id = sprintf("%0.6d",rand(0,999999));
    $image_name = "pywps".$map_id.".png";
    $image_url=$img_rel_path.$image_name;
    $image=$map->draw();
    $image->saveImage($img_path.$image_name);
	//non dovrebbe esserci bisogno di salvare questo mapfile
    $map->save($img_path."/mapfile_buffer.map");
}
}

?>
<html>
<head>
	<title>PyWPS v.net.path example by ominiverdi.org</title>
	<script type="text/javascript" src="../../js/xhr.js"></script>
	<script type="text/javascript" src="js/startUp.js"></script>
	<link href="../../css/screen.css" rel="stylesheet" type="text/css" media="all">
</head>
<body>


<div id="header">
	<h1>GRASS Buffer module</h1>
	<p>
	For this test please input this value (javascript check are not jet implemented)
	</p> 
	<p>
	x=594790 y=4921822  
    	</p>
	<p>
	Radius=1000
    	</p>

	</p>
	<p><strong>Usage:</strong> click on map to set <em>coords</em>. Use selects to change <em>distance</em> and
	<em>height</em> params.<br>
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
	<input type=text name="radius" size="20" maxlength="4" value="1000" max="3000" />
	</p>
	
	
	<input type="submit" name = "submit" value="Go!" /> </td></tr>
	</fieldset>
 </form>
 </div>
</body>
</html>
	

