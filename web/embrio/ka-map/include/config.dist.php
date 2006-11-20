<?php
/**********************************************************************
 *
 * $Id: config.dist.php,v 1.12 2006/07/05 15:17:34 dmorissette Exp $
 *
 * purpose: configuration file for kaMap, hopefully well documented
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * TODO:
 *
 *  - consider moving per-map configuration to metadata in map files
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
 * basic system configuration
 *
 * kaMap! uses PHP/MapScript and the PHP GD extension to
 * render tiles, and uses PHP/MapScript to generate initialization parameters
 * a legend, and a keymap from the selected map file.
 *
 * Make sure to set the correct module names for your PHP extensions.
 *
 * WINDOWS USERS: you will likely need to use php_gd2.dll instead of php_gd.dll
 */
$szPHPMapScriptModule = 'php_mapscript_46.'.PHP_SHLIB_SUFFIX;
$szPHPGDModule = 'php_gd.'.PHP_SHLIB_SUFFIX;

/******************************************************************************
 * tile generation parameters
 *
 * kaMap! generates tiles to load in the client application by first rendering
 * larger areas from the map file and then slicing them up into smaller tiles.
 * This approach reduces the overhead of loading PHP/MapScript and PHP GD and
 * drawing the map file.  These larger areas are referred to as metaTiles in
 * the code.  You can set the size of both the small tiles and the metaTiles
 * here.  A reasonable size for the small tiles seems to be 200 pixels square.
 * Smaller tiles seem to cause problems in client browsers by causing too many
 * images to be created and thus slowing performance of live dragging.  Larger
 * tiles take longer to download to the client and are inefficient.
 *
 * The number of smaller tiles that form a metaTile can also be configured.
 * This parameter allows tuning of the tile generator to ensure optimal
 * performance and for label placement.  MapServer will produce labels only
 * within a rendered area.  If the area is too small then features may be
 * labelled multiple times.  If the area is too large, it may exceed MapServer,s
 * maximum map size (by default 2000x2000) or be too resource-intensive on the
 * server, ultimately reducing performance.
 */
$tileWidth = 256;
$tileHeight =256;
$metaWidth = 6;
$metaHeight = 6;
/* $metaBuffer = Buffer size in pixels to add around metatiles to avoid
 * rendering issues along the edge of the map image
 */
$metaBuffer = 40;

/******************************************************************************
 * in-image debugging information - tile location, outlines etc.
 * to use this, you need to remove images from your cache first.  This also
 * affects the meta tiles - if debug is on, they are not deleted.
 */
$bDebug = false;

/******************************************************************************
 * aszMapFiles - an array of map files available to the application.  How this
 * is used is determined by the application.  Each map file is entered into
 * this array as a key->value pair.
 *
 * The key is the name to be used by the tile caching system to store cached
 * tiles within the base cache directory.  This key should be a single word
 * that uniquely identifies the map.
 *
 * The value associated with each key is an array of three values.  The first
 * value is a human-readable name to be presented to the user (should the
 * application choose to do so) and the second value is the path to the map
 * file.  It is assumed that the map file is fully configured for use with
 * MapServer/MapScript as no error checking or setting of values is done.  The
 * third value is an array of scale values for zooming.
 */

 $aszGMap = array (
         'title' => 'GMap 75',
         'path' => '../../gmap/htdocs/gmap75.map',
         'scales' => array( 40000000, 25000000, 12000000, 7500000, 3000000, 1000000 ),
         'format' =>'PNG'
         /* Sample authorized_users entry. See auth.php for more details:
          * ,'authorized_users' => array('popplace' => array('user1', 'user2'),
          *                              'park'     => array('user1')
          */
 );


 $aszMapFiles = array( 'gmap' => $aszGMap

/* Add more elements to this array to offer multiple mapfiles */

);

/******************************************************************************
 * figure out which map file to use and set up the necessary variables for
 * the rest of the code to use.  This does need to be done on every page load
 * unfortunately.
 *
 * szMap should be set to the default map file to use but can change if
 * this script is called with map=<mapname>.
 */
$szMap = 'gmap';

/******************************************************************************
 * kaMap! caching
 *
 * this is the directory within which kaMap! will create its tile cache.  The
 * directory does NOT have to be web-accessible, but it must be writable by the
 * web-server-user and allow creation of both directories AND files.
 *
 * the tile caching system will create a separate subdirectory within the base
 * cache directory for each map file.  Within the cache directory for each map
 * file, directories will be created for each group of layers.  Within the group
 * directories, directories will be created at each of the configured scales
 * for the application (see mapfile configuration above.)
 */
$szBaseCacheDir =  "/tmp/kacache/";

/* Uncomment the following if you have a web accessible cache */
//$szBaseWebCache = "kacache/";

/******************************************************************************
 * Authentication and access control:
 *
 * Uncomment the following lines to load auth.php and enable access control.
 * See docs at the top of auth.php for more details.
 */
//include_once('auth.php');
//$oAuth = new kaBasicAuthentication(&$aszMapFiles[$szMap]['authorized_users']);


/*****  END OF CONFIGURABLE STUFF - unless you know what you are doing   *****/

if (isset($_REQUEST['map']) && isset($aszMapFiles[$_REQUEST['map']]))
{
    $szMap = $_REQUEST['map'];
}

$szMapCacheDir = $szBaseCacheDir.$szMap;
$szMapName = $aszMapFiles[$szMap]['title'];
$szMapFile = $aszMapFiles[$szMap]['path'];
$anScales = $aszMapFiles[$szMap]['scales'];
setOutputFormat($aszMapFiles[$szMap]['format']);
/******************************************************************************
 * output format of the map and resulting tiles
 *
 * The output format used with MapServer can greatly affect appearance and
 * performance.  It is recommended to use an 8 bit format such as PNG
 *
 * NOTE: the tile caching code in tile.php is not configurable here.  It
 * currently assumes that it is outputting 8bit PNG files.  If you change to
 * PNG24 here then you will need to update tile.php to use the gd function
 * imagecreatetruecolor.  If you change the output format to jpeg then
 * you would need to change imagepng() to imagejpeg().  A nice enhancement
 * would be to make that fully configurable from here.
 *
 * DITHERED is a special output format that uses the 24bit png renderer to
 * render the entire map and then quantizes the final image into some number
 * number of colours just before saving, typically 256.
 *
 * To use DITHERED, you need MapServer 4.9 CVS after 2006-03-08, or any later
 * release.  You also need to create an OUTPUTFORMAT block in your
 * map file as follows:
 *
OUTPUTFORMAT
  NAME dithered
  DRIVER "GD/PNG"
  EXTENSION "png"
  MIMETYPE "image/png"
  IMAGEMODE RGBA
  TRANSPARENT OFF
  FORMATOPTION "QUANTIZE_FORCE=ON"
  FORMATOPTION "QUANTIZE_DITHER=OFF"
  FORMATOPTION "QUANTIZE_COLORS=256"
END
 *
 */
function setOutputFormat($szFormat)
{
    switch(strtoupper($szFormat)) {
        case "DITHERED":
            $GLOBALS['szMapImageFormat'] = 'dithered';
            $GLOBALS['szMapImageCreateFunction'] = "imagecreatefrompng";
            $GLOBALS['szImageExtension'] = '.png';
            $GLOBALS['szImageCreateFunction'] = "imagecreate";
            $GLOBALS['szImageOutputFunction'] = "imagepng";
            $GLOBALS['szImageHeader'] = 'image/png';
            break;
        case "PNG24":
            $GLOBALS['szMapImageFormat'] = 'PNG24';
            $GLOBALS['szMapImageCreateFunction'] = "imagecreatefrompng";
            $GLOBALS['szImageExtension'] = '.png';
            $GLOBALS['szImageCreateFunction'] = "imagecreatetruecolor";
            $GLOBALS['szImageOutputFunction'] = "imagepng";
            $GLOBALS['szImageHeader'] = 'image/png';
            break;
        case "ALPHA":
            $GLOBALS['szMapImageFormat'] = 'PNG24';
            $GLOBALS['szMapImageCreateFunction'] = "imagecreatefrompng";
            $GLOBALS['szImageExtension'] = '.png';
            $GLOBALS['szImageCreateFunction'] = "imagecreatetruecolor";
            $GLOBALS['szImageOutputFunction'] = "imagepng";
            $GLOBALS['szImageHeader'] = 'image/png';
            break;
        case "GIF":
            $GLOBALS['szMapImageFormat'] = 'GIF';
            $GLOBALS['szMapImageCreateFunction'] = "imagecreatefromgif";
            $GLOBALS['szImageExtension'] = '.gif';
            $GLOBALS['szImageCreateFunction'] = "imagecreate";
            $GLOBALS['szImageOutputFunction'] = "imagegif";
            $GLOBALS['szImageHeader'] = 'image/gif';
            break;
        case "JPEG":
            $GLOBALS['szMapImageFormat'] = 'JPEG';
            $GLOBALS['szMapImageCreateFunction'] = "imagecreatefromjpeg";
            $GLOBALS['szImageExtension'] = '.jpg';
            $GLOBALS['szImageCreateFunction'] = "imagecreatetruecolor";
            $GLOBALS['szImageOutputFunction'] = "imagejpeg";
            $GLOBALS['szImageHeader'] = 'image/jpeg';
            break;
        case "PNG":
            $GLOBALS['szMapImageFormat'] = 'PNG';
            $GLOBALS['szMapImageCreateFunction'] = "imagecreatefrompng";
            $GLOBALS['szImageExtension'] = '.png';
            $GLOBALS['szImageCreateFunction'] = "imagecreate";
            $GLOBALS['szImageOutputFunction'] = "imagepng";
            $GLOBALS['szImageHeader'] = 'image/png';
            break;
    }
}

/**
 * create all directories in a directory tree - found on the php web site
 * under the mkdir function ...
 */
function makeDirs($strPath, $mode = 0777)
{
   return is_dir($strPath) or ( makeDirs(dirname($strPath), $mode) and mkdir($strPath, $mode) );
}

/**
 * This function replaces all special characters in the given string.
 *
 * @param szString string - The string to convert.
 *
 * @return string converted
 */
function normalizeString($szString)
{
    // Normalize string by replacing all special characters
    // e.g.    "http://my.host.com/cgi-bin/mywms?"
    // becomes "http___my_host_com_cgi_bin_mywms_"
    return preg_replace("/(\W)/", "_", $szString);
}
?>
