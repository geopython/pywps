//javascript for xsearch
function submit_search(search_query,oMap)
{
    if (search_query.length <= 0){
    alert("Input search string!");
    }
    if (search_query.length > 0)
    {
        var agt = navigator.userAgent.toLowerCase();
        var is_ie = (agt.indexOf('msie') != -1);
        var is_ie5 = (agt.indexOf('msie 5') != -1);
       
        element = document.getElementById ('searchres');
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

        xmlhttp.open('GET', "tools/search/xsearch.php?xmlRequest=true&map="+oMap.getCurrentMap().name+"&searchstring="+searchstring, true);
        xmlhttp.send(null);
    }
}
