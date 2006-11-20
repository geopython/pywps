/**********************************************************************
 *
 * $Id: kaSearch.js,v 1.2 2006/08/08 20:50:41 lbecchi Exp $
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

/******************************************************************************
 * kaSearch - 
 *
 * To use kaSearch:
 * 
 * 1) add a script tag to your page:
 * 
 *   <script type="text/javascript" src="tools/kaSearch.js"></script>
 * 
 * 2) create a new instance of kaSearch
 * 
 *   var toolTip = new kaSearch( oMap);
 * 
 * 
 *
 * 
 *
 *****************************************************************************/
 
 function kaSearch( oKaMap ){
    this.kaMap = oKaMap;
    
    this.image = null;

    this.domObj = null;
    
    this.tooltip = new kaToolTip(oKaMap);
    
    
    this.init();


 };
 

kaSearch.prototype.init = function(){

	this.tooltip.setTipImage('images/tip-yellow.png',-6,-19);

};


kaSearch.prototype.search=function(search_query){
    if (search_query.length <= 0){
    alert("Input search string!");
    }
    if (search_query.length > 0)
    {
        var agt = navigator.userAgent.toLowerCase();
        var is_ie = (agt.indexOf('msie') != -1);
        var is_ie5 = (agt.indexOf('msie 5') != -1);
       
        element = document.getElementById ('searchres');
        element.innerHTML = "<h3>Processing search.<br>Please wait...</h3><hr>";
        element.className = "visible";
        function handle_do_search ()
        {
            if (xmlhttp.readyState == 4)//request completed
            {
                if (xmlhttp.status == 200)//request successful
                {
                    element.innerHTML = xmlhttp.responseText;
                }
                else
                {
                    alert ('No server answer!');
                }
            }
        }
       
        var xmlhttp = null;
        if (is_ie)
        {
            var control = (is_ie5) ? "Microsoft.XMLHTTP" : "Msxml2.XMLHTTP";
            try
            {
                xmlhttp = new ActiveXObject(control);
                xmlhttp.onreadystatechange = handle_do_search;
            } catch(e)
            {
                alert("You need to enable active scripting and activeX controls");
            }
        }
        else
        {
            xmlhttp = new XMLHttpRequest();
            xmlhttp.onload = handle_do_search;
            xmlhttp.onerror = handle_do_search;
        }
        //call for xsearch.php results - sending link
        searchstring=encodeURIComponent(search_query);// encoding searchstring for link

        xmlhttp.open('GET', "tools/search/kaSearch.php?xmlRequest=true&map="+this.kaMap.getCurrentMap().name+"&searchstring="+searchstring, true);
        xmlhttp.send(null);
    }

};
