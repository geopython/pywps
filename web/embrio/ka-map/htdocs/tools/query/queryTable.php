<?php
/**********************************************************************
 * $Id: queryTable.php,v 1.2 2006/07/12 14:46:40 acappugi Exp $
 * 
 * purpose: a simple query script used to print alfanumeric information of a query (bug 1508)
 *
 * author: Andrea Cappugi & Lorenzo Becchi
 *
 * 
 *
 * TODO:
 *
 * 
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
 /*
 * This script execute laod a quary executed before(query.php) and 
 * retrive alfanumeric information of selected records
 * 
 * 
 *
 * map: the name of the map to use.  This is handled by config.php.
 * sessionId: the session id
 * id:the query id to be loaded
 * 
 * 
 * send an xml document with query result
 * 
 * dtd
 * <query>
 *  <layer>
 * 	 <name></name>
 * 	 <group></group>
 *   <type></type>
 *   <fields>
 * 		 <field>
 * 			<name></name>
 * 			<alias></alias>
 * 			<type></type>
 * 		 </field>
 *   </field>
 *   <records>
 *     <number></number>
 * 	 <rec>
 * 		<ext><ext>
 * 	 	<val></val>
 *   </rec>
 *  <records>
 *  </layer>
 * </query>
 */
 //ERROR HANDLING
  if(isset($_REQUEST['debug'])) error_reporting ( E_ALL );
  else error_reporting( E_ERROR );
    error_reporting ( E_ALL );
  include_once( '../../../include/config.php' );
  if (!extension_loaded('MapScript'))
  {
    dl( $szPHPMapScriptModule );
  }
  $oMap = ms_newMapObj($szMapFile);


  //check if the session is on
  if (isset($_REQUEST['sessionId'])) $sessionId=trim($_REQUEST['sessionId']);
  else{
    $szResult= 'alert ("sessionId query required");';
    echo $szResult;
    die;
  } 
   if(isset($_REQUEST['id'])) $qId= $_REQUEST['id'];
  else{
    $szResult= 'alert ("id query required");';
    echo $szResult;
    die;
  }

  //Build query sys cache directory!!
  $szQueryCache=$szBaseCacheDir."/sessions/".$sessionId."/QuerySys/".$szMap."/".$qId."/query.bin"; 

  /* check if query cache exists */
  if (!@is_file($szQueryCache)){
  	$szResult= 'alert ("Error retriving saved query");';
    echo $szResult;
    die;
  }else //load the query 


$oMap->loadquery($szQueryCache);

    
//	$szResult="<textarea style='width:600px;height:100px;'><query><id>$qId</id>";
$szResult="<query><id>$qId</id>";
  //get Layers
  $nLayers = $oMap->numlayers;
  for($i=0;$i<$nLayers;$i++)
    {
      $oLayer = $oMap->getLayer($i);
      $totR = $oLayer->getNumResults();	
      if ($totR>0){
        //qui puoi printare quello che vuoi!!
		$szResult.="<layer> <name>".$oLayer->name."</name> <group>".$oLayer->group."</group><type>".$oLayer->type."</type> <fields>";						
		//get metadata
		 $szFields =$oLayer->getMetaData("fields");
		 //$szResult.=$szFields;
		 if ($szFields != '') {
		     $aField=explode(',',$szFields);
			 foreach ($aField as $key => $value) {
			 	$field = explode(':',$value);
			 	$fields[$field[0]]=(count($field)==2)? $field[1]:null;
			 }
		}
		//get hyiperlink
		$szHyperlink=$oLayer->getMetaData("hyperlink");
		if($szHyperlink!=''){
			$hyperlink=explode('|',$szHyperlink);
		}else $hyperlink=null;
		
		
		$oLayer->open();
		$oResultCache = $oLayer->getResult(0);                              
		$oShape = $oLayer->getShape($oResultCache->tileindex,$oResultCache->shapeindex);
		$aKeys = array_keys($oShape->values);
		
		$szResult.=$szFields;
		if($szFields != ''){     
		  foreach($fields as $key => $value){
            if(in_array($key, $aKeys)) {
              $szResult.="<field> <name>".$key."</name> <alias>".$fields[$key]."</alias><type>value</type></field>";
            }else unset($fields[$key]);
          }
         if($hyperlink){
			if(in_array($hyperlink[0], $aKeys))
			 $szResult.="<field> <name>".$hyperlink[0]."</name> <alias>hyperlink</alias><type>url</type></field>";
			 else $hyperlink=null;
         } 
          $oShape->free();
          $szResult.="</fields> <records> <number>".$totR."</number>";
          
          	for($a=0;$a<$totR;$a++){
			  $szResult.="<rec>";
			  $oResultCache = $oLayer->getResult($a);
			  $oShape = $oLayer->getShape($oResultCache->tileindex,$oResultCache->shapeindex);
              $rect=$oShape->bounds;
              $szExt=$rect->minx." ".$rect->miny." ".$rect->maxx." ".$rect->maxy;
              $szResult.="<ext>".$szExt."</ext>";
              $aValues = $oShape->values;
              foreach($fields as $key => $value){
              	 $val=($aValues[$key])?$aValues[$key]:null;
              	 $szResult.="<val>".$val."</val>";
                
              }
              if($hyperlink){
                $val=($aValues[$hyperlink[0]])?$aValues[$hyperlink[0]]:null;
	            $link=(count($hyperlink)==2)?($hyperlink[1]."?".$hyperlink[0]."=".$val):$val;
	            $szResult.="<val>".$link."</val>";         
              }
              $szResult.="</rec>";
              $oShape->free();
          	}
          	$szResult.="</records>";          	
        }else{
        	foreach($aKeys as $key){
               $szResult.="<field> <name>".$key."</name><alias></alias><type>value</type></field>";
          	}
          	if($hyperlink){
          	 if(in_array($hyperlink[0], $aKeys))
			 $szResult.="<field> <name>".$hyperlink[0]."</name> <alias>hyperlink</alias><type>url</type></field>";
			 else $hyperlink=null; 
          	}
          	$oShape->free();
          	$szResult.="</fields> <records> <number>".$totR."</number>";
          	for($a=0;$a<$totR;$a++){
			  $szResult.="<rec>";
			  $oResultCache = $oLayer->getResult($a);
			  $oShape = $oLayer->getShape($oResultCache->tileindex,$oResultCache->shapeindex);
			  $rect=$oShape->bounds;
              $szExt=$rect->minx." ".$rect->miny." ".$rect->maxx." ".$rect->maxy;
              $szResult.="<ext>".$szExt."</ext>";
              $aValues = $oShape->values;
              foreach($aValues as $key => $value){
              	$val=($value)?$value:null;
   	            $szResult.="<val>".$val."</val>";
              }
              if($hyperlink){
                $val=($aValues[$hyperlink[0]])?$aValues[$hyperlink[0]]:null;
	            $link=(count($hyperlink)==2)?($hyperlink[1]."?".$hyperlink[0]."=".$val):$val;
	            $szResult.="<val>".$link."</val>";         
              }
              $szResult.="</rec>";
              $oShape->free();
          	}
          	$szResult.="</records>";          	
        }
        $szResult.="</layer>";
      }
    }		
         $szResult.="</query>" ;
//     $szResult.="</query></pre></textarea>" ;
            
            header("Content-Type: text/xml");
			header("Cache-Control: no-store, no-cache, must-revalidate");
			//echo '<?xml version="1.0" encoding="UTF-8" >';
            echo $szResult;
            die;	
?>