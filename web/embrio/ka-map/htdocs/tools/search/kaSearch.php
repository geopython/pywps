<?php

/**********************************************************************
 *
 * $Id: kaSearch.php,v 1.3 2006/08/11 21:38:59 lbecchi Exp $
 *
 * purpose: search system for ka-Map (bug 1509)
 *         
 *
 * author: Paul Spencer, Lorenzo Becchi & Andrea Cappugi
 *
 * TODO:
 *   - 
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

//VARIABLE DEFINITIONS
//max results to output (to avoid data fload and server stress)
$max_results_per_layer = 20;


//ERROR HANDLING
if (isset ($_REQUEST['debug']))
	error_reporting(E_ALL);
else
	error_reporting(E_ERROR);


//REQUEST HANDLING
if (empty ($_REQUEST['searchstring'])) {

	$searchstring = "/Empty/";

	echo "Input string";

	die;

} else {

	// icnv is used only if your page encoding is different from data source encoding

	// in ISO-8859-13 encoding place your code

	$searchstring = iconv("UTF-8", "ISO-8859-13", $_REQUEST['searchstring']);

	$searchstring = "/" . $searchstring . "/i";//case insensitive
	//$searchstring = "/" . $searchstring . "/";//case sensitive

}
//echo "<p><small>" . gmdate("D, d M Y H:i:s") . "</small></p>";
echo "<p>Search string:</p><h6>" . $_REQUEST['searchstring'] . "</h6><hr>";

/**

* Mapscript query example, with both POSTGIS and SHAPEFILE

* in this example we want to query all the map layers with layer metadata

* value searchfield

**/

include_once ('../../../include/config.php');

if (!extension_loaded('MapScript')) {
	dl($szPHPMapScriptModule);
}
$oMap = ms_newMapObj($szMapFile);

$oMap->preparequery();
$tot = $oMap->numlayers; //number of layers in map
?>

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
echo "<div id=\"data\">";

$totResults = 0;

//LOOP ON LAYERS

for ($i = 0; $i < $tot; $i++) {
	$oLayer = $oMap->getLayer($i);
	//CHECKING GROUPS FOR VISIBILITY
	if ($oLayer->type != MS_LAYER_RASTER) {
		//echo($oLayer->group);

		//if BASE group
		/*if ($oLayer->group == "")
			$oLayer->set('status', MS_ON);
		//if on visible group
		elseif (in_array($oLayer->group, $aGroup)) {
			$oLayer->set('status', MS_ON);
			if (!$oLayer->isVisible() && ($oLayer->minscale < $scale && $oLayer->maxscale > $scale)) {
				$oLayer->set("minscale", 0);
				$oLayer->set("maxscale", (200000000)); // has to be greater that map maximum scale
			}
		} else {
			$oLayer->set('status', MS_OFF);
			if (!$oLayer->isVisible() && ($oLayer->minscale < $scale && $oLayer->maxscale > $scale)) {
				$oLayer->set("minscale", 0);
				$oLayer->set("maxscale", (200000000)); // has to be greater that map maximum scale
			}
			continue;
		}*/

		$szSearchfield = $oLayer->getMetaData('searchfield');
		//PRINTING STUFF

		

		if ($oLayer->queryByAttributes($szSearchfield, $searchstring, MS_MULTIPLE) == MS_SUCCESS) {

			
			//echo "<br>num records:".$oLayer->getNumResults();
			$totR = $oLayer->getNumResults();
			$totResults = $totResults + $totR;
			echo "<p>Layer Name:</p> <h6>" . $oLayer->name . "</h6>";
			
			if($max_results_per_layer < $totR) echo "<p>results: $max_results_per_layer of $totR (limited output)</p>";
			else echo "<p>results: $totR</p>";
			$oLayer->open();

			// METADATA
			$szFields = $oLayer->getMetaData("fields");
			//echo "<br>Fields".$szFields;
			if ($szFields != '') {
				$aField = explode(',', $szFields);
				foreach ($aField as $key => $value) {
					$field = explode(':', $value);
					$fields[$field[0]] = (count($field) == 2) ? $field[1] : null;
				}
			}
			//get hyiperlink
			$szHyperlink = $oLayer->getMetaData("hyperlink");
			if ($szHyperlink != '') {
				$hyperlink = explode('|', $szHyperlink);
			} else
				$hyperlink = null;
			//END METADATA

			echo "<table>";
			if ($totR) {
				$oResultCache = $oLayer->getResult($i);
				$oShape = $oLayer->getShape($oResultCache->tileindex, $oResultCache->shapeindex);

				

				$aKeys = array_keys($oShape->values);
				foreach ($aKeys as $key) {
					$aKeysNormal[] = strtoupper($key);
				}

				echo "<tr>";
				foreach ($fields as $key => $value) {

					if (in_array(strtoupper($key), $aKeysNormal)) {
						echo "<th>" . $fields[$key] . "</th>";
					} else
						unset ($fields[$key]);
				}
				if ($hyperlink) {
					if (in_array($hyperlink[0], $aKeys))
						echo "<th>" . $hyperlink[0] . " - hyperlink</th>";
					else
						$hyperlink = null;
				}
				echo "<th>Zoom to</th>";
				echo "</tr>";

				/*  //ALL FIELDS
				 echo "<tr>";
				foreach($aKeys as $key){
				    echo "<th>$key</th>";
				}
				echo "</tr>";*/
				$oShape->free();
			}
			if ($totR > $max_results_per_layer)
				$totR = $max_results_per_layer;

			for ($a = 0; $a < $totR; $a++) {
				$oResultCache = $oLayer->getResult($a);
				$oShape = $oLayer->getShape($oResultCache->tileindex, $oResultCache->shapeindex);
				$aValues = $oShape->values;
				
				//Calculate centroid for example tooltipe needs

				$x_c = ($oShape->bounds->minx + $oShape->bounds->maxx) / 2;

				$y_c = ($oShape->bounds->miny + $oShape->bounds->maxy) / 2;

				//$aTmp = array_merge( $aTmp ,  array('x' => $x,'y' => $y, 'id' => $result->shapeindex));

				//Calculate area coordinates for example function gotorectangle

				$xmin = $oShape->bounds->minx;

				$xmax = $oShape->bounds->maxx;

				$ymin = $oShape->bounds->miny;

				$ymax = $oShape->bounds->maxy;

				echo "<tr>";
				//echo "<td>".print_r($aValues)."</td>";
				foreach ($fields as $key => $value) {

					if ($aValues[strtoupper($key)]) {
						$val = $aValues[strtoupper($key)];
					} else
						if ($aValues[strtolower($key)]) {
							$val = $aValues[strtolower($key)];
						} else
							if ($aValues[$key]) {
								$val = $aValues[$key];
							} else {
								$val = " ";
							}
					echo "<td>$val</td>";

				}
				
				echo "<td align=\"center\"><a href=\"#\" onClick=\"myKaMap.zoomToExtents($xmin,$ymin,$xmax,$ymax)\"><img id=\"toolZoomInMini\" src=\"images/a_pixel.gif\" alt=\"zoom to\"></a></td>";
				//if($value)echo "<td>$value</td>";
				//else echo "<td>&nbsp;</td>";

				echo "</tr>";
				$oShape->free();
			}
			echo "</table><hr>";
			if ($totR > $max_results_per_layer)
				echo "Too many values to output, please reduce the request.";
			$oLayer->close();
			$fields = array ();
		}
	}
}

//$image=$oMap->drawQuery();
//$url=$image->saveWebImage();
if ($totResults) {
	// echo "<h6>tot res:$totResults</h6>";
} else
	echo "<h6>no matching results</h6><hr>";
?>
</div>

