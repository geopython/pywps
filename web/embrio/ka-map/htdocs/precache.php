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
 * Run from the command line with "php precache.php" to see usage.
 *
 *****************************************************************************/

if(!isset($argv)) {
    exit('This is a command line utility');
}

$usage = <<<END_USAGE

Usage:
    php $argv[0] [<-options>] <tile_url>

    Where <tile_url> is the URL to your tile.php script
    (e.g. http://localhost/ka-map/htdocs/tile.php)

    Options:
        -f          Force tile.php to overwrite existing cached images
        -m <map>    Limit cache creation to a single map
        -s <scale>  Limit cache creation to a single scale

END_USAGE;

include('../include/config.php');
if(!extension_loaded('MapScript')) {
    dl($szPHPMapScriptModule);
}
if($argc < 2) {
    exit($usage);
}

// parse arguments
array_shift($argv);
$tileURL = array_pop($argv);
if(preg_match('/^https?:\/\//i', $tileURL) != 1) {
    exit("Invalid <tile_url> : $tileURL\n" . $usage);
}
$argString = ' '.implode(' ',$argv).' ';
// check for -f force option
$forceOpt = (preg_match('/\s-f\s/', $argString) == 1) ? '&force=true' : '';
// check for -m map option
if(preg_match('/\s-m\s+(\w+)\s/', $argString, $matches) == 1) {
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

$allErrors = array();
$inchesPerUnit = array(1, 12, 63360.0, 39.3701, 39370.1, 4374754);
foreach($aszMapFiles as $mapKey => $mapParams) {
    $mapScales = $mapParams['scales'];
    $oMap = ms_newMapObj($mapParams['path']);
    // group all ungrouped layers in a group named __base__
    for($layerIndex = 0; $layerIndex < $oMap->numlayers; ++$layerIndex) {
        $oLayer = $oMap->getLayer($layerIndex);
        if($oLayer->group == '') {
            $oLayer->set('group', '__base__');
        }
    }
    $aGroups = $oMap->getAllGroupNames();

    $mapWidth = $metaWidth * $tileWidth;
    $mapHeight = $metaHeight * $tileHeight;

    $oMap->setSize($mapWidth, $metaHeight * $tileHeight);

    // modify map extent for max_extent metadata
    if ($oMap->getMetaData('max_extents') != '') {
        $szMaxExtents = $oMap->getMetaData('max_extents');
            $aszMaxExtents = preg_split('/[\s,]+/', $szMaxExtents);
            if(count($aszMaxExtents) == 4)
            {
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
    foreach($mapScales as $scale) {
        print "  Scale: $scale\n";
        $cellSize = $scale / ($oMap->resolution * $inchesPerUnit[$oMap->units]);

        $pixMinX = $dMinX / $cellSize;
        $pixMaxX = $dMaxX / $cellSize;
        $pixMinY = $dMinY / $cellSize;
        $pixMaxY = $dMaxY / $cellSize;

        $metaMinX = floor($pixMinX / $mapWidth) * $mapWidth;
        $metaMaxX = ceil($pixMaxX / $mapWidth) * $mapWidth;
        $metaMinY = -1 * ceil($pixMaxY / $mapHeight) * $mapHeight;
        $metaMaxY = -1 * floor($pixMinY / $mapHeight) * $mapHeight;

        $nWide = ($metaMaxX - $metaMinX) / $mapWidth;
        $nHigh = ($metaMaxY - $metaMinY) / $mapHeight;
        print "    Meta tiles: $nWide x $nHigh = " . ($nWide * $nHigh) . "\n";
        print "    Tiles: $nWide x $nHigh x $metaWidth x $metaHeight = " . ($nWide * $nHigh * $metaWidth * $metaHeight) . "\n";
        $nTotalTiles += ($nWide * $nHigh * $metaWidth * $metaHeight);

        $oMap->set("scale", $scale);
        foreach($aGroups as $groupName) {
            // determine if at least one layer in group is visible (due to scale)
            $groupIsVisible = false;
            $aLayersIdx = $oMap->getLayersIndexByGroup($groupName);
            foreach($aLayersIdx as $layerIndex) {
                $oLayer = $oMap->getLayer($layerIndex);
                $oLayer->set("status", MS_ON);
                if($oLayer->isVisible()) {
                    $groupIsVisible = true;
                    break;
                }
            }
            // for groups with visible layer(s), render tiles
            if($groupIsVisible) {
                print "    Group: $groupName\n";
                for($vertInded=0; $vertInded <$nHigh; $vertInded++) {
                    for($horizIndex=0; $horizIndex < $nWide; $horizIndex++) {
                        $theURL = $tileURL . "?s=$scale&t=" . ($metaMinY + ($vertInded * $mapHeight)) . "&l=" . ($metaMinX + ($horizIndex * $mapWidth)) . "&map=$mapKey&g=" . urlencode($groupName) . $forceOpt;
                        if(!@file_get_contents($theURL)) {
                            array_push($allErrors, "Failed to open stream: $theURL\n");
                        }
                    }
                }
            }
            flush();
        }
    }
}
if(count($allErrors) > 0) {
    $aPlural = (count($allErrors)==1) ? '' : 's';
    print "\nTrouble:\n  " . count($allErrors) . " error$aPlural encountered\n";
    print "  Report [a]ll, [l]ast, or [n]one? ";
    $line = trim(fgets(STDIN));
    if(stristr($line, 'a')) {
        exit("\n" . implode("\n", $allErrors));
    }
    if(stristr($line, 'l')) {
        exit("\n" . $allErrors[count($allErrors) - 1]);
    }
    if(stristr($line, 'n')) {
        exit;
    }
}
?>
