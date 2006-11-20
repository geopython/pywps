<?php
/**********************************************************************
 *
 * $Id: scalebar.php,v 1.7 2006/02/07 03:19:55 pspencer Exp $
 *
 * purpose: server-side support for a mapserver-based scalebar.  This is
 *          deprecated by a new client-side only scalebar (Tim Schaub).
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original scalebar.php code was written by DM Solutions Group.
 *
 * TODO:
 *
 *   - remove this file from cvs.
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
include_once('../include/config.php');

$szScalebarCacheDir = $szMapCacheDir."/scalebars";

/* create the main cache directory if necessary */
if (!@is_dir($szScalebarCacheDir))
    makeDirs($szScalebarCacheDir);

/* get the various request parameters 
 * also need to make sure inputs are clean, especially those used to
 * build paths and filenames
 */
$bForce = isset($_REQUEST['force'])? true : false;
$scale = isset( $_REQUEST['scale'] ) ? intval($_REQUEST['scale']) : $anScales[0];

/* resolve cache hit - clear the os stat cache if necessary */
$szCacheFile = $szScalebarCacheDir."/".$scale.$szImageExtension;
clearstatcache();


/* simple locking in case there are several requests for the same meta
   tile at the same time - only draw it once to help with performance */
$szLockFile = $szCacheFile.".lock";
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

        $oMap = ms_newMapObj($szMapFile);
        $oPoint = ms_newPointObj( );
        $oPoint->setXY($oMap->width/2, $oMap->height/2 );
        $oMap->zoomScale( $scale, $oPoint, $oMap->width, $oMap->height, $oMap->extent );

        $oImg = $oMap->drawScalebar();

        $oImg->saveImage($szCacheFile);
        $oImg->free();

    }
}

//acquire shared lock for reading to prevent a problem that could occur
//if the scalebar exists but is only partially generated.
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
exit;

?>
