<?php
/**********************************************************************
 *
 * $Id: xsearch.php,v 1.4 2006/08/08 20:50:41 lbecchi Exp $
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


if(empty($_REQUEST['searchstring'])){

  $searchstring = "/Empty/";

  echo "<h6>Input string missing</h6>";

  die;

}else{

  // icnv is used only if your page encoding is different from data source encoding

  // in ISO-8859-13 encoding place your code

 $searchstring=iconv("UTF-8", "ISO-8859-13", $_REQUEST['searchstring'] );

 $searchstring="/".$searchstring."/";

}
echo "<p><small>".gmdate("D, d M Y H:i:s")."</small></p>";
echo "<p>Search string: <strong>".$_REQUEST['searchstring']."</strong></p>";

/**

* Mapscript query example, with both POSTGIS and SHAPEFILE

* in this example we want to query all the map layers with layer metadata

* value searchfield

**/

include_once( '../../../include/config.php' );





if (!extension_loaded('MapScript'))

{

    dl( $szPHPMapScriptModule );

}

$isresult=0; //cont for layers where was somethig returned

$results = array();

$oMap = ms_newMapObj($szMapFile);


$aLayers = $oMap->getAllLayerNames(); //get all layer nemes

$tot = $oMap->numlayers; //number of layers in map



//------------------------------------------------------------------------------

foreach($aLayers AS $layer) {

        $oLayer = $oMap->getLayerByName($layer);



/** detect if group should be queryable 

 *for search it is not important

**/

        $szQueryable = "false";

        if ($oLayer->getMetaData( "queryable" ) != "") {

            if(strcasecmp($oLayer->getMetaData("queryable"), "true") == 0)

                $szQueryable = "true";

        }

        

/** detect if group should be searchable 

 * this is importamt for searcht to cnow search foield in database

 * **/

        $szSearchfield = $oLayer->getMetaData('searchfield');

        if ($oLayer->getMetaData( "searchfield" ) != "") {

              $szSearchfield = $szSearchfield;

//----------------------------------------------------

            if($oLayer->connectiontype == MS_POSTGIS){

                $searchstring = $szSearchfield . ' ~* \'' . $searchstring .'\'  ';

              } else {  // Shapefile

                $numclasses = $oLayer->numclasses;

                for($i = 1 ; $i < $numclasses; $i++){

                   // This produces a fatal: Call to undefined method ms_layer_obj::removeClass()

                   // $layer->removeClass();

                }

                // Second HACK: it work

                if($numclasses > 1){

                  $class = $oLayer->getClass(0);

                  // Match all

                  $class->setExpression('/.*/');

                }

              }

#----------------------------------------------------------------------------------------------
              if(@$oLayer->queryByAttributes($szSearchfield, $searchstring,MS_MULTIPLE) == MS_SUCCESS ){ //MS_SUCCESS
													// MS_MULTIPLE or MS_SINGLE
            	$oLayer->open();

                // Add element to results array for each result row

                $totr=$oLayer->getNumResults();

                for ($j=0; $j < $totr ; $j++)

                {

                    // get next shape row

                    $result = $oLayer->getResult($j);

                    $shape  = $oLayer->getShape($result->tileindex, $result->shapeindex);

                    // push the row array onto the results array

                    $aTmp = $shape->values;

                    //Calculate centroid for example tooltipe needs

                    $x_c = ($shape->bounds->minx + $shape->bounds->maxx) / 2;

                    $y_c = ($shape->bounds->miny + $shape->bounds->maxy) / 2;

                    //$aTmp = array_merge( $aTmp ,  array('x' => $x,'y' => $y, 'id' => $result->shapeindex));

                    //Calculate area coordinates for example function gotorectangle

                    $xmin = $shape->bounds->minx;

            	      $xmax = $shape->bounds->maxx;

                    $ymin = $shape->bounds->miny;

            	      $ymax = $shape->bounds->maxy;

                    $aTmp = array_merge( $aTmp ,  array('xmin' => $xmin,'xmax' => $xmin,'ymin' => $ymin,'ymax' => $ymax,'x_c'=>$x_c,'y_c'=>$y_c, 'id' => $result->shapeindex));

                    //$results[$layername][] =  $aTmp;
                    $results[$oLayer->name][] =  $aTmp;

                // end for loop

              }

              //print layer returned results

              printer($results,$szSearchfield,$layer);

              $isresult++;

              }

              $oLayer->close();

//----------------------------------------------------

        $results=flush($results);

        }

        else{

        $szSearchfield = "<p>Not defined searchfield</p>";

        }

 } 

//-------------------------------------if all layers returned 0 results----------

 if($isresult==0) echo"<hr><p><b>No results</b> for all layers with query string:</p> <h6>\"$searchstring\"</h6>";   

//-------------------------------------create print -----------------------------

function printer($results,$szSearchfield,$layer){

  foreach($results as $key_val => $value) {

  	echo "<hr><p>Layer Name:</p> <h6>".$layer."</h6>"; // top for each layer

      foreach($value as $key_val => $v) {

        // in ISO-8859-13 encoding place your code

      $m=iconv("ISO-8859-13", "UTF-8", $key_val[$szSearchfield]); //just liek in start iconv is nedet if your page and data encoding  is different

      //$field=$v[strtoupper($szSearchfield)]; // searchfield name
      if(isset($v[strtoupper($szSearchfield)]))
      	$field=$v[strtoupper($szSearchfield)]; // searchfield name
      else if (isset($v[strtolower($szSearchfield)]))
      	$field=$v[strtolower($szSearchfield)]; // searchfield name
      else if (isset($v[$szSearchfield]))
      	$field=$v[$szSearchfield]; // searchfield name
      else 
      	$field="<h6>no match for: ".$szSearchfield."</h6>";
      	
      $ku=$key_val["LOCATION"];

      $ku2=ltrim($ku,"/var/www/");

      //printing results with first link-show tooltipe, second link-go to rectangle
			//this.toolTip.setTipImage('images/tip-red.png',offsetX,offsetY);
			
			$outText="<table>";
			foreach($v as $key => $value){
				
				if($key !="xmin" &&$key !="ymin" && $key !="xmax" && $key !="ymax" && $key !="x_c" && $key !="y_c")
					$outText.= "<tr><th>".ucwords(strtolower($key))."</th><td>$value</td></tr>";
			}
			$outText.="</table>";
			
          print "<div class=\"kaLegendLayer\"><a href=\"#\" onClick=\"myKaSearch.tooltip.setText('<h3>$field</h3>".$outText."');myKaSearch.tooltip.moveGeo(".$v["x_c"].",".$v["y_c"].");\">Show point</a> | <a href=\"#\" onClick=\"myKaMap.zoomToExtents(".$v["xmin"].",".$v["ymin"].",".$v["xmax"].",".$v["ymax"].")\">$field</a></div>\n";
          //print_r($v); 

        }

      }

  }



//-------------------------------------create print end--------------------------

?>

