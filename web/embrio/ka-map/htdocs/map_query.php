<?php
//Bug reference: 
//http://bugzilla.maptools.org/show_bug.cgi?id=1313

//VARIABLE DEFINITIONS
//max results to output (to avoid data fload and server stress)
$max_results_per_layer = 20;

//ERROR HANDLING
if(isset($_REQUEST['debug'])) error_reporting ( E_ALL );
else error_reporting( E_ERROR );

include_once( '../include/config.php' );

if (!extension_loaded('MapScript'))
{
    dl( $szPHPMapScriptModule );
}
$oMap = ms_newMapObj($szMapFile);
if (isset($_REQUEST['scale']))
{
    $scale= $_REQUEST['scale'];
}

if (isset($_REQUEST['q_type']))
{
    $q_type= $_REQUEST['q_type'];
} else 
{
    echo "q_type not defined";
   die;
}
if (isset($_REQUEST['coords']))
{
    $coords= explode(',',$_REQUEST['coords']);
} else 
{
    echo "coordinate not defined";
    die;
}
if (isset($_REQUEST['groups']))$groups=$_REQUEST['groups'];
else $groups="";
$aGroup=explode(',',$groups);

/* Check that user has the rights to see requested group(s).
 */
if (isset($oAuth) && $groups)
{
    foreach ($aGroup as $thisGroup)
    {
        if (!$oAuth->testPrivilege($thisGroup))
        {
            /* User is not authorized. */
            echo "You are not authorized to access group '$thisGroup'\n";
            exit;
        }
    }
}

if (isset($_REQUEST['extent']))$extent=$_REQUEST['extent'];
else $extent="";
$aExtent=explode('|',$extent);
//print_r($coords);
//print_r( "query type:$q_type coords:".$coords." gruppi: ".$groups." extent: ".$extent." <br>");

//SETTING MAP EXTENT. 
$mapExtent = $oMap->extent;
if ((abs($mapExtent->maxx - $mapExtent->minx) - abs($aExtent[2]-$aExtent[0]))>0){
    $oMap->setExtent($aExtent[0],$aExtent[1],$aExtent[2],$aExtent[3]);
 
}
//$oMap->setExtent($aExtent[0],$aExtent[1],$aExtent[2],$aExtent[3]);

// SETTING QUERY POINT
if($q_type==0){
$point = ms_newPointObj();
$point->setXY($coords[0],$coords[1]);
//$oMap->zoompoint(2,$point,$oMap->width,$oMap->height,$oMap->extent);
}elseif($q_type==1)
{
$rect=ms_newRectObj();
$rect->setextent($coords[0],$coords[3],$coords[2],$coords[1]);
$oMap->setExtent($coords[0],$coords[3],$coords[2],$coords[1]);
}else
{
   echo "bad query type";
   die;
}

$oMap->preparequery();
?>
<html>
<head>
<title>
Query for: <?=$mX?> - <?=$mY?>
</title>
<style type="text/css">
body {
padding:0;
margin:0;
 font:arial,serif;
}

h2 {
    border:1px solid black;
    font-size:1.2em;
    padding:0.2em;
    background: gray;
    color: white;   
}
h3 {
    border:1px solid black;
    font-size:0.9em;
    padding:0.2em;
    background: gray;
    color: white;   
}
th {
    border:1px solid black;
    font-size:0.9em;
    padding:0.2em;
    background: rgb(170,170,170);
    color: white; 
    font-weight:bold;  
}
td {
    border-bottom:1px solid black;
    font-size:0.9em;
    padding:0.2em;
}
#data{
    position:absolute;
//    top:320px;
}
#image{
    position:absolute;
    top:0;
    border-top:2px solid black;
    border-bottom:2px solid black;
    width:100%;
    text-align:center;
    margin-top:10px;
    margin-bottom:10px;

}
img {
    padding:5px;
    margin:2px;
    border:1px solid black; 
}
.error {
position: absolute;
top:0;
width:95%;
text-align:center;
  margin:5px;
  padding:10px;
  border:1px solid black;
  color: red;
font-size:2em;

}
</style>
</head>
<body onload="window.focus();">

<?php
/*
 * Uncomment this code to set a minimum scale limit
 */
 
 /*
if($scale>100001){
echo "<span class=\"error\"> Identify system has 100000 as minimum scale</span>";
die;
}
*/
echo"<div id=\"data\">";

setOutputFormat("JPEG");
$oMap->selectOutputFormat( $szMapImageFormat );
//LOOP ON LAYERS
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
                
                //PRINTING STUFF
                if($q_type==0)$check_query = $oLayer->queryByPoint($point,MS_MULTIPLE,-1);
                else $check_query =$oLayer->queryByRect($rect);
 		
		if($check_query == MS_SUCCESS){	
                        echo "<h2>Layer Name:".$oLayer->name."</h2>";	
			//echo "<br>num records:".$oLayer->getNumResults();
			$totR = $oLayer->getNumResults();	
			//echo "<br> totR:".$totR;
			$oLayer->open();
                        echo "<table>";
                        if($totR){
                                $oResultCache = $oLayer->getResult($a);                              
				$oShape = $oLayer->getShape($oResultCache->tileindex,$oResultCache->shapeindex);
                                $aKeys = array_keys($oShape->values);
                                echo "<tr>";
                                foreach($aKeys as $key){
                                    echo "<th>$key</th>";
                                }
                                echo "<tr>";
                        	$oShape->free();
			}
             if($totR > $max_results_per_layer) $totR = $max_results_per_layer;           
			for($a=0;$a<$totR;$a++){
				$oResultCache = $oLayer->getResult($a);
				$oShape = $oLayer->getShape($oResultCache->tileindex,$oResultCache->shapeindex);
                                $aValues = array_values($oShape->values);
                                echo "<tr>";
                                foreach($aValues as $value){
                                    if($value)echo "<td>$value</td>";
                                    else echo "<td>&nbsp;</td>";
                                }
                                echo "</tr>";
				$oShape->free();
			} 
                        echo "</table>";
                        if($totR > $max_results_per_layer) echo "Too many values to output, please reduce the request.";
			$oLayer->close();
		}
	} else if($oLayer->type == MS_LAYER_RASTER)
	{
                if($oLayer->group=="")$oLayer->set('status',MS_ON);
                //if on visible group
		elseif (in_array($oLayer->group,$aGroup))$oLayer->set('status',MS_ON);
		else{
		$oLayer->set('status',MS_OFF);
		continue;
		}
                
        if($q_type==0)$check_query = $oLayer->queryByPoint($point,MS_MULTIPLE,-1);
                else $check_query =$oLayer->queryByRect($rect);
        
 		if($check_query == MS_SUCCESS){	
             echo "<h2>Layer Name:".$oLayer->name."</h2>";	
 			//echo "<br>num records:".$oLayer->getNumResults();
 			$totR = $oLayer->getNumResults();	
 			//echo "<br> totR:".$totR;
 			$oLayer->open();
             echo "<h3>pixel founds=".$totR."</h3>";
             if($totR > $max_results_per_layer) $totR = $max_results_per_layer;
             if($totR){
                 echo "<table>";
                        if($totR){
							$oResultCache = $oLayer->getResult($a);                              
							$oShape = $oLayer->getShape($oResultCache->tileindex,$oResultCache->shapeindex);
							$aKeys = array_keys($oShape->values);
							echo "<tr>";
							foreach($aKeys as $key){
							    echo "<th>$key</th>";
							}
							echo "<tr>";
							$oShape->free();
						}
			                        
						for($a=0;$a<$totR;$a++){
							$oResultCache = $oLayer->getResult($a);
							$oShape = $oLayer->getShape($oResultCache->tileindex,$oResultCache->shapeindex);
							    $aValues = array_values($oShape->values);
							    echo "<tr>";
							    foreach($aValues as $value){
							        if($value)echo "<td>$value</td>";
							        else echo "<td>&nbsp;</td>";
							    }
							    echo "</tr>";
							$oShape->free();
						} 
                        echo "</table>";
                  if($totR > $max_results_per_layer) echo "Too many values to output, please reduce the request.";
 			     $oLayer->close();
 			 }
          }
	}
}

//$image=$oMap->drawQuery();
//$url=$image->saveWebImage();
?>
</div>
<?php
/*
?>
<div id="image">
<img src="<?=$url?>">
</div>
<?php
*/
?>
</body>
</html>
