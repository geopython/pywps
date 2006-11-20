<?php
/******************************************************************************
 *
 * Copyright DM Solutions Group Inc 2005.  All rights reserved.
 *
 * kaMap! cache populator
 *
 * this is intended to be run from the command line and is used to
 * pre-generate cached images for a given map file.
 *
 * original author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * resurrected by: Tim Schaub of CommEn Space 2006/02/09
 *
 * This script will generate an image cache for all maps and all scales
 * given in config.php unless limited by the options described below.
 * If a map contains "max_extents" METADATA, tiles will be generated for
 * the specified extent.  Otherwise, tiles are generated for the EXTENT
 * defined in the mapfile.
 *
 * Run from the command line with "php precache2.php -h" to see usage.
 *
 *****************************************************************************/

if(!isset($argv)) {
    exit('This is a command line utility');
}

$usage = <<<END_USAGE

Usage:
    php $argv[0] [<-options>]

    Options:
        -f          Force tile.php to overwrite existing cached images
        -m <map>    Limit cache creation to a single map
        -s <scale>  Limit cache creation to a single scale
        -h          Display this message

END_USAGE;

include_once('../include/config.php');
if(!extension_loaded('MapScript')) {
    dl($szPHPMapScriptModule);
}
if (!extension_loaded('gd')) {
    dl( $szPHPGDModule);
}

// parse arguments
array_shift($argv);
$argString = ' '.implode(' ',$argv).' ';
// check for -f force option
$bForce = (preg_match('/\s-f\s/', $argString) == 1);
// check for -m map option (works for map names with hyphens and word chars
if(preg_match('/\s-m\s+([\w-]+)\s/', $argString, $matches) == 1) {
    if(array_key_exists($matches[1], $aszMapFiles)) {
        $aszMapFiles = array($matches[1] => $aszMapFiles[$matches[1]]);
    } else {
        exit("Can't find map named $matches[1]\n" . $usage);
    }
}
// check for -s scale option
if(preg_match('/\s-s\s+(\d+)\s/', $argString, $matches) == 1) {
    foreach($aszMapFiles as $mapKey => $mapParams) {
        if(in_array($matches[1], $mapParams['scales'])) {
            $aszMapFiles[$mapKey]['scales'] = array($matches[1]);
        } else {
            exit("Can't find scale $matches[1] in map named $mapKey\n" . $usage);
        }
    }
}
// check for -h help option
if(preg_match('/\s-h\s/', $argString) == 1) {
    exit($usage);
}


/* bug 1253 - root permissions required to delete cached files */
$orig_umask = umask(0);

/* create the main cache directory if necessary */
if(!@is_dir($szBaseWebCache))
    makeDirs($szBaseWebCache);

$inchesPerUnit = array(1, 12, 63360.0, 39.3701, 39370.1, 4374754);
foreach($aszMapFiles as $mapKey => $mapParams) {
    $szMapCacheDir = $szBaseCacheDir.$mapParams['title'];
    if (!@is_dir($szMapCacheDir)) {
        makeDirs($szMapCacheDir);
    }
    $oMap = ms_newMapObj($mapParams['path']);
    $nLayers = $oMap->numlayers;
    $mapWidth = $metaWidth * $tileWidth;
    $mapHeight = $metaHeight * $tileHeight;
    $oMap->setSize($mapWidth, $mapHeight);
    // group all ungrouped layers in a group named __base__
    for($layerIndex = 0; $layerIndex < $nLayers; ++$layerIndex) {
        $oLayer = $oMap->getLayer($layerIndex);
        if($oLayer->group == '') {
            $oLayer->set('group', '__base__');
        }
    }
    $aszGroups = $oMap->getAllGroupNames();

    // modify map extent for max_extent metadata
    if($oMap->getMetaData('max_extents') != '') {
        $szMaxExtents = $oMap->getMetaData('max_extents');
        $aszMaxExtents = preg_split('/[\s,]+/', $szMaxExtents);
        if(count($aszMaxExtents) == 4) {
            $minx = min($aszMaxExtents[0], $aszMaxExtents[2]);
            $miny = min($aszMaxExtents[1], $aszMaxExtents[3]);
            $maxx = max($aszMaxExtents[0], $aszMaxExtents[2]);
            $maxy = max($aszMaxExtents[1], $aszMaxExtents[3]);
            $oMap->setExtent($minx, $miny, $maxx, $maxy);
        }
    }

    $dMinX = $oMap->extent->minx;
    $dMaxX = $oMap->extent->maxx;
    $dMinY = $oMap->extent->miny;
    $dMaxY = $oMap->extent->maxy;

    $nTotalTiles = 0;
    print "\nMap: $mapKey\n";
    $mapScales = $mapParams['scales'];
    foreach($mapScales as $scale) {
        print "  Scale: $scale\n";
        $cellSize = $scale / ($oMap->resolution * $inchesPerUnit[$oMap->units]);

        $pixMinX = $dMinX / $cellSize;
        $pixMaxX = $dMaxX / $cellSize;
        $pixMinY = $dMinY / $cellSize;
        $pixMaxY = $dMaxY / $cellSize;

        // create a 1 tile buffer and round to nearest metatile
        $metaMinX = floor(($pixMinX - $tileWidth) / $mapWidth) * $mapWidth;
        $metaMaxX = ceil(($pixMaxX + $tileWidth) / $mapWidth) * $mapWidth;
        $metaMinY = -1 * ceil(($pixMaxY + $tileHeight) / $mapHeight) * $mapHeight;
        $metaMaxY = -1 * floor(($pixMinY - $tileHeight) / $mapHeight) * $mapHeight;

        $nWide = ($metaMaxX - $metaMinX) / $mapWidth;
        $nHigh = ($metaMaxY - $metaMinY) / $mapHeight;
        print "    Meta tiles: $nWide x $nHigh = " . ($nWide * $nHigh) . "\n";
        print "    Tiles: $nWide x $nHigh x $metaWidth x $metaHeight = " . ($nWide * $nHigh * $metaWidth * $metaHeight) . "\n";
        $nTotalTiles += ($nWide * $nHigh * $metaWidth * $metaHeight);

        $oMap->set("scale", $scale);
        $geoWidth = $scale/($oMap->resolution*$inchesPerUnit[$oMap->units]);
        $geoHeight = $scale/($oMap->resolution*$inchesPerUnit[$oMap->units]);

        foreach($aszGroups as $groupName) {
            // determine if at least one layer in group is visible (due to scale)
            $renderGroup = false;
            // turn on/off layers depending on group
            for($layerIndex = 0; $layerIndex < $nLayers; ++$layerIndex) {
                $oLayer = $oMap->getLayer($layerIndex);
                if($groupName == $oLayer->group) {
                    $oLayer->set("status", MS_ON);
                    if($oLayer->isVisible()) {
                        $renderGroup = true;
                    }
                }
                else {
                    $oLayer->set("status", MS_OFF);
                }
            }
            // get image format for the group (first layer)
            $aLayersIdx = $oMap->getLayersIndexByGroup($groupName);
            $oLayer = $oMap->getLayer($aLayersIdx[0]);
            $imageformat = $oLayer->getMetaData('imageformat');
            if($imageformat == '') {
                $imageformat = $oMap->imagetype;
            }
            setOutputFormat($imageformat);
            // check if tile_source is set to nocache
            $tileSource = strtolower($oLayer->getMetaData('tile_source'));
            if($tileSource == 'nocache') {
                $renderGroup = false;
            }
            // for groups with visible layer(s), render tiles
            if($renderGroup) {
                print "    Group: $groupName\n";
                for($vertIndex = 0; $vertIndex < $nHigh; ++$vertIndex) {
                    for($horizIndex = 0; $horizIndex < $nWide; ++$horizIndex) {
                        $top = $metaMinY + ($vertIndex * $mapHeight);
                        $left = $metaMinX + ($horizIndex * $mapWidth);
                        $metaLeft = floor( ($left)/($tileWidth*$metaWidth) ) * $tileWidth * $metaWidth;
                        $metaTop = floor( ($top)/($tileHeight*$metaHeight) ) * $tileHeight *$metaHeight;
                        $szMetaTileId = "t".$metaTop."l".$metaLeft;
                        $metaLeft -= $metaBuffer;
                        $metaTop -= $metaBuffer;
                        $szGroupDir = normalizeString($groupName);
                        $szLayerDir = "def";

                        /* caching is done by scale value, then groups and layers and finally metatile
                         * and tile id. Create a new directory if necessary
                         */
                        $szCacheDir = $szMapCacheDir."/".$scale."/".$szGroupDir."/".$szLayerDir."/".$szMetaTileId;
                        if(!@is_dir($szCacheDir)) {
                            makeDirs($szCacheDir);
                        }
                        // metatile is not rendered unless all tiles exist
                        $renderMetaTile = false;
                        for($i = 0; $i < $metaWidth; ++$i) {
                            for($j = 0; $j < $metaHeight; ++$j) {
                                $tileTop = ($j * $tileHeight) + $metaBuffer;
                                $tileLeft = ($i*$tileWidth) + $metaBuffer;
                                $szTileImg = $szCacheDir . "/t" . ($metaTop + $tileTop) . "l" . ($metaLeft + $tileLeft) . $szImageExtension;
                                if(!file_exists($szTileImg) || $bForce) {
                                    $renderMetaTile = true;
                                    break 2;
                                }
                            }
                        }

                        if($renderMetaTile || $bForce) {
                            $szMetaDir = $szCacheDir."/meta";
                            if(!@is_dir($szMetaDir)) {
                                makeDirs($szMetaDir);
                            }
                            /* Metatile width/height include 2x the metaBuffer value */
                            $oMap->set('width', $tileWidth * $metaWidth + (2 * $metaBuffer));
                            $oMap->set('height', $tileHeight * $metaHeight + (2 * $metaBuffer));

                            /* Tell MapServer to not render labels inside the metaBuffer area
                             * (new in 4.6)
                             * TODO: Until MapServer bugs 1353/1355 are resolved, we need to
                             * pass a negative value for "labelcache_map_edge_buffer"
                             */
                            $oMap->setMetadata("labelcache_map_edge_buffer", -$metaBuffer);

                            /* draw the metatile */
                            $minx = $metaLeft * $geoWidth;
                            $maxx = $minx + ($geoWidth * $oMap->width);
                            $maxy = -1 * $metaTop * $geoHeight;
                            $miny = $maxy - ($geoHeight * $oMap->height);
                            $oMap->setExtent($minx,$miny,$maxx,$maxy);
                            $oMap->selectOutputFormat($szMapImageFormat);
                            $oMap->outputformat->set("transparent", MS_ON);
                            $szMetaImg = $szMetaDir."/t".$metaTop."l".$metaLeft.$szImageExtension;
                            $oImg = $oMap->draw();
                            $oImg->saveImage($szMetaImg);
                            $oImg->free();
                            eval("\$oGDImg = ".$szMapImageCreateFunction."('".$szMetaImg."');");
                            // draw individual tiles
                            for($i = 0; $i < $metaWidth; ++$i) {
                                for($j = 0; $j < $metaHeight; ++$j) {
                                    $tileTop = ($j * $tileHeight) + $metaBuffer;
                                    $tileLeft = ($i * $tileWidth) + $metaBuffer;
                                    $szTileImg = $szCacheDir . "/t" . ($metaTop + $tileTop) . "l" . ($metaLeft + $tileLeft) . $szImageExtension;
                                    if(!file_exists($szTileImg)) {
                                        eval("\$oTile = ".$szImageCreateFunction."( ".$tileWidth.",".$tileHeight." );");
                                        // Allocate BG color for the tile (in case the metatile has transparent BG)
                                        $nTransparent = imagecolorallocate($oTile, $oMap->imagecolor->red, $oMap->imagecolor->green, $oMap->imagecolor->blue);
                                        imagecolortransparent($oTile, $nTransparent);
                                        imagecopy($oTile, $oGDImg, 0, 0, $tileLeft, $tileTop, $tileWidth, $tileHeight);
                                        eval("$szImageOutputFunction( \$oTile, '".$szTileImg."' );");
                                        imagedestroy($oTile);
                                        $oTile = null;
                                    }
                                }
                            }
                            if($oGDImg != null) {
                                imagedestroy($oGDImg);
                                $oGDImg = null;
                            }
                            unlink($szMetaImg);
                        }
                    }
                }
            }
            flush();
        }
    }
}
umask($orig_umask);
?>
