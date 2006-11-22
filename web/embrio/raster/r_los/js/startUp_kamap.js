/**********************************************************************
 * 
 * purpose: init sequence for DHTML interface
 *
 * authors: Luca Casagrande (...) and Lorenzo Becchi (lorenzo@ominiverdi.com)
 *
 * TODO:
 *   - a lot...
 * 
 **********************************************************************
 *
 * Copyright (C) 2006 ominiverdi.org
 *  
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *  
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 **********************************************************************/



//MAP variables
var outimg;
var map_extent;
var height_extent;
var distance_extent;
var input_x=null;
var input_y=null;

//ajax call vars
var image_url;
var xml_dump;

//MODULE VARS
var module_path = 'mod/mod_r_los.php';
var identifier = 'visibility2';//Identifier name for WPS service
var wpsCache = '/home/doktoreas/pywps.ominiverdi.org/subversion/trunk/web/tmp/';


//interface vars
var steps = 6;

//WPS manager
var wpsManager;

function runPywps(){
	if(input_x==null){
		alert('click on map for coords first');
		return;
	}
	var maxdistSel = getRawObject('maxdist');
	var maxdist= maxdistSel.options	[maxdistSel.selectedIndex].value;
	var observerSel = getRawObject('observer');
	var observer = observerSel.options[observerSel.selectedIndex].value;
	//var url = 'mod/r_los.php?xvalue='+input_x+'&yvalue='+input_y+'&maxdist='+maxdist+'&observer='+observer;
	
	//WPSMANAGER part
	var map = myKaMap.getCurrentMap();	
	var extents = map.currentExtents;
	var datainputs = 'x,'+input_x+',y,'+input_y+',maxdist,'+maxdist+',observer,'+observer;
	wpsManager.setWpsCache(wpsCache);
	wpsManager.query(map.name,extents,identifier,datainputs);
	//WPSMANAGER part end
	
	//to be deleted once WPS MANAGER works
	var url = module_path+'?xvalue='+input_x+'&yvalue='+input_y+'&maxdist='+maxdist+'&observer='+observer;
	waitStart();
	call(url, this, parsePywpsOut);
	//to be deleted once WPS MANAGER works END
}

function parsePywpsOut (szInit){
	
	if (szInit.substr(0, 1) != "/") {
        alert(szInit);
        return false;
    }

    eval(szInit);
	getRawObject('console').innerHTML = xml_dump.replace(/\+/g," ");
	getRawObject('outimg').src = image_url;
	getRawObject('outimg').onload = waitEnd;
}


function setFields(gX,gY){
        //set input objects
        input_x = parseInt(gX);
        //getRawObject('xvalue').value = input_x;
        getRawObject('xvalue_span').innerHTML = input_x;
        input_y = parseInt(gY);
        //getRawObject('yvalue').value = input_y;
        getRawObject('yvalue_span').innerHTML = input_y;
}



//trasform coords from image pixel space to map geo space
function waitStart  (){
	var parent = getRawObject('output');
	var wait = getRawObject('wait');
	if( wait)wait.parentNode.removeChild(wait);
	var div = document.createElement('div');
	div.id = 'wait';
	div.innerHTML ='Processing... please wait';
	parent.insertBefore(div,parent.firstChild);
}

//trasform coords from image pixel space to map geo space
function waitEnd(){
	var wait = getRawObject('wait');
	if( wait)wait.parentNode.removeChild(wait);
}
