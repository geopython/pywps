<?php
/**********************************************************************
 *
 * 
 * purpose: a simple hilite system for search and query system 
 *
 * author: Andrea Cappugi & Lorenzo Becchi
 *
 * 
 *
 * TODO:
 *All
 * 
 *
 **********************************************************************
 *
 * Copyright (c) 2006, ominiverdi.org
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
	
	
	session_start();
//ERROR HANDLING
  if(isset($_REQUEST['debug'])) 
  error_reporting ( E_ALL );
  else error_reporting( E_ERROR );
  
  include_once( '../../../include/config.php' );
  
  /* bug 1253 - root permissions required to delete cached files */
  $orig_umask = umask(0);
  
  if (!extension_loaded('MapScript')) dl( $szPHPMapScriptModule );
  $oMap = ms_newMapObj($szMapFile);


  //check if the session is on
  if (isset($_GET['sessionId'])){
  	 $sessionId=trim($_GET['sessionId']);
  	   session_id($sessionId);
  }
  else  $sessionId=session_id(); 
  
   if(isset($_REQUEST['id'])) $qId= $_REQUEST['id'];
   else{
    $szResult= 'alert ("id query required");';
    echo $szResult;
    die;
  }
  /*if(isset($_REQUEST['layer'])) $szLayer= $_REQUEST['layer'];
   else{
    $szResult= 'alert ("layer query required");';
    echo $szResult;
    die;
  }*/
  
  if(isset($_REQUEST['datainputs'])) $datainputs= $_REQUEST['datainputs'];
   else{
    $szResult= 'alert ("datainputs required");';
    echo $szResult;
    die;
  }
  
    if(isset($_REQUEST['wpsCache'])) $wpsCache= $_REQUEST['wpsCache'];
   else{
    $szResult= 'alert ("wpsCache required");';
    echo $szResult;
    die;
  }
  
  if(isset($_REQUEST['identifier'])) $identifier= $_REQUEST['identifier'];
   else{
    $szResult= 'alert ("identifier required");';
    echo $szResult;
    die;
  }
  
  if(isset($_REQUEST['wpsUrl'])) $wpsUrl= $_REQUEST['wpsUrl'];
   else{
    $szResult= 'alert ("wpsUrl required");';
    echo $szResult;
    die;
  }
  if(isset($_REQUEST['sldUrl'])) $sldUrl= $_REQUEST['sldUrl'];
   else{
    $szResult= 'alert ("sldUrl required");';
    echo $szResult;
    die;
  }
  
  
 //Destroy old query Cache
  if (is_dir($szBaseCacheDir."/sessions/".$sessionId."/wpsLayer/".$szMap."/"))
   remove_directory($szBaseCacheDir."/sessions/".$sessionId."/wpsLayer/".$szMap."/");

  //Build query sys cache directory!!
  $szQueryCacheDir=$szBaseCacheDir."/sessions/".$sessionId."/wpsLayer/".$szMap."/".$qId."/"; 
 
  /* create the main sessionID cache directory if necessary */
  if (!@is_dir($szQueryCacheDir))
    makeDirs($szQueryCacheDir);
    
    //REQUEST HANDLING


//Built up the request for PYWPS	
	
	$query_string = $wpsUrl."?service=wps&version=0.4.0&request=Execute&Identifier=$identifier&";
	$query_string .= "datainputs=". $datainputs;
	$query_string .= "&status=true&store=true";
	
//Extract the file name.This part need more debugging

	$dom = new DOMDocument();
	$dom->load($query_string);
	$CVR = $dom->getElementsByTagName('ComplexValueReference');
	if($CVR->item(0)){
		$reference = $CVR->item(0)->getAttribute('reference');
		$outFormat = $CVR->item(0)->getAttribute('format');
	}
	else die($query_string);
	
	//parsing reference value
	$aReference = explode('/',$reference);
	$filename = end($aReference);
	//$pywps_outputPath.=$filename;
	
	//Update the mapfile with new layer
	$layer = ms_newLayerObj($oMap);
    $layer->set('name', $identifier);
	$layer->set('status', MS_DEFAULT );
	$layer->set('data', $wpsCache.$filename);
	
	//SWITCHING on outFormat - still basic implementation
	if($outFormat=='text/xml'){
		//supposed to be GML
		$layer->set('connectiontype',MS_OGR);
		//Parsing GML to detect which datatype
		$domGML = new DOMDocument();
		$domGML->load($wpsCache.$filename);
		$point = $domGML->getElementsByTagName('gml:Point');
		$line = $domGML->getElementsByTagName('gml:LineString');
		$polygon = $domGML->getElementsByTagName('gml:Polygon');
		//<gml:LineString> <gml:Point> <gml:Polygon>
		if($point){
			$layer->set('type', MS_LAYER_POINT);
		}
		if($line){
			$layer->set('type', MS_LAYER_LINE);
		}
		if($polygon){
			$layer->set('type', MS_LAYER_POLYGON);
		}
		//APPLYING EXTERNAL SLD or forcing values
		if(!$layer->applySLDURL($sldUrl,$identifier)){
			$class = ms_newClassObj($layer);
			$style = ms_newStyleObj($class);
			$style=$class->getStyle(0);
			$style->color->setRGB( 255,255,0);
		}
	} else {
		//supposed to be Raster
		$layer->set('type', MS_LAYER_RASTER);
		//APPLYING EXTERNAL SLD or forcing values
		if(!$layer->applySLDURL($sldUrl,$identifier)){
			$class = ms_newClassObj($layer);
			$class->setExpression("1");
			$style = ms_newStyleObj($class);
			$style=$class->getStyle(0);
			$style->color->setRGB( -1,-1,-1);
		} 
	}
	$oMap->save($szQueryCacheDir."/embrio.map");
	
	//this output confirms to ka-map that the request has been completed properly
	echo "/*output*/queryResult=0;this.sessionId='$sessionId';";
	
	//DEBUG STUFF
	if(isset($_REQUEST['debug'])){
	echo "this.datapath='".$wpsCache.$filename."';this.mapfile=".$szQueryCacheDir."/embrio.map;";		
	
	echo "this.sldUrl=$sldUrl;";
	
			$map_id = sprintf("%0.6d",rand(0,999999));
			$image_name = "pywps".$map_id.".png";
			$image_url=$wpsCache.$image_name;
			$image=$oMap->draw();
			$image->saveImage($image_url);
			echo "<br>this.outimg='$image_url';";
			echo "<br>this.query_string='$query_string';";
			echo "<br>this.outFormat='$outFormat';";
			echo "<img src='../../../../../../tmp/$image_name'>";
	}
	
/*	
} else {
	
	echo"queryResult=0;";
}*/

   function remove_directory($dir) {
       $dir_contents = myScandir($dir);
       foreach ($dir_contents as $item) {
           if (is_dir($dir.$item) && $item != '.' && $item != '..') {
               remove_directory($dir.$item.'/');
           }
           elseif (file_exists($dir.$item) && $item != '.' && $item != '..') {
               unlink($dir.$item);
           }
       }
       rmdir($dir);
   }
   

 	function myScandir($dir){
 		$dirhandle = opendir($dir);
 		$dir_contents = array();
		while(( $file = readdir($dirhandle)) !== false)
		{
			if (( $file != "." )&&( $file != ".."))
			{
				$dir_contents[] = $file;
			}
		}
		return $dir_contents;
			
 	}
 
?>
