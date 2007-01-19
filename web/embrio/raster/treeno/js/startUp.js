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

window.onload=startUp;


// Global variables
var isCSS, isW3C, isIE4, isNN4;


//MAP variables
var outimg;
var map_extent;
var raster = 'luca.buho';

//ajax call vars
var image_url;
var xml_dump;

//MODULE NAME
var module_path = 'mod/mod_treeno.php';

//interface vars
var steps = 6;

function startUp(){
	initDHTMLAPI();
	//set img object
	outimg = document.getElementById('outimg');
	outimg.onmousedown = getCoords;
	//get params
	map_extent = document.getElementById('map_extent').value;
	map_extent = map_extent.split(',');
	
	//set button event
	getRawObject('go').onclick = runPywps;
}


function runPywps(){
	//var url = 'mod/r_los.php?xvalue='+input_x+'&yvalue='+input_y+'&maxdist='+maxdist+'&observer='+observer;
	var url = module_path+'?raster='+raster;
	waitStart();
	call(url, this, parsePywpsOut);
}

function parsePywpsOut (szInit){
	
	if (szInit.substr(0, 1) != "/") {
        alert(szInit);
        return false;
    }

    eval(szInit);
	//getRawObject('console').innerHTML = xml_dump.replace(/\+/g," ");
	getRawObject('outimg').src = image_url;
	getRawObject('outimg').onload = waitEnd;
}
function getCoords (e){
	e = (e)?e:((event)?event:null);
    if (e.button==2) {
        return;
    } else {
        var x = e.pageX || (e.clientX +
             (document.documentElement.scrollLeft || document.body.scrollLeft));
        var y = e.pageY || (e.clientY +
             (document.documentElement.scrollTop || document.body.scrollTop));
        setFields(x,y);
        e.cancelBubble = true;
        e.returnValue = false;
        if (e.stopPropogation) e.stopPropogation();
        if (e.preventDefault) e.preventDefault();
        return false;
	}
}

function setFields(pX,pY){
	var gCoords = pix2geo(pX,pY);
	//set input objects
	input_x = gCoords[0];
	getRawObject('xvalue').value = input_x;
	getRawObject('xvalue_span').innerHTML = input_x;
	input_y = gCoords[1];	
	getRawObject('yvalue').value = input_y;
	getRawObject('yvalue_span').innerHTML = input_y;
}

function pix2geo (pX,pY){
	var minX = map_extent[0];
	var minY = map_extent[3];
	var maxX = map_extent[2];
	var maxY = map_extent[1];
	var dX = maxX - minX;
	var dY = maxY - minY;
	var imgW = getObjectWidth('outimg');
	var imgH = getObjectHeight('outimg');
	//(gX-minX):pX=dX:imgW;
	//alert(dX + ' ' + dY);

	var gX = parseInt(minX) + pX * dX/imgW;
    var gY = parseInt(minY) + pY * dY/imgH;
    gX = parseInt(gX);
    gY = parseInt(gY);
return [gX, gY];
    
	
}

// DHTML STUFF
// initialize upon load to let all browsers establish content objects
function initDHTMLAPI() {
    if (document.images) {
        isCSS = (document.body && document.body.style) ? true : false;
        isW3C = (isCSS && document.getElementById) ? true : false;
        isIE4 = (isCSS && document.all) ? true : false;
        isNN4 = (document.layers) ? true : false;
        isIE6CSS = (document.compatMode && document.compatMode.indexOf("CSS1") >= 0) ? true : false;
    }
}
// Retrieve the rendered width of an element
function getObjectWidth(obj)  {
    var elem = getRawObject(obj);
    var result = 0;
    if (elem.offsetWidth) {
        result = elem.offsetWidth;
    } else if (elem.clip && elem.clip.width) {
        result = elem.clip.width;
    } else if (elem.style && elem.style.pixelWidth) {
        result = elem.style.pixelWidth;
    }
    return parseInt(result);
}

// Retrieve the rendered height of an element
function getObjectHeight(obj)  {
    var elem = getRawObject(obj);
    var result = 0;
    if (elem.offsetHeight) {
        result = elem.offsetHeight;
    } else if (elem.clip && elem.clip.height) {
        result = elem.clip.height;
    } else if (elem.style && elem.style.pixelHeight) {
        result = elem.style.pixelHeight;
    }
    return parseInt(result);
}


// Convert object name string or object reference
// into a valid element object reference
function getRawObject(obj) {
    var theObj;
    if (typeof obj == "string") {
        if (isW3C) {
            theObj = document.getElementById(obj);
        } else if (isIE4) {
            theObj = document.all(obj);
        } else if (isNN4) {
            theObj = seekLayer(document, obj);
        }
    } else {
        // pass through object reference
        theObj = obj;
    }
    return theObj;
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
