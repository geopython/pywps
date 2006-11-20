<?php
/**********************************************************************
 *
 * $Id: tile_nocache.php,v 1.8 2006/07/05 15:17:35 dmorissette Exp $
 *
 * purpose: a simple phpmapscript-based tile renderer that implements
 *          rudimentary caching for reasonable efficiency.  Note the
 *          cache never shrinks in this version so your disk could
 *          easily fill up!
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
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

include_once( '../include/config.php' );

$tileBuffer = 10; // integer number of pixels

/* get the various request parameters
 * also need to make sure inputs are clean, especially those used to
 * build paths and filenames
 */

$top = isset( $_REQUEST['t'] ) ? intval($_REQUEST['t']) : 0;
$left = isset( $_REQUEST['l'] ) ? intval($_REQUEST['l']) : 0;
$scale = isset( $_REQUEST['s'] ) ? intval($_REQUEST['s']) : $anScales[0];
$groups = isset( $_REQUEST['g'] ) ? $_REQUEST['g'] : "";
$layers = isset( $_REQUEST['layers'] ) ? $_REQUEST['layers'] : "";

// dynamic imageformat ----------------------------------------------
//use the function in config.php to set the output format
if (isset($_REQUEST['i']))
   setOutputFormat($_REQUEST['i']);
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

/* Check that user has the rights to see requested group(s).
 */
if (isset($oAuth) && $groups)
{
    $aszGroups = explode(",", $groups);

    foreach ($aszGroups as $thisGroup)
    {
        if (!$oAuth->testPrivilege($thisGroup))
        {
            /* User is not authorized. */
            echo "You are not authorized to access group '$thisGroup'\n";
            exit;
        }
    }
}

if (!extension_loaded('MapScript')) {
    dl( $szPHPMapScriptModule );
}
if (!extension_loaded('gd')) {
    dl( $szPHPGDModule);
}

$oMap = ms_newMapObj($szMapFile);

/* tile width/height */
$oMap->set('width', $tileWidth + (2 * $tileBuffer));
$oMap->set('height', $tileHeight + (2 * $tileBuffer));

/* Tell MapServer to not render labels inside the metaBuffer area
 * (new in 4.6)
 * TODO: Until MapServer bugs 1353/1355 are resolved, we need to
 * pass a negative value for "labelcache_map_edge_buffer"
 */
$oMap->setMetadata("labelcache_map_edge_buffer", -$metaBuffer);

$inchesPerUnit = array(1, 12, 63360.0, 39.3701, 39370.1, 4374754);
$geoWidth = $scale / ($oMap->resolution * $inchesPerUnit[$oMap->units]);
$geoHeight = $scale / ($oMap->resolution * $inchesPerUnit[$oMap->units]);
$geoBuffer = $tileBuffer * $scale / ($oMap->resolution * $inchesPerUnit[$oMap->units]);

/* draw the metatile */
$minx = ($left * $geoWidth) - $geoBuffer;
$maxx = $minx + $geoWidth * $oMap->width;
$maxy = (-1 * $top * $geoHeight) + $geoBuffer;
$miny = $maxy - $geoHeight * $oMap->height;

// if they aren't already set, set minx miny etc
if(!isset($_REQUEST['minx'])) {
    $_REQUEST['minx'] = $minx;
}
if(!isset($_REQUEST['miny'])) {
    $_REQUEST['miny'] = $miny;
}
if(!isset($_REQUEST['maxx'])) {
    $_REQUEST['maxx'] = $maxx;
}
if(!isset($_REQUEST['maxy'])) {
    $_REQUEST['maxy'] = $maxy;
}

$nLayers = $oMap->numlayers;
$oMap->setExtent($minx, $miny, $maxx, $maxy);
$oMap->selectOutputFormat($szMapImageFormat);
$aszLayers = array();
if($groups || $layers) {
    /* Draw only specified layers instead of default from mapfile*/
    if($layers) {
        $aszLayers = explode(",", $layers);
    }
    if($groups) {
        $aszGroups = explode(",", $groups);
    }
    for($i=0;$i<$nLayers;$i++) {
        $oLayer = $oMap->getLayer($i);
        if(($aszGroups && in_array($oLayer->group, $aszGroups)) ||
           ($aszLayers && in_array($oLayer->name, $aszLayers)) ||
           ($aszGroups && $oLayer->group == '' && in_array( "__base__", $aszGroups))) {
            $oLayer->set("status", MS_ON );
            /* Variable substitution
             * Looks through the mapfile for any pattern like %variable%
             * and then replaces that with the value of $_REQUEST['variable'].
             * Works for layer->data, layer->connection, layer->filter, and
             * for class->expression.  If %variable% exists in a layer but not
             * in the request, then the layer is turned off before drawing.
             */
            $data = $oLayer->data;
            if(preg_match_all("/%(\w+)%/", $data, $matches, PREG_SET_ORDER) > 0) {
                $matchArray = array();
                $replaceArray = array();
                foreach($matches as $match) {
                    $key = $match[1];
                    if(isset($_REQUEST[$key])) {
                        $value = get_magic_quotes_gpc() ? stripslashes($_REQUEST[$key]) : $_REQUEST[$key];
                        array_push($matchArray, $match[0]);
                        array_push($replaceArray, $value);
                    } else {
                        $oLayer->set("status", MS_OFF);
                        break;
                    }
                }
                $oLayer->set("data", str_replace($matchArray, $replaceArray, $data));
            }
            $connection = $oLayer->connection;
            if(preg_match_all("/%(\w+)%/", $connection, $matches, PREG_SET_ORDER) > 0) {
                $matchArray = array();
                $replaceArray = array();
                foreach($matches as $match) {
                    $key = $match[1];
                    if(isset($_REQUEST[$key])) {
                        $value = get_magic_quotes_gpc() ? stripslashes($_REQUEST[$key]) : $_REQUEST[$key];
                        array_push($matchArray, $match[0]);
                        array_push($replaceArray, $value);
                    } else {
                        $oLayer->set("status", MS_OFF);
                        break;
                    }
                }
                $oLayer->set("connection", str_replace($matchArray, $replaceArray, $connection));
            }
            $filter = $oLayer->getFilter();
            if(preg_match_all("/%(\w+)%/", $filter, $matches, PREG_SET_ORDER) > 0) {
                $matchArray = array();
                $replaceArray = array();
                foreach($matches as $match) {
                    $key = $match[1];
                    if(isset($_REQUEST[$key])) {
                        $value = get_magic_quotes_gpc() ? stripslashes($_REQUEST[$key]) : $_REQUEST[$key];
                        array_push($matchArray, $match[0]);
                        array_push($replaceArray, $value);
                    } else {
                        $oLayer->set("status", MS_OFF);
                        break;
                    }
                }
                $oLayer->setFilter(str_replace($matchArray, $replaceArray, $filter));
            }
            for($j = 0; $j < $oLayer->numclasses; ++$j) {
                $oClass = $oLayer->getClass($j);
                $expression = $oClass->getExpression();
                if(preg_match_all("/%(\w+)%/", $expression, $matches, PREG_SET_ORDER) > 0) {
                    $matchArray = array();
                    $replaceArray = array();
                    foreach($matches as $match) {
                        $key = $match[1];
                        if(isset($_REQUEST[$key])) {
                            $value = get_magic_quotes_gpc() ? stripslashes($_REQUEST[$key]) : $_REQUEST[$key];
                            array_push($matchArray, $match[0]);
                            array_push($replaceArray, $value);
                        } else {
                            $oLayer->set("status", MS_OFF);
                            break;
                        }
                    }
                    $oClass->setExpression(str_replace($matchArray, $replaceArray, $expression));
                }
            }
        }
        else {
            $oLayer->set("status", MS_OFF );
        }
    }
    //need transparency if groups or layers are used
    $oMap->outputformat->set("transparent", MS_ON);
}
else {
    $oMap->outputformat->set("transparent", MS_OFF);
}

$oImg = $oMap->draw();
($tmpFileName = tempnam($oMap->web->imagepath, 'tmp')) or exit("Can't create new file in ".addslashes($oMap->web->imagepath));
$szMetaImg = preg_match('/\.\w+$/', $tmpFileName) ? preg_replace('/\.\w+$/', $szImageExtension, $tmpFileName) : $tmpFileName . $szImageExtension;
$oImg->saveImage($szMetaImg);
$oImg->free();
eval("\$oGDImg = ".$szMapImageCreateFunction."('".$szMetaImg."');");
eval("\$oTile = ".$szImageCreateFunction."( ".$tileWidth.",".$tileHeight." );");
// Allocate BG color for the tile (in case the metatile has transparent BG)
$nTransparent = imagecolorallocate($oTile, $oMap->imagecolor->red, $oMap->imagecolor->green, $oMap->imagecolor->blue);
imagecolortransparent( $oTile,$nTransparent);
// center the tile on the image already created (subtracting the buffer)
$tileTop = $tileBuffer;
$tileLeft = $tileBuffer;
imagecopy($oTile, $oGDImg, 0, 0, $tileLeft, $tileTop, $tileWidth, $tileHeight);
imagedestroy($oGDImg);
$oGDImg = null;
unlink($szMetaImg);

header("Content-Type: " . $szImageHeader);
//header("Content-Length: " . strlen($oTile));
header("Expires: " . date("D, d M Y H:i:s GMT", time() + 31536000));
header("Cache-Control: max-age=31536000, must-revalidate");
eval("$szImageOutputFunction(\$oTile);");

exit;
?>
