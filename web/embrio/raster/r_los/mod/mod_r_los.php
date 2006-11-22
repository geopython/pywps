<?php  
 /**********************************************************************
 *
 * purpose: a connector r.los GRASS function
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
 
	include('../include/config.php');
 
        $map = ms_newMapObj($map_path.$map_file);
	
//Built up the request for PYWPS	
	
	$stringa_query = $cgi_executable."?service=wps&version=0.4.0&request=Execute&Identifier=visibility2&";
	$array = array('x', $_REQUEST['xvalue'],'y',$_REQUEST['yvalue'],'maxdist',$_REQUEST['maxdist'],'observer',$_REQUEST['observer']);
	$comma_separated = implode(",", $array);
	$stringa_query .= "datainputs=";
	$stringa_query .= $comma_separated;
	$stringa_query .= "&status=true&store=true";
	
//Extract the file name.This part need more debugging

	$dom = new DOMDocument();
	$dom->load($stringa_query);
	$CVR = $dom->getElementsByTagName('ComplexValueReference');
	$nodo = $CVR->item(0)->getAttribute('reference');
	$aNodo = explode('/',$nodo);
	$filename = end($aNodo);
	$pywps_outputPath.=$filename;
	
//Update the mapfile with new layer

	$layer = ms_newLayerObj($map);
        $layer->set('name', "visibility");
	$layer->set('status', MS_DEFAULT );
	$layer->set('data', $img_path.$filename);
	$layer->set('type', MS_LAYER_RASTER);
    
	
		$map->imagecolor->setRGB( -1,-1,-1);

        $class = ms_newClassObj($layer);
        $class->setExpression("1");
	$style = ms_newStyleObj($class);
        $style=$class->getStyle(0);
        $style->color->setRGB( -1,-1,-1);
		
		
		
	$map->save($img_path."/mapfile_buffer.map");
//Create the output image

	$map_id = sprintf("%0.6d",rand(0,999999));
	$image_name = "pywps".$map_id.".png";
	$image_url=$img_rel_path.$image_name;
	$image=$map->draw();
	$image->saveImage($img_path.$image_name);
	echo "/*r los output*/";
	echo "image_url='$image_url';";
	echo "xml_dump='".urlencode($dom->saveXML())."';";
	echo "mapfile='/tmp/".$sessionId.".map';";
	//echo "mapfile='$img_path."/mapfile_buffer.map"

?>	
