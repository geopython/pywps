<?php
/**********************************************************************
 *
 * $Id: test.php,v 1.4 2006/02/07 03:19:55 pspencer Exp $
 *
 * purpose: generate test tiles without requiring a map file, for
 *          TESTING only
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original kaTool code was written by DM Solutions Group.
 *
 * TODO:
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

$top = $_REQUEST['t'];
$left = $_REQUEST['l'];
$width = $_REQUEST['w'];
$height = $_REQUEST['h'];
$scale = $_REQUEST['s'];

if (!extension_loaded('MapScript'))
{
    dl('php_mapscript.'.PHP_SHLIB_SUFFIX );
}
if (!extension_loaded('gd'))
{
    dl('php_gd.'.PHP_SHLIB_SUFFIX);
}

$oImg = imagecreate( $width, $height );

$randColor = imagecolorallocate( $oImg, rand(128, 255), rand(128,255), rand(128,255) );
$black = imagecolorallocate($oImg, 0, 0, 0);
imagefill($oImg, 0, 0, $randColor );
imagestring ( $oImg, 3, 10, 10, $top." x ".$left, $black );
// make sure this thing doesn't cache
//header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");
//header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");
//header("Cache-Control: no-store, no-cache, must-revalidate");
//header("Cache-Control: post-check=0, pre-check=0", false);
//header("Pragma: no-cache");
header("Content-type: image/png");
imagepng($oImg);
?>
