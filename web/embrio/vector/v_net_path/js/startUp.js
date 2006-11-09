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
var height_extent;
var distance_extent;
var input_x=null;
var input_y=null;

//ajax call vars
var image_url;
var xml_dump;


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
	height_extent = document.getElementById('height_extent').value.split(',');
	height_unit = parseInt((height_extent[1]-height_extent[0])/steps*100)/100;
	distance_extent = document.getElementById('distance_extent').value.split(',');
	distance_unit = parseInt((distance_extent[1]-distance_extent[0])/steps*100)/100;
	
	//print ranges
	getRawObject('observer_range').innerHTML = height_extent[0] + ' -&gt; ' + height_extent[1]; 
	getRawObject('maxdist_range').innerHTML = distance_extent[0] + ' -&gt; ' + distance_extent[1]; 
	
	//update selects
	var maxdist = getRawObject('maxdist');
	var observer = getRawObject('observer');
	var height = parseInt(height_extent[0]);
	var distance = parseInt(distance_extent[0]);
    for(i=0;i<=steps;i++) {
        if(i==steps){
			height = parseInt(height_extent[1]);
			distance = parseInt(distance_extent[1]);
			maxdist[i] = new Option(distance,distance,false,false);
			observer[i] = new Option(height,height,false,false);
		} else{  
			maxdist[i] = new Option(distance,distance,false,false);
			observer[i] = new Option(height,height,false,false);
		}
		
		height = parseInt((height + height_unit)*100)/100;
		distance = parseInt(distance + distance_unit);
    }
	
	//set button event
	getRawObject('go').onclick = runPywps;
}


function runPywps(){
	if(input_x==null){
		alert('click on map for coords first');
		return;
	}
	var maxdistSel = getRawObject('maxdist');
	var maxdist= maxdistSel.options	[maxdistSel.selectedIndex].value;
	var observerSel = getRawObject('observer');
	var observer = observerSel.options[observerSel.selectedIndex].value;
	var url = 'mod/r_los.php?xvalue='+input_x+'&yvalue='+input_y+'&maxdist='+maxdist+'&observer='+observer;
	
	call(url, this, parsePywpsOut);
}

function parsePywpsOut (szInit){
	
	if (szInit.substr(0, 1) != "/") {
        alert(szInit);
        return false;
    }

    eval(szInit);
	getRawObject('console').innerHTML = xml_dump.replace(/\+/g," ");
	getRawObject('outimg').src = image_url;
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