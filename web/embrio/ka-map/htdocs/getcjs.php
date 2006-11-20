<?php
/**********************************************************************
 *
 * $Id: getcjs.php,v 1.8 2006/03/21 18:53:38 pspencer Exp $
 *
 * purpose: compress a javascript file by removing white space and
 *          comments
 *
 * author: Paul Spencer (pspencer@dmsolutions.ca)
 *
 * TODO:
 *
 *   - provide option to replace function names with shorter versions
 *   - handle potential problems in strings (don't do conversions inside
 *     strings)
 *   - test cases
 *
 **********************************************************************
 *
 * Copyright (c) 2005, DM Solutions Group Inc.
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
include( '../include/config.php' );
clearstatcache();
if (!isset($_REQUEST['name']))
{
    echo "alert( 'name not set when requesting compressed javascript file' );";
    exit;
}

ob_start ("ob_gzhandler");
header("Content-type: text/javascript; charset: UTF-8");
header("Cache-Control: must-revalidate");
$days = 30;
$offset = 60 * 60 * 24 * $days; 
$ExpStr = "Expires: " . gmdate("D, d M Y H:i:s", time() + $offset) . " GMT";
header($ExpStr);

$files = explode(',',$_REQUEST['name']);
//TODO: clean $_REQUEST['name']

foreach($files as $file) {
	output_js_file($file);
}
exit;

function output_js_file( $file ) {
	$bCompress = false;
	if (!file_exists($file))
	{
	    echo "alert( 'requested file does not exist: ".$_REQUEST['name']."');";
	    exit;
	}
	if ((isset($_REQUEST['compress']) && $_REQUEST['compress'] != 'no') || !isset($_REQUEST['compress']))
	{
	    /* create the main cache directory if necessary */
	    $szScriptCacheDir = $GLOBALS['szBaseCacheDir']."/scripts";
	    if (!@is_dir($szScriptCacheDir))
	        makeDirs($szScriptCacheDir);

	    //file exists at this point.  Check if the compressed version exists
	    if (isset($_REQUEST['force']) && $_REQUEST['force'] == 'true')
	    {
	        $bCompress = true;
	    }
	    else if (!@file_exists($szScriptCacheDir."/".$file.".cjs"))
	    {
	        $bCompress = true;
	    }
	    else
	    {
	        //if it does exist, check the timestamp file
	        if (!@file_exists( $szScriptCacheDir."/".$file.".ts"))
	        {
	            $bCompress = true;
	        }
	        else
	        {
	            $ts = file_get_contents( $szScriptCacheDir."/".$file.".ts" );
	            if ($ts != filemtime($file))
	            {
	                $bCompress = true;
	            }
	        }
	    }

	    if ($bCompress)
	    {
	        compressJS( $file,  
	                   $szScriptCacheDir."/".$file.".cjs",
	                   $szScriptCacheDir."/".$file.".ts");
	    }

	    $h = fopen($szScriptCacheDir."/".$file.".cjs", "r");
	}
	else
	{
	    $h = fopen($file, "r" );
	}
	fpassthru($h);
	fclose($h);
}

function compressJS( $szJSfile, $szCJSfile, $szTSfile )
{
	$szContents = @file_get_contents($szJSfile);
    
    $aSearch = array('/\/\/.*/', // c++ style comments - //something
                     '/\/\*.*\*\//sU', // c style comments - /* something */
                     '/\s{2,}/s', //2 or more spaces down to one space
                     '/\n/', //newlines removed
                     '/\s=/', //space =
                     '/=\s/', // = space
                     );
    
    $aReplace = array( '',
                       '',
                       ' ',
                       '',
                       '=',
                       '=',
                       
                      );
    //remove c++ comments
    $szContents = preg_replace( $aSearch, $aReplace, $szContents );
    makeDirs(dirname($szCJSfile));
    $fh = fopen($szCJSfile, "w");
    fwrite( $fh, $szContents);
    fclose($fh);
    $ts = filemtime($szJSfile);
    $fh = fopen($szTSfile, "w");
    fwrite($fh, $ts);
    fclose($fh);
}
?>
