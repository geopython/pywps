<?php  
 /**********************************************************************
 *
 * purpose: a connector r.los GRASS function
 *
 * authors: Luca Casagrande (...) and Lorenzo Becchi (lorenzo@ominiverdi.com)
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


 include('../include/config.php');
 
        $map = ms_newMapObj($map_path.$map_file);
    
    
	$maxradius = 3000;

if ($_POST['radius'] > $maxradius) {
      die ("In this example, radius can't be greater of $maxradius.Please use suggested value.");
   
   /*} 
   elseif ($_POST['x']  < 589435 ||  $_POST['y']  < 4914010 || $_POST['x']  > 609527 ||  $_POST['y'] >  4928060) {
     die("The point it's outside the extent. Please use suggested value.");
     */
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
	echo "<p>$stringa_query = $stringa_query</p>";
	print_r($dom);
	die;
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
		
	echo "/*r los output*/";
	echo "image_url='$image_url';";
	echo "xml_dump='".urlencode($dom->saveXML())."';";
	//echo "mapfile='/tmp/".$sessionId.".map';";
?>