<?php  
 /**********************************************************************
 *
 * purpose: a raster analysis process
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


// This file is created to use stromy.tif 

	include('../include/config.php');
 
//Initialize some var for parsing output
	
	$value=0;
	$output=array();	
        $map = ms_newMapObj($map_path.$map_file);

//This one is used if user can select more then a raster
	
	$input_raster="/home/doktoreas/data/treeno/stromy.tif";	

//Built up the request for PYWPS	
	
	$stringa_query = $cgi_executable."?service=wps&version=0.4.0&request=Execute&Identifier=trees&";
	$array = array('input', $input_raster);
	$comma_separated = implode(",", $array);
	$stringa_query .= "datainputs=";
	$stringa_query .= $comma_separated;
	$stringa_query .= "&status=false&store=true";
	
	$dom = new DOMDocument();
	$dom->load($stringa_query);
	
//Output are 2 vector files (one area and one point) and 1 costant (number of trees)

//Extract the path of the vectors

foreach ($dom->getElementsByTagName('ComplexValueReference') as $CVR) {
        $nodo = $CVR->getAttribute('reference');
        $aNodo = explode('/',$nodo);
        $filename = end($aNodo);
        $output[$value]=$pywps_outputPath.$filename;
        $value++;
        }

//Extract the value of the constant (to be finished)

//	$number_trees=$dom->getElementsByTagName('LiteralValue');
		


/*	$CVR = $dom->getElementsByTagName('ComplexValueReference');
	$nodo = $CVR->item(0)->getAttribute('reference');
	$aNodo = explode('/',$nodo);
	$filename = end($aNodo);
	$pywps_outputPath.=$filename;
*/	


//Update the mapfile with first layer voronoi (area)
	 
	$layer = ms_newLayerObj($map);
   	$layer->set('name', "voronoi");
   	$layer->set('status', MS_DEFAULT );
   	$layer->set('connection', $output[0]);
   	$layer->set('type', MS_LAYER_POLYGON);
   	$layer->set('transparency',"64");
   	$layer->set('connectiontype',MS_OGR);
        $class = ms_newClassObj($layer);
        $style = ms_newStyleObj($class);
        $style=$class->getStyle(0);
        $style->color->setRGB(102,228,73);
	$style->outlinecolor->setRGB(0,0,0);

//This is for the layer top (point)

	$layer= ms_newLayerObj($map);
   	$layer->set('name', "top");
   	$layer->set('status', MS_DEFAULT );
   	$layer->set('connection', $output[1]);
   	$layer->set('type', MS_LAYER_POINT);
   	$layer->set('connectiontype',MS_OGR);
        $class= ms_newClassObj($layer);
        $style= ms_newStyleObj($class);
        $style=$class->getStyle(0);
        $style->color->setRGB(108,88,220);
		
//The mapfile is saved for debugging purpose
		
	$map->save($img_path."/mapfile_tree.map");

//Create the output image

	$map_id = sprintf("%0.6d",rand(0,999999));
	$image_name = "pywps".$map_id.".png";
	$image_url=$img_rel_path.$image_name;
	$image=$map->draw();
	$image->saveImage($img_path.$image_name);
	echo "/*r los output*/";
	echo "image_url='$image_url';";
	//echo "xml_dump='".urlencode($dom->saveXML())."';";
	echo "mapfile='/tmp/".$sessionId.".map';";
	//echo "mapfile='$img_path."/mapfile_tree.map"
	if(isset($_REQUEST['debug'])){
	echo "<br>filename = $filename";
	echo "<br>outimg = $image_url";
	echo "<br>".$img_path."/mapfile_treeno.map";
	}
?>	
