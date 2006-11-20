<?php
/******************************************************************************
 * $Id: init.php,v 1.41 2006/07/05 15:17:35 dmorissette Exp $
 ******************************************************************************
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
 ******************************************************************************
 * kaMap! session initialization file
 *
 * This file is called from the kaMap! module using XMLHttpRequest.  The result
 * is evaluated as javascript and should initialize the kaMap! instance with
 * the map files and various related information about them.  This script
 * should only be called once per session.
 *
 * The per-map configuration comes from config.php.  The per-layer
 * configuration comes from metadata in the map file.  Metadata is
 * read from the first layer in a group.  Metadata on other layers in
 * the same group is ignored.
 *
 * The following per-layer metadata can be set:
 *
 * 'opacity' '[0-100]'
 *     sets the starting opacity of a group of layers, 0 is transparent.
 *
 *     The default is 100.
 *
 * 'tile_source' '[auto|cache|redraw|nocache]'
 *     Default is auto - tile.php draws from existing tiles if they
 *     exist, otherwise it creates new ones.  If set to cache, a web
 *     accessible cache must also be defined in config.php ($szBaseWebCache).
 *     With the cache option, tile.php will be avoided and tiles will be
 *     requested directly.  If set to redraw, this group of layers will not
 *     be rendered from tile cache but will be drawn every time a tile is
 *     requested. This makes rendering slower and causes higher load on the
 *     server but it does enable some form of dynamic content from the server.
 *     Note that redraw does not keep the browser from using cached images.
 *
 *     The default is auto
 *
 * 'redraw_interval' '[n > 0]'
 *     n is the number of seconds to use to consider the data stale
 *     when re-requesting a tile using redraw or refresh mode.  In
 *     these modes, a timestamp is appended to each tile request and
 *     if the tiles were re-generated more than this interval in the
 *     past, they will be re-generated.
 *
 * 'refresh_interval' '[n > 0]'
 *     n is the interval, in seconds, at which to automatically re-request
 *     the tiles for a layer.  This is only useful if combined with 
 *     "tile_source" "redraw" or "nocache".
 *
 * 'imageformat' '[DITHERED|PNG24|PNG|JPEG|GIF]'
 *     One of the valid formats for rendering tiles.  This overrides the
 *     overall map setting for output format for a specific group of
 *     layers.  This allows rendering vectors using a smaller format such
 *     as PNG and rendering raster imagery using PNG24 or JPEG (for instance)
 *
 *     Dithered is a special format that uses PNG24 in MapServer to render
 *     the group of layers but then reduces it to an 8-bit format (PNG)
 *     This option is especially useful when using antialiased labels and
 *     thick lines and you experience corruption of the colour table
 *     (especially noticeable in symbols).
 *
 *     The default is to use the config.php setting for the map.
 *
 * 'queryable' '[true|false]'
 *     Specify a group of layers as queryable.  This is primarily a hint
 *     to the kaLegend code to indicate a layer is queryable and to
 *     display a user control for that group in the interface to select
 *     that layer for a query.  It does not prevent a group of layers from
 *     being queried if it is not set.
 *
 *     This is false by default.
 *
 * Parameters that this script accepts are:
 *
 * map=<map name> - used to specify a map to start up with.  If not set, the
 * default map file from the config.php file will be used.  If set, it will
 * check to see if the requested map name exists in the config file and use
 * if it does.
 * modified by andre cappugi (cappu) 15-12-2005
 * consider if a group is visible at different scale:
 * if one group's layer is visible at a scale, group is visble.
 * modified by Andrea Cappugi and Lorenzo Becchi to add group visibility for
 * each map scale
 *
 * TODO:
 *
 *   - consider using more parameters from the map file via metadata
 *
 *****************************************************************************/
include_once( '../include/config.php' );

/* safely ensure the mapscript module is loaded ... its always loaded when
 * compiled as a module, or if it is configured into php.ini as an extension.
 * However, many installs are CGI and don't include mapscript in php.ini
 * by default.  Making this check enables making ka-Map work in most
 * situations without having to worry about the configuration of mapscript
 */
if (!extension_loaded('MapScript')) {
    dl( $szPHPMapScriptModule );
}

$szResult = '/*init*/'; //leave this in so the js code can detect errors

foreach($aszMapFiles as $key => $aszMapFile) {
    $oMap = ms_newMapObj( $aszMapFile['path'] );
    $szResult .= "aszScales=new Array('".implode("','", $aszMapFile['scales'])."');";
    $aGroups = array();
    $szLayers = '';
    
    //get mapfile version from metadata
    $szMapVersion = $oMap->getMetaData('version');
    
    /*
     * for this version, I have chosen to use groups to turn layers on and off
     * a special group called __base__ is created to hold all ungrouped layers
     * This group cannot be turned on/off in the interface (or at least not
     * using the default legend template
     */
    for($layerIndex = 0; $layerIndex < $oMap->numlayers; ++$layerIndex) {
        $oLayer = $oMap->getLayer($layerIndex);
        if($oLayer->group == '') {
            $oLayer->set('group', '__base__');
        }
    }
    $aGroups = $oMap->getAllGroupNames();

    /*cappu 15-12-2005 group's metadata should be write in first group layer
     * each group has status MS_ON if at least one group layer is MS_ON
     * each gropu is considered visible if at least ona group layer is visible
     * for considered scale, also if layer is MS_OFF
     */
    foreach($aGroups As $groupName) {
        /* Check that user has the rights to see this group.
         */
        if (isset($oAuth) && !$oAuth->testPrivilege($groupName))
        {
            /* User is not authorized. Skip this group */
            continue;
        }

        $aLayersIdx = $oMap->getLayersIndexByGroup($groupName);
        $oLayer = $oMap->getLayer($aLayersIdx[0]);

        /* detect layer opacity (default 100% opaque) */
        $opacity = $oLayer->getMetaData('opacity');
        if ($opacity == '') {
            $opacity = 100;
        }

        /* detect tile source options (cache, redraw, nocache, or auto) */
        $tileSource = strtolower($oLayer->getMetaData('tile_source'));
        if(($tileSource != 'cache') && ($tileSource != 'redraw') && ($tileSource != 'refresh') && ($tileSource != 'nocache')) {
            $tileSource = 'auto';
        }
        
        /* detect refresh interval for redraw layers */
        $redrawInterval = $oLayer->getMetaData('redraw_interval');
        if ($redrawInterval == '') {
            $redrawInterval = '-1';
        }
        
        /* detect automatic refresh interval */
        $refreshInterval = $oLayer->getMetaData('refresh_interval');
        if ($refreshInterval == '') {
            $refreshInterval = '-1';
        }

        /* detect if there should be a special
         * imageformat for this layer
         */
        $imageformat = $oLayer->getMetaData('imageformat');
        if($imageformat == '') {
            $imageformat = $oMap->imagetype;
        }

        /* detect if group should be queryable */
        $szQueryable = "false";
        if ($oLayer->getMetaData( "queryable" ) != "") {
            if(strcasecmp($oLayer->getMetaData("queryable"), "true") == 0)
                $szQueryable = "true";
        }

        /* if just one layer in group is on the group is on */
        $status = 'false';
        foreach($aLayersIdx As $idx) {
            $oLayer= $oMap->getLayer($idx);
            if($status == 'false') {
                $status = ($oLayer->status != MS_OFF) ? 'true' : 'false';
            }
        }
        $groupScaleVis = array();
        $i=0;
        foreach($aszMapFile['scales'] as $szScale) {
            $oMap->set("scale", $szScale);
            $groupScaleVis[$i] = 0;
            foreach($aLayersIdx As $idx) {
                $oLayer = $oMap->getLayer($idx);
                $oLayer->set("status", MS_ON);
                if ($oLayer->isVisible()) {
                    $groupScaleVis[$i] = $oLayer->isVisible();
                    continue;
                }
            }
            $i++;
        }

        $szLayers .= "map.addLayer(new _layer( { ".
                     "name:'".$groupName."',".
                     "visible:".$status.",".
                     "opacity:".$opacity.",".
                     "imageformat:'".$imageformat."',".
                     "queryable:".$szQueryable.",".
                     "tileSource:'".$tileSource."',".
                     "redrawInterval:".$redrawInterval.",".
                     "refreshInterval:".$refreshInterval.",".
                     "scales: new Array('".implode("','",$groupScaleVis)."')}));";
    }
    $units = $oMap->units;
    $szResult .= "var map = new _map({".
                      "name:'".$key."',".
                      "title:'".$aszMapFile['title']."',".
                      "currentScale: 0,".
                      "units:".$units.",".
                      "resolution:".$oMap->resolution.",".
                      "version:'".$szMapVersion."',".
                      "scales:aszScales});";
    $szExtents = $oMap->extent->minx.",".$oMap->extent->miny.",".
    $oMap->extent->maxx.",".$oMap->extent->maxy;
    $szResult .= "map.setDefaultExtents(".$szExtents.");";
    if ($oMap->getMetaData( "max_extents") != '') {
        $szMaxExtents = $oMap->getMetaData("max_extents");
        if (strcasecmp($szMaxExtents, 'auto') == 0) {
            $szMaxExtents = $szExtents;
        } else {
            $aszMaxExtents = preg_split('/[\s,]+/', $szMaxExtents);
            $minx = min($aszMaxExtents[0], $aszMaxExtents[2]);
            $miny = min($aszMaxExtents[1], $aszMaxExtents[3]);
            $maxx = max($aszMaxExtents[0], $aszMaxExtents[2]);
            $maxy = max($aszMaxExtents[1], $aszMaxExtents[3]);
            $szMaxExtents = $minx.",".$miny.",".$maxx.",".$maxy;
        }
        $szResult .= "map.setMaxExtents(".$szMaxExtents.");";
    }
    $szResult .= "map.setBackgroundColor('rgb(".$oMap->imagecolor->red.",".$oMap->imagecolor->green.",".$oMap->imagecolor->blue.")');";
    $szResult .= $szLayers;
    if (isset($_GET['extents']) && $szMap == $key) {
        $szResult .= "map.setCurrentExtents(".$_GET['extents'].");";
    }
    if (isset($_GET['centerPoint']) && $szMap == $key) {
        $szResult .= "map.aZoomTo=new Array(".$_GET['centerPoint'].");";
    }
    $szResult .= "map.resolution = ".$oMap->resolution.";";
    $szResult .= "this.addMap( map );";
}
if(isset($szBaseWebCache)) {
    $szResult .= "this.webCache = '" . $szBaseWebCache . "';";
    $szResult .= "this.metaWidth = " . $metaWidth . ";";
    $szResult .= "this.metaHeight = " . $metaHeight . ";";
}
$szResult .= "this.tileWidth=$tileWidth;";
$szResult .= "this.tileHeight=$tileHeight;";
//default values for scripts that work with this backend:
$szURL = 'http';
if (isset($_SERVER['HTTPS'])&& strcasecmp($_SERVER['HTTPS'], 'off') != 0 ) {
    $szURL .= "s";
}
$szURL .= "://";
if (isset($_SERVER['HTTP_X_FORWARDED_HOST'])) {
    $szURL .= $_SERVER['HTTP_X_FORWARDED_HOST'];
} else {
    $szURL .= $_SERVER['HTTP_HOST'];
    if(preg_match('/:\d+$/', $szURL) == 0) {
        // check to make sure port is not already in SERVER_HOST variable
        if (isset($_SERVER['SERVER_PORT']) && $_SERVER['SERVER_PORT'] != '80')
            $szURL .= ":".$_SERVER['SERVER_PORT'];
    }
}

if( isset( $_SERVER['REQUEST_URI'] ) ) {
    if ((substr($szURL, -1, 1) != '/') &&
        (substr($_SERVER['REQUEST_URI'],0,1) != '/')) {
        $szURL .= "/";
    }
    $szURL .= dirname($_SERVER['REQUEST_URI'])."/";
} else {
    if ((substr($szURL, -1, 1) != '/') &&
        (substr($_SERVER['PHP_SELF'],0,1) != '/')) {
        $szURL .= "/";
    }
    $szURL .= dirname($_SERVER['PHP_SELF'])."/";
}

$szResult .= "this.server = '".$szURL."';";
$szResult .= "this.tileURL = 'tile.php';";

$szResult .= "this.selectMap('$szMap');";
echo $szResult;
?>
