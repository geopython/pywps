<?php
/**********************************************************************
 *
 * $Id: legend.php,v 1.8 2006/02/19 18:17:26 pspencer Exp $
 *
 * purpose: server-side support for a mapserver-based legend.  This is
 *          deprecated by a new client-side only legend.
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * The original legend.php code was written by DM Solutions Group.
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

if (!extension_loaded('MapScript'))
{
    dl( $szPHPMapScriptModule );
}

$groups = isset( $_REQUEST['g'] ) ? $_REQUEST['g'] : "";
$layers = isset( $_REQUEST['layers'] ) ? $_REQUEST['layers'] : "";

$oMap = ms_newMapObj($szMapFile);
$oPoint = ms_newPointObj( );
$oPoint->setXY($oMap->width/2, $oMap->height/2 );
$oMap->zoomScale( $_REQUEST['scale'], $oPoint, $oMap->width, $oMap->height, $oMap->extent );

$aszLayers = array();

if ($groups || $layers)
{
    /* Draw only specified layers instead of default from mapfile*/
    if ($layers)
    {
        $aszLayers = explode(",", $layers);
    }

    if ($groups)
    {
        $aszGroups = explode(",", $groups);
    }
    $nLayers = $oMap->numlayers;
    for($i=0;$i<$nLayers;$i++)
    {
        $oLayer = $oMap->getLayer($i);
        if (($aszGroups && in_array($oLayer->group,$aszGroups)) ||
            ($aszLayers && in_array($oLayer->name,$aszLayers)) ||
            ($aszGroups && $oLayer->group == '' && 
             in_array( "__base__", $aszGroups)))
        {
            $oLayer->set("status", MS_ON );
        }
        else
        {
            $oLayer->set("status", MS_OFF );
        }
    }
}
header( 'Content-type: image/png' );
$oImg = $oMap->drawLegend();

$szURL = $oImg->saveImage("");
?>
