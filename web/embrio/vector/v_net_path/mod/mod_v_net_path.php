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

if ($_REQUEST['cost'] != 0) {
      die ("Sorry in this example, the path can't be selected using a cost parameter.Please assign 0 to the cost form");

   /*} 
   elseif ($_REQUEST['x']  < 589435 ||  $_REQUEST['y']  < 4914010 || $_REQUEST['x']  > 609527 ||  $_REQUEST['y'] >  4928060) {
     die("The point it's outside the extent. Please use suggested value.");
     */
     }else
   {
      
$stringa_query = $cgi_executable."?service=wps&version=0.4.0&request=Execute&Identifier=shortestpath2&";
    #$stringa_query = "http://localhost/cgi-bin/wps.py?service=wps&version=0.4.0&request=Execute&Identifier=shortestpath2&";
    $array = array('x1', $_REQUEST['x1value'],'y1',$_REQUEST['y1value'],'x2', $_REQUEST['x2value'],'y2',$_REQUEST['y2value'],'cost',$_REQUEST['cost']);
    $comma_separated = implode(",", $array);
    $stringa_query .= "datainputs=";
    $stringa_query .= $comma_separated;
    $stringa_query .= "&status=true&store=true";

//Indirizzo completo terminato, estraggo il nome del file    

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
        $layer->set('name', "path");
	$layer->set('status', MS_DEFAULT );
	$layer->set('connection', $pywps_outputPath);
	$layer->set('type', MS_LAYER_LINE);
  	$layer->set('connectiontype',MS_OGR);  
        $class = ms_newClassObj($layer);
	$style = ms_newStyleObj($class);
        $style=$class->getStyle(0);
	$style->color->setRGB( 255,255,0);
        
// Creo l'immagine
    
    $map_id = sprintf("%0.6d",rand(0,999999));
    $image_name = "pywps".$map_id.".png";
    $image_url=$img_rel_path.$image_name;
    $image=$map->draw();
    $image->saveImage($img_path.$image_name);
//non dovrebbe esserci bisogno di salvare questo mapfile
    $map->save($img_path."/mapfile_path.map");
}	
		
	echo "/*r los output*/";
	echo "image_url='$image_url';";
	echo "xml_dump='".urlencode($dom->saveXML())."';";
	//echo "mapfile='/tmp/".$sessionId.".map';";
?>