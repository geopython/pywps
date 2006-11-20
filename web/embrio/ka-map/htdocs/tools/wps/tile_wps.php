<?php
/**********************************************************************
 * $Id: tile_query.php,v 1.1 2006/06/25 17:40:40 lbecchi Exp $
 * 
 * purpose: a simple phpmapscript-based tile renderer used to render query layer (bug: 1508)
 *
 * author: Andrea Cappugi & Lorenazo Becchi based on tile.php Paul Spencer (pspencer@dmsolutions.ca)
 *
 * modifications by Daniel Morissette (dmorissette@dmsolutions.ca)
 *
 * TODO:
 *
 *   - remove debugging stuff (not really needed now)
 *
 **********************************************************************
 *
 * Copyright (c) 2005, DM Solutions Group Inc.
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
 * the tile renderer accepts several parameters and returns a tile image from
 * the cache, creating the tile only if necessary.
 *
 * all requests include the pixel location of the request at a certain scale
 * and this script figures out the geographic location of the tile from the
 * scale assuming that 0,0 in pixels is 0,0 in geographic units
 *
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
 /*parameter*/
   
//echo "io lupo";
include_once( '../../../include/config.php' );
error_reporting ( E_ALL );
/* bug 1253 - root permissions required to delete cached files */
$orig_umask = umask(0);

/* create the main cache directory if necessary */
if (!@is_dir($szMapCacheDir))
    makeDirs($szMapCacheDir);

/* get the various request parameters
 * also need to make sure inputs are clean, especially those used to
 * build paths and filenames
 */
$qId=isset( $_REQUEST['id'] ) ? $_REQUEST['id'] : null;
$sessionId=isset( $_REQUEST['sessionId'] ) ? $_REQUEST['sessionId'] : null;
$top = isset( $_REQUEST['t'] ) ? intval($_REQUEST['t']) : 0;
$left = isset( $_REQUEST['l'] ) ? intval($_REQUEST['l']) : 0;
$scale = isset( $_REQUEST['s'] ) ? intval($_REQUEST['s']) : $anScales[0];
$bForce = isset($_REQUEST['force'])? true : false;
$groups = isset( $_REQUEST['g'] ) ? $_REQUEST['g'] : "";
$layers = isset( $_REQUEST['layers'] ) ? $_REQUEST['layers'] : "";
$timestamp = isset($_REQUEST['ts']) ? $_REQUEST['ts'] : '';
$interval = isset($_REQUEST['interval']) ? $_REQUEST['interval'] : 300;
$version = isset($_REQUEST['version']) ? $_REQUEST['version'] : '';


//echo $layers."--".$groups."<br>";

// dynamic imageformat ----------------------------------------------
//use the function in config.php to set the output format
$useAlphaCh = false;
if (isset($_REQUEST['i'])) {
   setOutputFormat( $_REQUEST['i'] );
   if (strtoupper($_REQUEST['i']) == 'ALPHA') {
   	$useAlphaCh = true;
   }
}

//----------------------------------------------------------------

/* tileid=t#####l#### can be used instead of t+l parameters. Useful in
 * regenerating the cache for instance.
 */
if (isset( $_REQUEST['tileid']) &&
    preg_match("/t(-?\d+)l(-?\d+)/", $_REQUEST['tileid'], $aMatch) )
{
    $top = intval($aMatch[1]);
    $left = intval($aMatch[2]);
}

/* Calculate the metatile's top-left corner coordinates.
 * Include the $metaBuffer around the metatile to account for various
 * rendering issues happening around the edge of a map
 */
$metaLeft = floor( ($left)/($tileWidth*$metaWidth) ) * $tileWidth * $metaWidth;
$metaTop = floor( ($top)/($tileHeight*$metaHeight) ) * $tileHeight *$metaHeight;
$szMetaTileId = "t".$metaTop."l".$metaLeft;
$metaLeft -= $metaBuffer;
$metaTop -= $metaBuffer;

/* caching is done by scale value, then groups and layers and finally metatile
 * and tile id. Create a new directory if necessary
 */
$szGroupDir = $groups != "" ? normalizeString($groups) : "def";
$szLayerDir = $layers != "" ? normalizeString($layers) : "def";
$szQueryCacheDir=$szBaseCacheDir."/sessions/".$sessionId."/QuerySys/".$szMap."/".$qId."/"; 
//echo $szQueryCacheDir."<br>";
$szCacheDir = $szQueryCacheDir."/".$scale."/".$szGroupDir."/".$szLayerDir."/".$szMetaTileId;

//echo $szCacheDir;

if (!@is_dir($szCacheDir))
    makeDirs($szCacheDir);

/* resolve cache hit - clear the os stat cache if necessary */
$szTileId = "t".$top."l".$left;
$szCacheFile = $szCacheDir."/".$szTileId.$szImageExtension;
clearstatcache();

$szMetaDir = $szCacheDir."/meta";
if (!@is_Dir($szMetaDir))
    makeDirs($szMetaDir);
    
/* timestamp checking - ignore requests more than the interval in the future (bad client)*/
$now = gmttime();
if ($timestamp != '' && $now >= $timestamp - $interval) {
    //get the metatile cache timestamp
    $ts_file = $szMetaDir."/timestamp";
    clearstatcache();
    if (!file_exists($ts_file)) {
        $bForce = true;
    } else {
        $h = fopen($ts_file,"r");
        $meta_timestamp = fread($h,filesize($ts_file));
        fclose($h);
        if ($timestamp > $meta_timestamp + $interval) {
            $bForce = true;
        }    
    }
}

if ($version != '') {
    $version_file = $szMetaDir."/version";
    clearstatcache();
    if (!file_exists($version_file)) {
        $bForce = true;
    } else {
        $h = fopen($version_file, 'r');
        $meta_version = fread($h,filesize($version_file));
        fclose($h);
        if ($meta_version < $version) {
            $bForce = true;
        }
    }
}

/* simple locking in case there are several requests for the same meta
   tile at the same time - only draw it once to help with performance */
$szLockFile = $szMetaDir."/lock_".$metaTop."_".$metaLeft;
$fpLockFile = fopen($szLockFile, "a+");
clearstatcache();
if (!file_exists($szCacheFile) || $bForce)
{
    flock($fpLockFile, LOCK_EX);
    fwrite($fpLockFile, ".");

    //check once more to see if the cache file was created while waiting for
    //the lock
    clearstatcache();
    if (!file_exists($szCacheFile) || $bForce)
    {
        if (!extension_loaded('MapScript'))
        {
            dl( $szPHPMapScriptModule );
        }
        if (!extension_loaded('gd'))
        {
            dl( $szPHPGDModule);
        }

        //modified by kappu
        $oMap = ms_newMapObj($szMapFile);
        $check=$oMap->loadquery($szBaseCacheDir."/sessions/".$sessionId."/QuerySys/".$szMap."/".$qId."/query.bin");
		if($check)die;//if fail to lad the saved query die!!
		$oMap->querymap->set('width', $tileWidth * $metaWidth + 2*$metaBuffer);
		$oMap->querymap->set('height', $tileHeight * $metaHeight + 2*$metaBuffer);
		$oMap->querymap->set('style', 2 ); //setting to hilite syle
	
        /* Metatile width/height include 2x the metaBuffer value */
        $oMap->set('width', $tileWidth * $metaWidth + 2*$metaBuffer);
        $oMap->set('height', $tileHeight * $metaHeight + 2*$metaBuffer);

        /* Tell MapServer to not render labels inside the metaBuffer area
         * (new in 4.6)
         * TODO: Until MapServer bugs 1353/1355 are resolved, we need to
         * pass a negative value for "labelcache_map_edge_buffer"
         */
        $oMap->setMetadata("labelcache_map_edge_buffer", -$metaBuffer);

        $inchesPerUnit = array(1, 12, 63360.0, 39.3701, 39370.1, 4374754);
        $geoWidth = $scale/($oMap->resolution*$inchesPerUnit[$oMap->units]);
        $geoHeight = $scale/($oMap->resolution*$inchesPerUnit[$oMap->units]);
			
        /* draw the metatile */
        $minx = $metaLeft * $geoWidth;
        $maxx = $minx + $geoWidth * $oMap->width;
        $maxy = -1 * $metaTop * $geoHeight;
        $miny = $maxy - $geoHeight * $oMap->height;

        $nLayers = $oMap->numlayers;
        $oMap->setExtent($minx,$miny,$maxx,$maxy);
        $oMap->selectOutputFormat( $szMapImageFormat );
        $aszLayers = array();
       if ($groups || $layers)
        {
            /* Draw only specified layers instead of default from mapfile*/
        //    if ($layers)
         //   {
          //      $aszLayers = explode(",", $layers);
           // }

            //if ($groups)
            //{
            /*    $aszGroups = explode(",", $groups);
            }
           */ for($i=0;$i<$nLayers;$i++)
            {
               $oLayer = $oMap->getLayer($i);
               $totR = $oLayer->getNumResults();	
               $szColor =$oLayer->getMetaData("rgbColor");
		
				/*get hilite color if set in map file*/ 
		 		if ($szColor != '') {
			 		$Color=  explode(',',$szColor);
			 		$aColor=array('R'=>$Color[0],'G'=>$Color[1],'B'=>$Color[2]);
		 		}
               else $aColor= array('R'=>0,'G'=>255,'B'=>100);
               /*
                if ((($aszGroups && in_array($oLayer->group,$aszGroups)) ||
                    ($aszLayers && in_array($oLayer->name,$aszLayers)) ||
                    ($aszGroups && $oLayer->group == '' &&
                     in_array( "__base__", $aszGroups)))&& $oLayer->type!=3)*/
                if ($totR>0)
                {
                  // echo "modifico LAyer: $oLayer->name <br>";
                	$oLayer->set("status", MS_ON );
                    /*modificare il colore della linea!!*/
					
					$nClass=$oLayer->numclasses;
					$layerType=$oLayer->type;
	
	
					if($layerType>=0 && $layerType<=2){
				   for($n=0;$n<$nClass;$n++){
		
					/*da gestire i diversi tipi di classe poligoni lineee cazzi e mazzi!!*/
						$class=$oLayer->getClass($n);
						switch ($layerType) {
   							case 0:
       							point($class);
       						break;
   							case 1:
   								line($class);
   							break;
   							case 2:
    							polygonStyle($class);
   							break;
   							default:
   							die;
						}
						
					}
					}	

                }else
                {
                    $oLayer->set("status", MS_OFF );
                }
            }
            //need transparency if groups or layers are used
            $oMap->outputformat->set("transparent", MS_ON );
        }
        else
        {
            $oMap->outputformat->set("transparent", MS_OFF );
        }

        //record timestamp for this metatile
        $h = fopen($szMetaDir.'/timestamp', 'w+');
        fwrite($h, $now);
        fclose($h);
        
        //record mapfile version for this metatile
        $h = fopen($szMetaDir.'/version', 'w+');
        fwrite($h, $version);
        fclose($h);
        
        $szMetaImg = $szMetaDir."/t".$metaTop."l".$metaLeft.$szImageExtension;
        $oImg = $oMap->drawQuery();
        $oImg->saveImage($szMetaImg);
		$oImg->free();

        eval("\$oGDImg = ".$szMapImageCreateFunction."('".$szMetaImg."');");
        if ($bDebug)
        {
            $blue = imagecolorallocate($oGDImg, 0, 0, 255);
            imagerectangle($oGDImg, 0, 0, $tileWidth * $metaWidth - 1, $tileHeight * $metaHeight - 1, $blue );
        }
        for($i=0;$i<$metaWidth;$i++)
        {
            for ($j=0;$j<$metaHeight;$j++)
            {
                eval("\$oTile = ".$szImageCreateFunction."( ".$tileWidth.",".$tileHeight." );");
                // Allocate BG color for the tile (in case the metatile has transparent BG)
		if (!$useAlphaCh) {
                    $nTransparent = imagecolorallocate($oTile, $oMap->imagecolor->red, $oMap->imagecolor->green, $oMap->imagecolor->blue);
                    //if ($oMap->outputformat->transparent == MS_ON)
                    //{
                        imagecolortransparent( $oTile,$nTransparent);
                    //}
		}
                $tileTop = $j*$tileHeight + $metaBuffer;
                $tileLeft = $i*$tileWidth + $metaBuffer;
		if ($useAlphaCh) {
		  ImageAlphaBlending($oTile, false);
		  imagesavealpha($oTile, true);
		}
                imagecopy( $oTile, $oGDImg, 0, 0, $tileLeft, $tileTop, $tileWidth, $tileHeight );
                /* debugging stuff */
                if ($bDebug)
                {
                    $black = imagecolorallocate($oTile, 1, 1, 1);
                    $green = imagecolorallocate($oTile, 0, 128, 0 );
                    $red = imagecolorallocate($oTile, 255, 0, 0);
                    imagerectangle( $oTile, 1, 1, $tileWidth-2, $tileHeight-2, $green );
                    imageline( $oTile, 0, $tileHeight/2, $tileWidth-1, $tileHeight/2, $red);
                    imageline( $oTile, $tileWidth/2, 0, $tileWidth/2, $tileHeight-1, $red);
                    imagestring ( $oTile, 3, 10, 10, ($metaLeft+$tileLeft)." x ".($metaTop+$tileTop), $black );
                    imagestring ( $oTile, 3, 10, 30, ($minx+$i*$geoWidth)." x ".($maxy - $j*$geoHeight), $black );
                }
                $szTileImg = $szCacheDir."/t".($metaTop+$tileTop)."l".($metaLeft+$tileLeft).$szImageExtension;
                eval("$szImageOutputFunction( \$oTile, '".$szTileImg."' );");
                imagedestroy($oTile);
                $oTile = null;
            }
        }
        if ($oGDImg != null)
        {
            imagedestroy($oGDImg);
            $oGDImg = null;
        }
        if (!$bDebug)
        {
            unlink( $szMetaImg );
        }
    }
    //release the exclusive lock
    flock($fpLockFile, LOCK_UN );
}

//acquire shared lock for reading to prevent a problem that could occur
//if a tile exists but is only partially generated.
flock($fpLockFile, LOCK_SH);

$h = fopen($szCacheFile, "r");
header("Content-Type: ".$szImageHeader);
header("Content-Length: " . filesize($szCacheFile));
header("Expires: " . date( "D, d M Y H:i:s GMT", time() + 31536000 ));
header("Cache-Control: max-age=31536000, must-revalidate" );
fpassthru($h);
fclose($h);

//release lock
fclose($fpLockFile);

/* bug 1253 - root permissions required to delete cached files */
umask($orig_umask);

exit;

function gmttime() {
   $aNow = localtime();
   $iDelta = gmmktime(1, 1, 1, 1, 1, 1980, $aNow[8]) - mktime(1, 1, 1, 1, 1, 1980, $aNow[8]);
   $theTime = localtime(time() - $iDelta, 0);
   $ts = mktime($theTime[2],$theTime[1],$theTime[0],$theTime[4]+1,$theTime[3],$theTime[5]+1900);
   $ts -= $theTime[8] * 3600; //daylight savings???
   return $ts;
}
function polygonStyle($class) {
global $aColor;
$check=true;

//looking for style with outlinecolor
$nStyles=$class->numstyles;
  for($n=$nStyles-1;$n>=0;$n--){
    $styleObj=$class->getStyle($n);
    $colorObj    = $styleObj->outlinecolor;
    if ($colorObj->red!=-1){
    //the first style have outlinecolor
      $colorObj->setRGB($aColor['R'], $aColor['G'], $aColor['B']);
      $check=false;
      break;
    }
}
if($check){
  $styleObj=$class->getStyle(0);
  $colorObj    = $styleObj->outlinecolor;
  $colorObj->setRGB($aColor['R'], $aColor['G'], $aColor['B']);
}
}
function line($class) {
global $aColor;
$check=true;

//looking for style with outlinecolor
$nStyles=$class->numstyles;
  for($n=$nStyles-1;$n>=0;$n--){
    $styleObj=$class->getStyle($n);
    $colorObj    = $styleObj->color;
    if ($colorObj->red!=-1){
    //the first style have outlinecolor
      $colorObj->setRGB($aColor['R'], $aColor['G'], $aColor['B']);
      $check=false;
      break;
    }
}
if($check){
  $styleObj=$class->getStyle(0);
  $colorObj    = $styleObj->color;
  $colorObj->setRGB($aColor['R'], $aColor['G'], $aColor['B']);
}
}
function point($class) {
$check=true;
global $aColor;
//looking for style with outlinecolor
$nStyles=$class->numstyles;
  for($n=$nStyles-1;$n>=0;$n--){
    $styleObj=$class->getStyle($n);
    $colorObj    = $styleObj->color;
    if ($colorObj->red!=-1){
    //the first style have outlinecolor
      $colorObj->setRGB($aColor['R'], $aColor['G'], $aColor['B']);
      $check=false;
      break;
    }
}
if($check){
  $styleObj=$class->getStyle(0);
  $colorObj    = $styleObj->color;
  $colorObj->setRGB($aColor['R'], $aColor['G'], $aColor['B']);
}
}
?>
