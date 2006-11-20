<?php
/**********************************************************************
 *
 * $Id: print_map.php,v 1.8 2006/09/01 12:31:13 lbecchi Exp $
 *
 * purpose: printing system (bug 1498)
 *
 * author: Lorenzo Becchi and Andrea Cappugi
 *	- based on FPDF lib by Olivier PLATHEY version 1.53 
 *	- idea took from Armin Burger pdfprint in p.mapper (pmapper.sourceforce.org)
 *	- layer trasparence control added by Donal Regan
 *
 * TODO:
 * - integrate query results in the PDF page.
 *
 **********************************************************************
 *
 * Copyright (c)  2006, ominiverdi.org
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
 
session_start();
$sessionId=session_id(); 



//ERROR HANDLING
if(isset($_REQUEST['debug'])) error_reporting ( E_ALL );
else error_reporting( E_ERROR );


//MAPSCRIPT INIT
include_once( '../../../include/config.php' );

if (!extension_loaded('MapScript'))
{
    dl( $szPHPMapScriptModule );
}

    
//PARSE URL
if (isset($_REQUEST['scale']))
{
    $scale= $_REQUEST['scale'];
}
 
if (isset($_REQUEST['map']))
{
    $map= $_REQUEST['map'];
} else 
{
    echo "map not defined";
   die;
}

if (isset($_REQUEST['img_width']))
{
    $max_width = 1000; //pixel
    $pw=($_REQUEST['img_width']<$max_width)?$_REQUEST['img_width']:$max_width;
} else 
{
    echo "img_width not defined";
   die;
}


if (isset($_REQUEST['groups']))$groups=$_REQUEST['groups'];
else $groups="";
$aGroup=explode(',',$groups);

if (isset($_REQUEST['opacitys']))$opacitys=$_REQUEST['opacitys'];
else $opacitys="";
$aOpacity=explode(',',$opacitys);

if (isset($_REQUEST['extent']))$extent=$_REQUEST['extent'];
else $extent="";
$aExtent=explode('|',$extent);




if(isset($_REQUEST['output_type'])){

	switch ($_REQUEST['output_type']) {
		case 'JPEG':
			setOutputFormat("JPEG");	
			break;
		case 'PNG':
			setOutputFormat("PNG");	
			break;
		case 'GIF':
			setOutputFormat("GIF");	
			break;
		case 'PDF':
			require('fpdf.php');
			require('kaPDF.php');
			
			setOutputFormat("JPEG");//alpha channel not support by PFDF	
			$pdf=true;
			break;
		case 'GeoTIFF':
			setOutputFormat("JPEG");//alpha channel not support by PFDF	
			$geoTIFF=true;
			break;
			
		default:
			setOutputFormat("PNG");
	}
	
	
} else {
//SHOW MENU	
	$request = "map=$_REQUEST[map]&groups=$_REQUEST[groups]&opacitys=$_REQUEST[opacitys]&extent=$_REQUEST[extent]&img_width=$_REQUEST[img_width]&scale=$_REQUEST[scale]";
	?>	
		<html>
		<head>
		<meta http-equiv="Content-Language" content="en" />
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
		<title>ka-Map print system</title>
		<style type="text/css">
			body {background-color:rgb(50,50,50);color:white;}
			h1 {font-size:1.5em;border-bottom:1px solid white;}
			a {color:rgb(240,170,0);}
		</style>
		</head>
		<body>
		<h1>choose an output type:</h1>	
		<p>left click to view or right button "save link as..." to download:</p>	  	
		  	<a href="print_map.php?<?php echo $request; ?>&output_type=JPEG">JPEG</a> <br>
  			<a href="print_map.php?<?php echo $request; ?>&output_type=PNG">PNG</a> <br>
  			<a href="print_map.php?<?php echo $request; ?>&output_type=GIF">GIF</a> <br>
  			<a href="print_map.php?<?php echo $request; ?>&output_type=PDF">PDF</a> <br>
  			<a href="print_map.php?<?php echo $request; ?>&output_type=GeoTIFF">GeoTIFF</a><br>	
		</body>
		</html>	
	<?php
	die;
}



//TEMP DIR
$szCacheDir = $szMapCacheDir."/print/";
if (!@is_dir($szCacheDir))
    makeDirs($szCacheDir);
    

//INIT MAP OBJ
$oMap = ms_newMapObj($szMapFile);

//SETTING MAP EXTENT. 
$mapExtent = $oMap->extent;
if ((abs($mapExtent->maxx - $mapExtent->minx) - abs($aExtent[2]-$aExtent[0]))>0){
    $oMap->setExtent($aExtent[0],$aExtent[1],$aExtent[2],$aExtent[3]);
 
}

//SELECTING LAYERS
$tot = $oMap->numlayers;
for($i=0;$i<$tot;$i++){
	$oLayer= $oMap->getLayer($i);
        //CHECKING GROUPS FOR VISIBILITY
	if($oLayer->type != MS_LAYER_RASTER ){
                //echo($oLayer->group);
                //if BASE group
                if($oLayer->group=="")$oLayer->set('status',MS_ON);
                //if on visible group
		elseif (in_array($oLayer->group,$aGroup)){
		        $oLayer->set('status',MS_ON);
				$opacity = $aOpacity[array_search($oLayer->group,$aGroup)];
				if($opacity!='')$oLayer->set('transparency',$opacity);
		        if(!$oLayer->isVisible() && ($oLayer->minscale < $scale && $oLayer->maxscale > $scale )){
		        $oLayer->set("minscale",0);
		        $oLayer->set("maxscale",(200000000)); // has to be greater that map maximum scale
		        }
		}else{
		$oLayer->set('status',MS_OFF);
		if(!$oLayer->isVisible() && ($oLayer->minscale < $scale && $oLayer->maxscale > $scale )){
		        $oLayer->set("minscale",0);
		        $oLayer->set("maxscale",(200000000)); // has to be greater that map maximum scale
		        }
		continue;
		}    
	}
}




//OUTPUT
        
   //PREPARING THE IMAGES     
       
        
        

// OUTPUTTING
if(isset($pdf)){
 		
 		$oMap->selectOutputFormat( $szMapImageFormat );
        
        //MAP IMAGE
        //set image widht and height       
        $gw =$aExtent[2] - $aExtent[0];
        $gh = $aExtent[3] - $aExtent[1];    
        $ph = ceil($pw*$gh/$gw);
        $oMap->set('width', $pw);
        $oMap->set('height', $ph);
        $oMap->resolution = 96;//pare che non funga
        $oImg=$oMap->draw();
        $szImg = $szCacheDir. $sessionId;
        $oImg->saveImage($szImg,$oMap);
        $oImg->free();
	
	
	//SET MAP IMAGE
	copy($szImg, $szImg.'.jpg');	
	$imgH = ceil(200*$gh/$gw);
	
	//LEGEND IMAGE
		$oImg=$oMap->drawLegend();
		//$oImg->createLegendIcon(200, 100);
	   	$oImg->saveImage($szImg.'_legend',$oMap);
	   	copy($szImg.'_legend', $szImg.'_legend.jpg');
	   	$legendW = $oImg->width;
	   	$legendH = $oImg->height;
		$oImg->free();
	
	//SCALEBAR IMAGE
		$oImg=$oMap->drawScaleBar();
		//$oImg->createLegendIcon(200, 100);
	   	$oImg->saveImage($szImg.'_scalebar',$oMap);
	   	copy($szImg.'_scalebar', $szImg.'_scalebar.jpg');
	   	$scalebarW = $oImg->width;
	   	$scalebarH = $oImg->height;
		$oImg->free();

	$pdf=new kaPDF($oMap,'P','mm','A4',210,290);
	$pdf->init($oMap->name, "Arial", 9);
	$pdf->setImage($szImg.'.jpg',$pw,$ph);
	$pdf->setLegend($szImg.'_legend.jpg',$legendW,$legendH);
	$pdf->setScalebar($szImg.'_scalebar.jpg',$scalebarW,$scalebarH);
	$pdf->setMapExtent($aExtent[0],$aExtent[1],$aExtent[2],$aExtent[3]);
	$pdf->setScale($oMap->scale);
    $pdf->drawPage();
	$pdf->Output($oMap->name,'I');
	
} else if (isset($geoTIFF)){
	//MAP IMAGE
        //set image widht and height       
        $gw =$aExtent[2] - $aExtent[0];
        $gh = $aExtent[3] - $aExtent[1];    
        $ph = ceil($pw*$gh/$gw);
        $oMap->set('width', $pw);
        $oMap->set('height', $ph);
        $oMap->resolution = 96;//pare che non funga
        $oMap->selectOutputFormat(GTIFF);
        $oImg=$oMap->draw();
        $szImg = $szCacheDir. $sessionId;
        $oImg->saveImage($szImg,$oMap);
        $oImg->free();
        
	$h = fopen($szImg, "r");
	header("Content-Type: TIFF/GeoTIFF");
	header("Content-Length: " . filesize($szImg));
	header("Expires: " . date( "D, d M Y H:i:s GMT", time() + 31536000 ));
	header("Cache-Control: max-age=31536000, must-revalidate" );
	header("Content-Disposition: attachment; filename=\"".$oMap->name.".tiff\"");
	fpassthru($h);
	fclose($h);
} else {
	
	 $oMap->selectOutputFormat( $szMapImageFormat );
        
        //MAP IMAGE
        //set image widht and height       
        $gw =$aExtent[2] - $aExtent[0];
        $gh = $aExtent[3] - $aExtent[1];    
        $ph = ceil($pw*$gh/$gw);
        $oMap->set('width', $pw);
        $oMap->set('height', $ph);
        $oMap->resolution = 96;//pare che non funga
        $oImg=$oMap->draw();
        $szImg = $szCacheDir. $sessionId;
        $oImg->saveImage($szImg,$oMap);
        $oImg->free();
        
	$h = fopen($szImg, "r");
	header("Content-Type: ".$szImageHeader);
	header("Content-Length: " . filesize($szImg));
	header("Expires: " . date( "D, d M Y H:i:s GMT", time() + 31536000 ));
	header("Cache-Control: max-age=31536000, must-revalidate" );
	header("Content-Disposition: attachment; filename=\"".$oMap->name.".".strtolower($_REQUEST['output_type'])."\"");
	fpassthru($h);
	fclose($h);
}


?>