<?php
/**********************************************************************
 * $Id: query.php,v 1.1 2006/06/25 17:40:40 lbecchi Exp $
 * 
 * purpose: a simple map query script the query is executed and saved in a file
 *
 * author: Andrea Cappugi & Lorenzo Becchi
 *
 * 
 *
 * TODO:
 *
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

 /*
 * This script execute a query and save the result in cahce file.!
 * in feture It will be able to quary on a precedent query result!!
 * Now execut to kind of query point query and rect query
 * Request parameters are:
 *
 * map: the name of the map to use.  This is handled by config.php.
 *
 * t: top pixel position
 * l: left pixel position
 * s: scale
 * g: (optional) comma-delimited list of group names to draw
 * layers: (optional) comma-delimited list of layers to draw
 * force: optional.  If set, force redraw of the meta tile.  This was added to
 *        help with invalid images sometimes being generated.
 * tileid: (optional) can be used instead of t+l to specify the tile coord.,
 *         useful in regenerating the cache
 */
//Bug reference: 
//http://bugzilla.maptools.org/show_bug.cgi?id=1313
  session_start();
  //ERROR HANDLING
  if(isset($_REQUEST['debug'])) error_reporting ( E_ALL );
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
  //Destroy old query Cache
  if (is_dir($szBaseCacheDir."/sessions/".$sessionId."/QuerySys/".$szMap."/"))
   remove_directory($szBaseCacheDir."/sessions/".$sessionId."/QuerySys/".$szMap."/");

  //Build query sys cache directory!!
  $szQueryCacheDir=$szBaseCacheDir."/sessions/".$sessionId."/QuerySys/".$szMap."/".$qId."/"; 
 
  /* create the main sessionID cache directory if necessary */
  if (!@is_dir($szQueryCacheDir))
    makeDirs($szQueryCacheDir);
  if (isset($_REQUEST['scale']))
  {
    $scale= $_REQUEST['scale'];
  }
  else 
  {
    $szResult= 'alert ("scale not defined");';
    echo $szResult;
    die;
  }
  if (isset($_REQUEST['q_type'])) $q_type= $_REQUEST['q_type'];
  else 
  {
    $szResult= 'alert ("q_type not defined");';
    echo $szResult;
    die;
  }
  if (isset($_REQUEST['coords'])) $coords= explode(',',$_REQUEST['coords']);
  else 
  {
    $szResult= 'alert ("coordinate not defined");';
    echo $szResult;
    die;
  }
  $groups = isset( $_REQUEST['groups'] ) ? $_REQUEST['groups'] : "";
  $layers = isset( $_REQUEST['layers'] ) ? $_REQUEST['layers'] : "";
  if (isset($_REQUEST['extent']))$extent=$_REQUEST['extent'];
  else   
  {
    $szResult= 'alert ("Error missing map extent");';
    echo $szResult;
    die;
  }

  $aExtent=explode('|',$extent);
  
  //calculate img dimantion for scale and extent!!
  //in realtà non serve perche il kamappo già mi manda i layer visibili alle varie scale
  
  $inchesPerUnit = array(1, 12, 63360.0, 39.3701, 39370.1, 4374754);
  $geoWidth = abs($aExtent[2]-$aExtent[0]);
  $geoHeight = abs($aExtent[3]-$aExtent[1]);
  //$szResult=$geoWidth." ".$geoHeight." ";
  $width=round(($geoWidth/$scale)*$oMap->resolution*$inchesPerUnit[$oMap->units]);
  $height=round(($geoHeight/$scale)*$oMap->resolution*$inchesPerUnit[$oMap->units]);
  //$szResult.= $width." ".$height;
  //SETTING MAP EXTENT. 
  $oMap->setExtent($aExtent[0],$aExtent[1],$aExtent[2],$aExtent[3]);

  //SETTING img width height.
  $oMap->setSize($width,$height);
  
  $oMap->preparequery();
  //$szResult.= " ".$oMap->scale;
  //echo $szResult;
  
  
// // SETTING QUERY POINT
  if($q_type==0){
    $point = ms_newPointObj();
    $point->setXY($coords[0],$coords[1]);
//    $oMap->zoompoint(2,$point,$oMap->width,$oMap->height,$oMap->extent);
  }elseif($q_type==1)//query by rect
  {
   $rect=ms_newRectObj();
   $rect->setextent($coords[0],$coords[3],$coords[2],$coords[1]);
   //$oMap->setExtent($coords[0],$coords[3],$coords[2],$coords[1]);
   }else
  {
    $szResult= 'alert ("bad query type");';
    echo $szResult;
    die;
  }
  $oMap->preparequery();
  $nLayers = $oMap->numlayers;
  $aszLayers = array();
  if ($groups || $layers)
  {
    /* Draw only specified layers instead of default from mapfile*/
    if ($layers) $aszLayers = explode(",", $layers);
    if ($groups) $aszGroups = explode(",", $groups);
    $szTest="";
    for($i=0;$i<$nLayers;$i++)
    {
      $oLayer = $oMap->getLayer($i);
       if (($oLayer->type != MS_LAYER_RASTER) && $oLayer->isVisible() &&
        (($aszGroups && in_array($oLayer->group,$aszGroups)) ||
         ($aszLayers && in_array($oLayer->name,$aszLayers))))
       {
         $oLayer->set("status", MS_ON );
         $szTest.=$oLayer->name." ";
       }
       else $oLayer->set("status", MS_OFF );
    }
  	//Execute query
    if($q_type==0)$check_query = $oMap->queryByPoint($point,MS_MULTIPLE,0);
    else $check_query =$oMap->queryByRect($rect);
    if($check_query==MS_SUCCESS)$oMap->savequery($szQueryCacheDir."query.bin");
   // $szResult.= "var queryResult=$check_query;var sessionId='$sessionId';alert('$szTest')";
   $szResult.= "var queryResult=$check_query;this.sessionId='$sessionId'";
  }else{
     $szResult= 'alert ("Nessun layer o gruppo interrogabile");';
     echo $szResult;
     die;
  }
  echo $szResult;
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

