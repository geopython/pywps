<?php
/**********************************************************************
 *
 * $Id: reproj.php,v 1.1 2006/06/14 14:18:53 lbecchi Exp $
 *
 * purpose: This simple php script is used to reprojec point!! 
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

error_reporting(E_ALL);
if (!extension_loaded('MapScript'))
{
    dl( "php_mapscript.so" );
}
//$pp=array();
//$p=array();
//$p[0]=11.5;
//$p[1]=43.7;
//$pp[]=$p;
//
//$r=new reproj($pp,"4236");
//$s=$r->cs2cs("26591");
//print_r($s);

class reproj {
var $aPoints;
var $srsProj;
var $toProj;
function reproj($pointsArray,$epsg){
		/*expected an array with an array point x,y)*/
		foreach($pointsArray as $val){
			$point=ms_newPointObj();
			//print_r($val);
			$point->setXY($val[0],$val[1]);
			$this->aPoints[]=$point;
		}
		$this->srsProj=ms_newProjectionObj("init=epsg:$epsg");
		
}
function cs2cs($to_epsg){
		$this->toProj=ms_newProjectionObj("init=epsg:$to_epsg");
		$points= array();
		foreach($this->aPoints as $val){
			$val->project($this->srsProj,$this->toProj);
		}
		return $this->aPoints;
}
	
	
}
	
















?>