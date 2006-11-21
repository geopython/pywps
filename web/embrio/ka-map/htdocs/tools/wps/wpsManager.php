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
  
  if(isset($_REQUEST['identifier'])) $identifier= $_REQUEST['identifier'];
   else{
    $szResult= 'alert ("identifier required");';
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
/*if (empty ($_REQUEST['searchstring'])) {

	$searchstring = "/Empty/";

	echo "Input string";

	die;

} else {

	// icnv is used only if your page encoding is different from data source encoding
	// in ISO-8859-13 encoding place your code
	$searchstring = iconv("UTF-8", "ISO-8859-13", $_REQUEST['searchstring']);
	//$searchstring = "/" . $searchstring . "/i";

}*/

//PARAMS TO BE PUT OUTSIDE THIS FILE
$cgi_executable = '/cgi-bin/wps.py';
$img_path = '';//the path where pywps store the image file

//Built up the request for PYWPS	
	
	$query_string = $cgi_executable."?service=wps&version=0.4.0&request=Execute&Identifier=$identifier&";
	$query_string .= "datainputs=". $datainputs;
	$query_string .= "&status=true&store=true";
	
//Extract the file name.This part need more debugging

	$dom = new DOMDocument();
	$dom->load($query_string);
	$CVR = $dom->getElementsByTagName('ComplexValueReference');
	$reference = $CVR->item(0)->getAttribute('reference');
	$aReference = explode('/',$reference);
	$filename = end($aReference);
	$pywps_outputPath.=$filename;
	
	//Update the mapfile with new layer

	$layer = ms_newLayerObj($oMap);
    $layer->set('name', $identifier);//not sure about wich name to choose
	$layer->set('status', MS_DEFAULT );
	$layer->set('data', $img_path.$filename);
	$layer->set('type', MS_LAYER_RASTER);
	
	//THIS PART SHOULD STAY ON A EXTERNAL SLD
	$class = ms_newClassObj($layer);
	$class->setExpression("1");
	$style = ms_newStyleObj($class);
	$style=$class->getStyle(0);
	$style->color->setRGB( -1,-1,-1);
	
	
if($map->save($szQueryCacheDir."/mapfile_buffer.map")){
	
	$oMap->savequery($szQueryCacheDir."query.bin");
	
	echo"/*output*/queryResult=1;this.sessionId='$sessionId';";
	
} else {
	
	echo"/*output*/queryResult=0;";
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
