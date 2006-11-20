<?php
/**********************************************************************
 *
 * $Id: wfs_connector.php,v 1.1 2006/06/14 14:18:54 lbecchi Exp $
 *
 * purpose: This simple php script is used by wfsConnector.js class 
 *
 *
 *
 * author: Lorenzo Becchi & Andrea Cappugi      ominiverdi :-)
 *
 **********************************************************************
 *
 * Copyright (c) 2006, ominiverdi.org
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

/*file vuoto*/
session_start();
//error_reporting ( E_ALL );
include_once( '../../../include/config.php' );
include_once( './reproj.php' );
$dir=$szMapCacheDir;

if (isset($_GET['com']))  $com=trim($_GET['com']);
else {
  echo "alert('Define command i.e com=getCapabilities|getFeature|query');";
  die;
}
switch ($com)
{
  case 'getCapabilities':
    getCapabilities();
    break;
  case 'getFeature':
    getFeature();
    break;
  case 'query':
    query();
    break;
  default:
    echo "alert('Error: command not found i.e com=getCapabilities|getFeature|query');";
    die;
    break;
}
function getCapabilities(){
  if (isset($_GET['wfsURL']))  $wfsUrl=trim($_GET['wfsURL']);
  else {
    echo "alert('Error: wfsURL missing, define wfsURL=URL please');";
    die;
  }
    $szResult="this.sessionId='".session_id()."';";
    $cap=new wfsGetCapabilities($wfsUrl);
    $szResult.=buildSelect($cap);
    echo $szResult;
}
function getFeature(){
  if (isset($_GET['wfsURL']))  $wfsUrl=trim($_GET['wfsURL']);
  else {
    echo "alert('Error: wfsURL missing, define wfsURL=URL please');";
    die;
  }
  if (isset($_GET['sessionId'])) $sessionId=trim($_GET['sessionId']);
  else  $sessionId=session_id(); 
   if (isset($_GET['epsg']))  $to_epsg=trim($_GET['epsg']);
  else $to_epsg=null;
  global $dir;
  session_id($sessionId);
//detect fetclass name
 $fatClassName=null;
  $aParam = explode('&',$wfsUrl);
  foreach($aParam As $value)
    if(stristr($value,"typename")) $fatClassName=substr(stristr($value,"typename"),9); 
  if($fatClassName==null){
    echo "alert('Error: missing typename in wfsURL!');";
    die;
  }
  $szResult="feature='$fatClassName';";
  $geom=new wfsGetGeometries($wfsUrl);
  $lPoints=$geom->getPointGeometries();
  $srs_epsg=explode(":",$geom->getEPSG());
  
  
  if($to_epsg!=null && $lPoints->length>0 && $to_epsg!=$srs_epsg)
  {
  		$pArray=array();
 		 	
  		
  		for($i=0;$i<$lPoints->length -1 ;$i++){
  		$pArray[]=explode(",",$geom->getPointCoords($lPoints->item($i)));
  		}
  		$r=new reproj($pArray,$srs_epsg[1]);
  		$p=$r->cs2cs($to_epsg);
	  	$szResult.="this.points=new Array(";
  		for($i=0;$i<count($p) -1 ;$i++)
  	    	 $szResult.="new Array($i,".$p[$i]->x.",".$p[$i]->y."),";
  		$szResult.="new Array($i,".$p[$i]->x.",".$p[$i]->y."));";
  	 	
  }
  elseif($lPoints->length>0)
  {
    $szResult.="this.points=new Array(";
    for($i=0;$i<$lPoints->length -1 ;$i++)
      $szResult.="new Array($i,".$geom->getPointCoords($lPoints->item($i))."), ";
    $szResult.="new Array($i,".$geom->getPointCoords($lPoints->item($i)).")); "; 
 }else $szResult="alert('Any point for this wfs layer');";
  echo $szResult;

  $_SESSION['path']= $dir."/".$sessionId;
  if (!@is_dir($_SESSION['path']))
    makeDirs($_SESSION['path']);
    $geom->dom->save($_SESSION['path']."/$fatClassName.gml");
}
function query(){
  if (isset($_GET['sessionId'])) $sessionId=trim($_GET['sessionId']);
  else{
    echo "alert('Error: sessionId missing, define sessionId to execute query');";
    die;
  }
  if (isset($_GET['featureId']))$ftId=$_GET['featureId'];  
  else{
    echo "alert('Error: featureId missing, define featureId to execute query');";
    die;
  }
  if (isset($_GET['features']))$fatClassName=$_GET['features'];  
  else{
    echo "alert('Error: featureClassName missing, define featureClassName to execute query');";
    die;
  }
  global $dir;
  session_id($sessionId);
  $expURL='(^|[ \t\r\n])((ftp|http|https):(([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?([A-Za-z0-9$_+!*();/?:~-]))';
  $expMail='(^|[ \t\r\n<;(])((([A-Za-z0-9$_.+%=-])|%[A-Fa-f0-9]{2})+@(([A-Za-z0-9$_.+!*,;/?:%&=-])|%[A-Fa-f0-9]{2})+\.[a-zA-Z0-9]{1,4})';
  $szResult='';
  if(!isset($_SESSION['path'])){
  	echo "alert('Error: session expired reloda features')";
  	die;  
  }
  
  if(file_exists($_SESSION['path']."/$fatClassName.gml"))
  {
    $geom=new wfsGetGeometries($_SESSION['path']."/$fatClassName.gml");
    $lPoints=$geom->getPointGeometries();
    if($lPoints->length>0 && $lPoints->length>$ftId)
    {
      $attr=$geom->getAttributes($lPoints->item($ftId));
      $szResult.="this.toolTip.setText(urlDecode('<table>";
        foreach($attr As $key => $value){
      	if(trim($value)){
      		$akey=explode(":",$key);
      		if(count($akey)>1)$key=$akey[1];
       		$key = str_replace("_", " ", $key);
      		if( ereg($expURL,$value)==1)
        		$szResult.="<tr><th>".urlencode($key)."</th><td><a href=\"".urlencode($value)."\" target=\"_blank\"> LINK </a></td></tr>";
      		elseif( ereg($expMail,$value)==1)
      			$szResult.="<tr><th>".urlencode($key)."</th><td><a href=\"mailto:".urlencode($value)."\"> MAIL </a></td></tr>";
      		else
      			$szResult.="<tr><th>".urlencode($key)."</th><td>".urlencode($value)."</td></tr>";
      	}
      }
         $szResult.="</table>'));";
    }else $szResult="alert('Error: featureId out of range!');";
  }
  echo $szResult;
}

?>
<?php
class wfsGetCapabilities {
   var $xmlUrl;
   var $dom;
   function wfsGetCapabilities($xmlUrl) {
         $this->xmlUrl = $xmlUrl;
        if (!$this->dom = DOMDocument::load($this->xmlUrl))
        {
        echo "alert('Error: unable to open server');";
        die;
        }
  }
function getNames(){
          $aNames=array();
          $lFeatureType=$this->dom->getElementsByTagname("FeatureType");
          for ($i=0;$i<$lFeatureType->length;$i++){
            $aNames[]=$lFeatureType->item($i)->getElementsByTagname("Name")->item(0)->textContent;
          }
}
function getFeaturesClasses(){
          $lFeatureType=$this->dom->getElementsByTagname("FeatureType");
          return $lFeatureType;
   }
function getName($featureType){
        if( $featureType->getElementsByTagname("Name")->length>0)
          return $featureType->getElementsByTagname("Name")->item(0)->textContent;
}
function getTitle($featureType){
        if( $featureType->getElementsByTagname("Title")->length>0)
          return $featureType->getElementsByTagname("Title")->item(0)->textContent;
}
function getSRS($featureType){
          if( $featureType->getElementsByTagname("SRS")->length>0)
          return $featureType->getElementsByTagname("SRS")->item(0)->textContent;
}
}
class wfsGetGeometries {
   var $xmlUrl;
   var $dom;
   function wfsGetGeometries($xmlUrl) {
         $this->xmlUrl = $xmlUrl;
 
        if (!$this->dom = DOMDocument::load($this->xmlUrl))
        {
        die ("Error while parsing the document\n");
        }
  }
function getPointGeometries(){
          $lFeatures=$this->dom->getElementsByTagname("Point");
          return $lFeatures ;
}
function getPointCoords($feature){
          if($feature->getElementsByTagname("coordinates")->length > 0)
          return $feature->getElementsByTagname("coordinates")->item(0)->textContent;
  }
function getEPSG(){
		  $box=$this->dom->getElementsByTagname("Box");
		  if($box->item(0))return $box->item(0)->getAttribute("srsName");
        	else return 0;    
  }
function getAttributes($feature){
          $aAtribute=array();
          if($feature->parentNode){
           	$parent=$feature->parentNode;
            $sib=$parent->nextSibling;
          while ($sib)
          	{   
          		if($sib->nodeType==1)
          		$aAtribute[" $sib->nodeName "]=$sib->textContent;
          		$sib=$sib->nextSibling;
          	}
          }
          return $aAtribute;
  }
}
function buildSelect($cap){
  $nlFeaturesClass=$cap->getFeaturesClasses();
  $string="var select= getRawObject('wfsSelect');";
  for ($i=0; $i<$nlFeaturesClass->length; $i++){
    $string.="var option=document.createElement('option');";
    $string.="option.innerHTML='".$cap->getTitle($nlFeaturesClass->item($i))."';";
    $string.="option.setAttribute('value','".$cap->getName($nlFeaturesClass->item($i))."');";
    $string.=" select.appendChild(option);";
  }
  return $string;
}
?>