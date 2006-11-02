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
    
    $stringa_query = "http://localhost/cgi-bin/wps.py?service=wps&version=0.4.0&request=Execute&Identifier=visibility2&";
    $array = array('x', $_REQUEST['xvalue'],'y',$_REQUEST['yvalue'],'maxdist',$_REQUEST['maxdist'],'observer',$_REQUEST['observer']);
    $comma_separated = implode(",", $array);
    $stringa_query .= "datainputs=";
    $stringa_query .= $comma_separated;
    $stringa_query .= "&status=true&store=true";
    //echo $stringa_query;
    //die();

//L'indirizzo completo √® terminato, estraggo il nome del file    

    $dom = new DOMDocument();
    $dom->load($stringa_query);
    /*echo $dom->saveHTML();
    die();*/
    $CVR = $dom->getElementsByTagName('ComplexValueReference');
    $nodo = $CVR->item(0)->getAttribute('reference');
    
// Estrae il nome del file
    $aNodo = explode('/',$nodo);
    //$filename = $aNodo[aNodo.length];
    $filename = end($aNodo);
    //$filename = substr($nodo, 32, 30);
    $pywps_path.=$filename;
    //var_dump($pywps_path);

// Aggiorna il mapfile con il file creato e visualizza il layer
        $layer = ms_newLayerObj($map);
        $layer->set('name', "visibility");
	$layer->set('status', MS_DEFAULT );
	$layer->set('data', $pywps_path);
	$layer->set('type', MS_LAYER_RASTER);
    
        $class = ms_newClassObj($layer);
        $class->setExpression("1");
	$style = ms_newStyleObj($class);
        $style=$class->getStyle(0);
        $style->color->setRGB( -1,-1,-1);

// Creo l'immagine

        $map_id = sprintf("%0.6d",rand(0,999999));
        $image_name = "pywps".$map_id.".png";
        $image_url="/tmp/".$image_name;
        $image=$map->draw();
        $image->saveImage($img_path.$image_name);
        $map->save("/var/www/localhost/htdocs/tmp/mapfile.map");
	echo "/*r los output*/";
	echo "image_url='$image_url';";
	echo "xml_dump='".urlencode($dom->saveXML())."';";
?>