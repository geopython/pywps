<?php
/***************************************************
 * Created on 22-gen-2006
 *
 * Piergiorgio Navone 
 *
 * $Id: drawgeom.php,v 1.2 2006/05/31 11:09:33 pspencer Exp $
 ***************************************************
 * 
 * URL Parameters:
 * 
 * it		Image type: "P": PNG, "G": GIF (default "P").
 * cl		Coordinates list "X1,Y1,X2,Y2,...".
 * sc		Scale factor: coordinates will be divided by this factor (default 1).
 * bp		Image border in pixels (default 0).
 * gt		Gometry type: "L": Linestring, "P": Polygon (default "L") 
 * st		Stroke, the brush width in pixels
 * lc		Line color in ARGB or RGB
 * fc		Fill color (for polygons) in ARGB or RGB
 * op		Opacity: from 0 (transparent) to 100 (solid). If present overvrite the alpha channel in colors. 
 */

include_once('../../include/config.php');
 
if (!extension_loaded('gd'))
{
    dl($szPHPGDModule);
}

//
//
//
function parseColor($c) {
	$r = array("A" => 255, "R" => 0, "G" => 0, "B" => 0);
	trim($c);
	
	if (strlen($c)<6) 
		trigger_error("Color parsing error: ($c)", E_USER_ERROR);
	
	if ($c{0} == "#") $c = substr($c,1);
	
	if (strlen($c)>6) {
		$r["A"] = intval(substr($c,0,2), 16);
		$c = substr($c,2);
	}
	
	if (strlen($c)<6) 
		trigger_error("Color parsing error: ($c)", E_USER_ERROR);
	
	$r["R"] = intval(substr($c,0,2), 16);
	$r["G"] = intval(substr($c,2,2), 16);
	$r["B"] = intval(substr($c,4,2), 16);
	
	//trigger_error("Color parsing: ($c) -> ".$r["A"]." ".$r["R"]." ".$r["G"]." ".$r["B"], E_USER_ERROR);
	return $r; 
}

//
//
//
$imageType = isset( $_REQUEST['it'] ) ? $_REQUEST['it'] : "P";
$coords = isset( $_REQUEST['cl'] ) ? $_REQUEST['cl'] : null;
$scale  = isset( $_REQUEST['sc'] ) ? $_REQUEST['sc'] : 1;
$border  = isset( $_REQUEST['bp'] ) ? ceil($_REQUEST['bp']) : 0;
$type  = isset( $_REQUEST['gt'] ) ? $_REQUEST['gt'] : "L";
$stroke  = isset( $_REQUEST['st'] ) ? ceil($_REQUEST['st']) : 1;
$lcolor  = isset( $_REQUEST['lc'] ) ? parseColor($_REQUEST['lc']) : null;
$fcolor  = isset( $_REQUEST['fc'] ) ? parseColor($_REQUEST['fc']) : null;
$opacity = isset( $_REQUEST['op'] ) ? ceil($_REQUEST['op']) : -1;

if ($lcolor == null and $type == "L") $lcolor = parseColor("#000000");
if ($lcolor == null and $fcolor == null and $type == "P") $lcolor = parseColor("#000000");
if ($opacity>0 and $opacity<=100) {
	$a = round($opacity*2.55);
	if ($lcolor != null) $lcolor["A"] = $a;
	if ($fcolor != null) $fcolor["A"] = $a;
}

//trigger_error("Colors : ".$fcolor["A"]." ".$fcolor["R"]." ".$fcolor["G"]." ".$fcolor["B"], E_USER_ERROR);


//
//
//
$ca = explode(",",$coords);
$cc = count ($ca);
$cxy = array();
$width = 1;
$height = 1;
for($i = 0; $i < $cc; $i+=2) {
	$x = round ( $ca[$i] / $scale ); 
	if ($width < $x) $width = $x;
	$y = round ( $ca[$i+1] / $scale );
	if ($height < $y) $height = $y;
	array_push($cxy, $x+$border, $y+$border);
}

$width += $border * 2; 
$height += $border * 2; 

//
//
//
$oImg = imagecreate( $width, $height );

$it = imagecolorallocate($oImg, 1, 1, 1);
imagecolortransparent ( $oImg, $it );

//imageantialias ( $oImg, true );

if ($lcolor != null) {
	$brush = imagecreate( $stroke, $stroke );
	$bt = imagecolorallocate($brush,1,1,1);
	imagecolortransparent ( $brush, $bt );
	if ($lcolor["A"] < 255) $lineColor = imagecolorallocatealpha( $brush, $lcolor["R"], $lcolor["G"], $lcolor["B"], 127 - $lcolor["A"]/2 );
	else $lineColor = imagecolorallocate( $brush, $lcolor["R"], $lcolor["G"], $lcolor["B"] );
	if ($stroke > 3) 
		imagefilledellipse($brush, round($stroke/2), round($stroke/2), $stroke, $stroke, $lineColor);
	else 
		imagefilledrectangle($brush, 0, 0, $stroke, $stroke, $lineColor);
	
	imagesetbrush ( $oImg, $brush );
}

if ($fcolor != null) {
	//$fillColor = imagecolorallocate( $oImg, $fcolor["R"], $fcolor["G"], $fcolor["B"] );
	$fillColor = imagecolorallocatealpha( $oImg, $fcolor["R"], $fcolor["G"], $fcolor["B"], 127 - $fcolor["A"]/2 );
}

//
//
//
if ($type == "L") {
	
	$cc = count ($cxy);
	for($i = 0; $i < $cc-3; $i+=2) {
		imageline ( $oImg, $cxy[$i], $cxy[$i+1], $cxy[$i+2], $cxy[$i+3], IMG_COLOR_BRUSHED);
	}
	
} else if ($type == "P") {
	
	$cc = count ($cxy);
	if ($fcolor != null) {
		imagefilledpolygon ( $oImg, $cxy, $cc/2, $fillColor);
	}	
	if ($lcolor != null) {
		imagepolygon ( $oImg, $cxy, $cc/2, IMG_COLOR_BRUSHED);
	}
}

//
//
//

//    Output handler
function output_handler($img) {
   header('Content-Length: ' . strlen($img));
   return $img;
}
ob_start("output_handler");

header("Cache-Control: no-store, no-cache, must-revalidate");
if ($imageType == "P") {
	header("Content-type: image/png");
	imagepng($oImg);
} else if ($imageType == "G") {
	header("Content-type: image/gif");
	imagegif($oImg);
}

ob_end_flush();
?>