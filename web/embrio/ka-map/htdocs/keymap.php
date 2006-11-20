<?php
/**********************************************************************
 *
 * $Id: keymap.php,v 1.11 2006/02/07 03:19:55 pspencer Exp $
 *
 * purpose: server-side support for keymap
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original keymap.php code was written by DM Solutions Group.
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
 
 /******************************************************************************
 *
 * This file is called from the kaMap! module using XMLHttpRequest.  It returns
 * some javascript that sets up the keymap object in the client.  The URL for
 * the keymap image points back to this file, which obtains the path to the
 * image from the map file and returns the image directly to the client.
 * 
 *****************************************************************************/
include_once('../include/config.php');

if (!extension_loaded('MapScript'))
{
    dl( $szPHPMapScriptModule );
}

$oMap = ms_newMapObj($szMapFile);

/* this gets excuted to get the keymap image - this is the second pass,
 * the first pass goes through the code below
 */
if (isset($_GET['loadImage']) && $_GET['loadImage']=='true')
{
    $img = $oMap->reference->image;
    if (substr($img, 0, 1) != '/' && substr($img,1,1) != ':')
    {
        $szMapPath = dirname($szMapFile);
        if (substr($szMapFile, 0, 1) != '/' && substr($szMapFile,1,1) != ':')
        {
            $szMapPath = realpath(dirname(__FILE__)."/".dirname($szMapFile));
        }
        $img = realpath( $szMapPath."/".$img );
    }
    else
    {
        $img = realpath( $img );
    }
    //echo $img; exit;
    //TODO: make this sensitive to the image extension
    $path_parts = pathinfo($img);
    switch($path_parts['extension']) {
        case 'gif':
            header( 'Content-type: image/gif');
            break;
        case 'jpg':
            header( 'Content-type: image/jpeg');
            break;
        case 'png':
            header( 'Content-type: image/png');
            break;
    }        
    readfile($img);
    exit;
}

$extent = $oMap->reference->extent->minx.",". 
          $oMap->reference->extent->miny.",".
          $oMap->reference->extent->maxx.",".
          $oMap->reference->extent->maxy;
$width = $oMap->reference->width;
$height = $oMap->reference->height;

//determine keymap.php url :(

$szURL = 'http';
if (isset($_SERVER['HTTPS'])&& strcasecmp($_SERVER['HTTPS'], 'off') != 0 )
    $szURL .= "s";
$szURL .= "://";
if (isset($_SERVER['HTTP_X_FORWARDED_HOST']))
    $szURL .= $_SERVER['HTTP_X_FORWARDED_HOST'];
else
{
    $szURL .= $_SERVER['HTTP_HOST'];
    if (!strpos($szURL,':')) 
    {  // check to make sure port is not already in SERVER_HOST variable
         if (isset($_SERVER['SERVER_PORT']) && $_SERVER['SERVER_PORT'] != '80')
               $szURL .= ":".$_SERVER['SERVER_PORT'];
    }
}

if( isset( $_SERVER['REQUEST_URI'] ) )
{
    if ((substr($szURL, -1, 1) != '/') &&
        (substr($_SERVER['REQUEST_URI'],0,1) != '/'))
    {
        $szURL .= "/";
    }
    $szURL .= dirname($_SERVER['REQUEST_URI'])."/";
}
else
{
    if ((substr($szURL, -1, 1) != '/') &&
        (substr($_SERVER['PHP_SELF'],0,1) != '/'))
    {
        $szURL .= "/";
    }
    $szURL .= dirname($_SERVER['PHP_SELF'])."/";
}

$szResult = "this.aExtents = new Array(".$extent.");";
$szResult .= "this.imgSrc = '".$szURL."keymap.php?loadImage=true';";
$szResult .= "this.imgWidth = ".$width.";";
$szResult .= "this.imgHeight = ".$height.";";
echo $szResult;
?>
