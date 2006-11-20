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
  if(isset($_REQUEST['layer'])) $szLayer= $_REQUEST['layer'];
   else{
    $szResult= 'alert ("layer query required");';
    echo $szResult;
    die;
  }
  
  if(isset($_REQUEST['sIndex'])) $sIndex= $_REQUEST['sIndex'];
   else{
    $szResult= 'alert ("sIndex required");';
    echo $szResult;
    die;
  }
  
  if(isset($_REQUEST['tIndex'])) $tIndex= $_REQUEST['tIndex'];
   else{
    $szResult= 'alert ("tIndex required");';
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
    
    //REQUEST HANDLING
if (empty ($_REQUEST['searchstring'])) {

	$searchstring = "/Empty/";

	echo "Input string";

	die;

} else {

	// icnv is used only if your page encoding is different from data source encoding
	// in ISO-8859-13 encoding place your code
	$searchstring = iconv("UTF-8", "ISO-8859-13", $_REQUEST['searchstring']);
	//$searchstring = "/" . $searchstring . "/i";

}

$oMap->preparequery();
$oLayer = $oMap->getLayerByName($szLayer); //number of layers in map
$totResults = 0;


$szSearchfield = $oLayer->getMetaData('searchfield');


$szResult = $oMap->queryByIndex($oLayer->index,$tIndex,$sIndex);
if ($szResult == MS_SUCCESS)
{ 
	
	$oMap->savequery($szQueryCacheDir."query.bin");
	
	//print_r($oShape);
	
	
	
	//$szResult=0;
	echo"queryResult= $szResult;this.sessionId='$sessionId';";
	
} else {
	
	echo"queryResult= $szResult;";
}

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
