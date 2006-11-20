<?php
/* overlay system
 
 relative bug: 1317

 */
session_start();
include_once( '../../include/config.php' );
$dir=$szMapCacheDir;
if (!extension_loaded('MapScript'))
{
    dl( $szPHPMapScriptModule );
}

//URL Parsing
if (isset($_GET['xmlUrl']))  $xmlUrl=trim($_GET['xmlUrl']);
else {
  echo "Define xmlUrl=URL please";
  die;
}
if (isset($_GET['mapName']))  $mapName=trim($_GET['mapName']);
else {
  echo "Define mapName please";
  die;
}

if (isset($_GET['sessionId']) && ($_GET['sessionId'])){
  $sessionId=trim($_GET['sessionId']);
  session_id($sessionId);
}
else  $sessionId=session_id();


if(isset($_REQUEST['imgWidth'])) $imgWidth = $_REQUEST['imgWidth'];
else $imgWidth = 300;

if(isset($_REQUEST['imgHeight'])) $imgHeight = $_REQUEST['imgHeight'];
else $imgHeight = 300;

$kml = new KMLParser($xmlUrl);


$placemarks=$kml->getPlacemarks();
$groupName=$kml->getPlacemarkName($placemarks->item(0));

//rewrite session Map
if(!file_exists($dir.$sessionId.".map") )
{
//      echo("build map file");

      $oMap = ms_newMapObj(null);
      $aszMapFile=$aszMapFiles[$mapName];

      $oMapO = ms_newMapObj($aszMapFile[1]);
      $ext=$oMapO->extent;
      $oMap->setExtent($ext->minx,$ext->miny,$ext->maxx,$ext->maxy);
     //setto extent mappa e size
//      $oMap->setExtent(-100.0,-100.0,100.0,100.0);
     $oMap->setsize( $imgWidth,$imgHeight);
     $oMap->set("units",$oMapO->units);
     $oMap->selectOutputFormat("PNG");
//setta colore sfondo mappa
     $color=$oMap->imagecolor;
     $color->setRGB(255,255,255);
//setta trasparenza mappa
     $oMap->outputformat->set("transparent", MS_ON );
     //creo layer nome ? gruppo da placemark 
     $layerObj= ms_newLayerObj($oMap);
     //setta caratteristiche base del layer nome gruppo typo
     $layerObj->set("name", $groupName);
     $layerObj->set("group", $groupName);
     //tipo del layer
     $layerObj->set("type", MS_LAYER_POLYGON);
     $layerObj->set("status", MS_ON );

    //crea la classe del layer e la setti con style obj!!
    $classObj = ms_newClassObj($layerObj);
    $classObj->set("name","Polygon");
    $styleObj = ms_newStyleObj($classObj);
    $styleObj->color->setRGB(0,255,0);
    $styleObj->outlinecolor->setRGB(0,0,255);


    //prendo polygn dal kml
    $featureClass=$kml->getPolygons($placemarks->item(0));
    kmlPolygons2mapLayer ($featureClass,$layerObj);

      //$oShp->add($oLine);

//       $oImg = $oMap->draw();
//       $oImg->saveImage("/home/rischio/www/prova.jpg");


         $oMap->save($dir.$sessionId.".map");
         $oMap=null;
         $oMap = ms_newMapObj($dir.$sessionId.".map");
    $oMap->setsize( $imgWidth,$imgHeight);
     //$_SESSION['oMap'] = $oMap;
       szResult($oMap,$aszMapFiles,$mapName,$sessionId);
	szImageMap($oMap,$aszMapFiles,$mapName,$sessionId,$dir);
}
else {
      $oMap = ms_newMapObj($dir.$sessionId.".map");
	$oMap->setsize( $imgWidth,$imgHeight);
      szResult($oMap,$aszMapFiles,$mapName,$sessionId);
	szImageMap($oMap,$aszMapFiles,$mapName,$sessionId,$dir);
}


/*
	szImageMap
*/
function szImageMap($oMap,$aszMapFiles,$mapName,$sessionId,$dir){
	$szResult = "";
/* *******************
*       SVG per image map
********************* */

  // Provo a produrre l'SVG per la mappa html
//      $oMap->setSize($imgWidth,$imgHeight);
        $oMap->selectOutputFormat("SVG");
        $svg =  $oMap->draw();
        $szResult .= "/*svg init |  $oMap->width,$oMap->height*/";
//      $szResult .=  $svg->saveImage('');//da errore di temp file non accessibile (lascia un file vuoto e protetto da scrittura)
        $tempSVG = $dir.$sessionId.'.svg';//va messo con il nome della sessionId
        $svg->saveImage($tempSVG);


        if (! $dom = DOMDocument::load($tempSVG))// DOM version
 //       if (!$dom = domxml_open_file($tempSVG))//DomXML version
        {
                die ("Error while parsing the document\n");
        }

        $paths = $dom->getElementsByTagname('path');// DOM version
        //$paths = $dom->get_elements_by_tagname('path');//DomXML version
        $imageMap="\n\n<map name=\"overlayMap\">";
        $i=0;
	foreach($paths as $path){
                $coords = $path->getAttribute("d");
                $coords = str_replace('M','',$coords);
                $coords = str_replace('L','',$coords);
                $coords = str_replace('z','',$coords);
                $coords = str_replace(' ',',',trim($coords));
                $coords = str_replace(',,',',',trim($coords));
                $imageMap .= "\n<area href=\"#\" shape=\"poly\" coords=\"$coords\" id=\"obj $i\" alt=\"alt value\" title=\"title description for 
obj $i\" onClick=\"myKaOverlay.showInfo(this);\" />";
		$i++;
        }
        $imageMap .= "\n</map>";

        $szResult .= "/*aggiungo SVG*/this.imageMap =unescape('";
        $szResult .= urlencode($imageMap);
        $szResult .= "').replace(/\+/g,  ' ');";


/* *******************
*      Output Finale
********************* */
 echo $szResult;
}




function szResult($oMap,$aszMapFiles,$mapName,$sessionId){

  $szResult = "/*init*/this.sessionId='$sessionId';"; //leave this in so the js code can detect errors
  $aszMapFile=$aszMapFiles[$mapName];
  $aGroups = array();
  $szLayers = '';
  $aGroups=$oMap->getAllGroupNames();
  foreach( $aGroups As $groupName)
  {
    $groupScaleVis=array();
    $status='false';
    $aLayersIdx=$oMap->getLayersIndexByGroup($groupName);
    for($i=0; $i<$oMap->numlayers; $i++)
    {
        $oLayer = $oMap->getLayer($i);
        if ($oLayer->group == '')$aLayersIdx[]=$i;
    }
    sort($aLayersIdx);
    $oLayer= $oMap->getLayer($aLayersIdx[0]);
    $opacity = $oLayer->getMetaData( 'opacity' );
    /* dynamic imageformat */
    $imageformat = $oLayer->getMetaData( 'imageformat' );
    if ($imageformat == '') $imageformat = $oMap->imagetype;
    /* queryable */
    $szQueryable = "false";
    if ($oLayer->getMetaData( "queryable" ) != "")
    {
      if (strcasecmp($oLayer->getMetaData("queryable"), "true") == 0)$szQueryable = "true";
    }
    foreach($aLayersIdx As $idx)
    {
      $oLayer= $oMap->getLayer($idx);
      /*if just one layer in group is on the group is on*/
      if ( $status == 'false') $status = ($oLayer->status!=MS_OFF)?'true':'false';
    }
 
//    determin scale visibility, if one group's layer is visble at scale , group is visible
    $i=0;
    foreach( $aszMapFile[2] As $oScale)
    {
      $oMap->set("scale",$oScale);
      $groupScaleVis[$i]=0;
      foreach($aLayersIdx As $idx)
      {
        $oLayer= $oMap->getLayer($idx);
        $oLayer->set("status",MS_ON);
        if ($oLayer->isVisible())
        {
          $groupScaleVis[$i]=$oLayer->isVisible();
          continue;
        }
      }
      $i++;
    }
if ($opacity == '') $opacity = 100;
  $szLayers .= "this.overlayLayers.push(new _overlayLayer( '".$groupName."', ".$status.", ".$opacity.", '".$imageformat."',".$szQueryable.", new Array('".implode("','",$groupScaleVis)."'), '$sessionId' ));"; //added imageformat parameter}
  }
     $szResult .= $szLayers;


	echo $szResult;
}

function kmlPolygons2mapLayer ($featureClass,$layerObj){
    // Create shape
    $pointObj = ms_newPointObj();
   foreach($featureClass As $polygon){

        $oShp = ms_newShapeObj(MS_SHAPE_POLYGON);
        $outerBoundaryIs=$polygon->getElementsByTagname("outerBoundaryIs");//Dom version
        //$outerBoundaryIs=$polygon->get_elements_by_tagname("outerBoundaryIs");//DomXML version
        $coordinates=$outerBoundaryIs->item(0)->getElementsByTagname("coordinates");//Dom version
        //$coordinates=$outerBoundaryIs[0]->get_elements_by_tagname("coordinates");//DomXML version
        $po=explode(" ",trim($coordinates->item(0)->textContent));//Dom version
        //$po=explode(" ",trim($coordinates[0]->get_content()));//DomXML version
        $oLine = ms_newLineObj();
        foreach ($po As $p) {
             if($p && $p !="\n" && $p !="\r")
             {
              $co=explode(",",$p);
              $pointObj->setXY($co[0], $co[1]);
              $oLine->add($pointObj);
             }
         }
        $oShp->add($oLine);
        //prendo innerBoundaryIs
        $innerBoundaryIs=$polygon->getElementsByTagname("innerBoundaryIs");//Dom version
        //$innerBoundaryIs=$polygon->get_elements_by_tagname("innerBoundaryIs");//DomXML version
        if ($innerBoundaryIs->length>0){
            $oLine = ms_newLineObj();
            $coordinates=$innerBoundaryIs->item(0)->getElementsByTagname("coordinates");//Dom version
            //$coordinates=$innerBoundaryIs[0]->get_elements_by_tagname("coordinates");//DomXML version
            $po=explode(" ",trim($coordinates->item(0)->textContent));//Dom Version
            //$po=explode(" ",trim($coordinates[0]->get_content()));//DomXML version
           
            foreach ($po As $p) {
                if($p && $p !="\n" && $p !="\r")
                {
                  $co=explode(",",$p);
                  $pointObj->setXY($co[0], $co[1]);
                  $oLine->add($pointObj);
                }
            }
                $oShp->add($oLine);
         }
         $layerObj->addFeature($oShp);
     }
     return 1;
}


?>

<?php
class KMLParser {
   var $xml_url;
   var $dom;
   function KMLParser($xml_url) {
         $this->xml_url = $xml_url;
      
        if (!$this->dom = DOMDocument::load($this->xml_url))//DOM version
        //if (!$this->dom = domxml_open_file($this->xml_url))//DomXML version
        {
        die ("Error while parsing the document\n");
        }
   }
   function getPlacemarks(){
          $placemarks=$this->dom->getElementsByTagname("Placemark");//DOM version
          //$placemarks=$this->dom->get_elements_by_tagname("Placemark");//DomXML version
          return $placemarks;
   }
   function getPlacemarkName($placemark){
          $names=$placemark->getElementsByTagname("name");//DOM version
          //$names=$placemark->get_elements_by_tagname("name");//DomXML version
          return $names->item(0)->textContent;//Dom version
          //return $names[0]->get_content();//DomXML version
   }
   function getPolygons($placemark){
          $polygons=$placemark->getElementsByTagname("Polygon");//Dom version
          //$polygons=$placemark->get_elements_by_tagname("Polygon");//DomXML version
          return $polygons;

  }
   function getLines($placemark){
           $lines=$placemark->getElementsByTagname("LineString");//Dom version
           //$lines=$placemark->get_elements_by_tagname("LineString");//DomXML version
           return $lines;
   }
    function getPoints($placemark){
            $points=$placemark->getElementsByTagname("Point");//Dom version
            //$points=$placemark->get_elements_by_tagname("Point");//DomXML version
            return $points;
   }

}

function GetContentAsString($node) {
  $st = "";
  foreach ($node->childNodes() as $cnode)//Dom version 
  //foreach ($node->child_nodes() as $cnode)//DomXML version
   if ($cnode->nodeType()==XML_TEXT_NODE)//Dom version
   //if ($cnode->node_type()==XML_TEXT_NODE)//DomXML version
     $st .= $cnode->nodeValue();//Dom version
     //$st .= $cnode->node_value();//DomXML version
   else if ($cnode->nodeType()==XML_ELEMENT_NODE) {//DOM version
   //else if ($cnode->node_type()==XML_ELEMENT_NODE) {//DomXML version
     $st .= "<" . $cnode->nodeName();//Dom version
     //$st .= "<" . $cnode->node_name();//DomXML version
     if ($attribnodes=$cnode->attributes()) {//attributes funziona sia con Dom che con DomXML
       $st .= " ";
       foreach ($attribnodes as $anode)
         $st .= $anode->nodeName() . "='" .//DOM version
         //$st .= $anode->node_name() . "='" .//DomXML version
           $anode->node_value() . "'";
       }   
     $nodeText = GetContentAsString($cnode);
     if (empty($nodeText) && !$attribnodes)
       $st .= " />";        // unary
     else
       $st .= ">" . $nodeText . "</" .
         $cnode->node_name() . ">";//Dom version
         //$cnode->node_name() . ">";//DomXML version
     }
  return $st;
  }
?>