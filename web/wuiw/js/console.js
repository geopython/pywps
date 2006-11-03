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
function console(objId)
 {
    this.id= objId;
    this.obj= getRawObject(objId);

 };

console.prototype.echo = function (text){
	 this.obj.innerHTML = text;
  
};

console.prototype.echoXML = function (text){
	 this.obj.innerHTML = myurldecode(text);
  
};



function myurlencode(string) {
  encodedHtml = escape(string);
  encodedHtml = encodedHtml.replace(/\//g,"%2F");
  encodedHtml = encodedHtml.replace(/\?/g,"%3F");
  encodedHtml = encodedHtml.replace(/=/g,"%3D");
  encodedHtml = encodedHtml.replace(/&/g,"%26");
  encodedHtml = encodedHtml.replace(/@/g,"%40");
  return encodedHtml;
  } ;

function myurldecode(sz){

	return unescape(sz).replace(/\+/g," ");

};
function trim(text){
	
return text.replace(/^\s*|\s*$/g,"");
}