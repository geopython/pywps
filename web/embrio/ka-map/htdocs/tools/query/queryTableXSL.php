<?php
/**********************************************************************
 * $Id: queryTableXSL.php,v 1.3 2006/07/12 14:47:20 acappugi Exp $
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
  //check if the session is on
  if (isset($_REQUEST['sessionId'])) $sessionId=trim($_REQUEST['sessionId']);
  else{
    $szResult= 'alert ("sessionId query required");';
    echo $szResult;
    die;
  } 
   if (isset($_REQUEST['map'])) $map=trim($_REQUEST['map']);
  else{
    $szResult= 'alert ("map required");';
    echo $szResult;
    die;
  } 
  
  if(isset($_REQUEST['id'])) $qId= $_REQUEST['id'];
  else{
    $szResult= 'alert ("id query required");';
    echo $szResult;
    die;
  }
  $output = (isset($_REQUEST['output']))? $_REQUEST['output']:"html"; 

//Getting actual http working dir  
$req = $HTTP_SERVER_VARS['SCRIPT_NAME'];
$server = $_SERVER['SERVER_NAME'];
$prot = $_SERVER['SERVER_PROTOCOL'] ;
$dir = str_replace(strrchr($req,'/'),'/',$req);
$protocol=strtolower(str_replace(strchr($prot,'/'),'://',$prot));
$path=$protocol.$server.$dir;
$szUrl=$path."queryTable.php?sessionId=".$sessionId."&id=".$qId;
 
if ( class_exists("XSLTProcessor")){
// Load the XML source
$xml = new DOMDocument;
$xml->load($szUrl);

$xsl = new DOMDocument;
if($output=="table") $xsl->load('table.xsl');
else $xsl->load('html.xsl');

// Configure the transformer
$proc = new XSLTProcessor;
$proc->importStyleSheet($xsl); // attach the xsl rules

if($output=="table"){
$doc = $proc->transformToDoc($xml);
echo $doc->saveHTML();}
else echo  $proc->transformToXML($xml);
}else{
      /*missing xsl lib*/
 	   $rh = fopen($szUrl, 'r');
       header("Content-Type: text/xml");
	   header("Cache-Control: no-store, no-cache, must-revalidate");
       fpassthru($rh);
       fclose($rh);
}
?>

