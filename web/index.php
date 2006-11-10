<html>
<head>
<title>Embrio: A new way to see through the GRASS (by doktoreas and ominiverdi) </title>
<style type="text/css">
body {
	margin:0;
	padding:0;
}
#header {
	background: #999 url("pywps.png") no-repeat 98% 5px ;
	height:120px;
	color:white;
	padding:0;
	margin:0;
}
h1{
	margin:0;
	padding:20px;
}
h2{
	background-color:rgb(200,200,200);
	margin:0;
	padding:10px;
}
a
{
	color: #559900;
	font-weight: bold;
	text-decoration: none;
	background-color: inherit;
}

a:hover
{
	color: #336600;
	text-decoration: none;
	background-color: inherit;
}
div#footer {
    padding: 5px;
    margin-top: 20px;
    color: #fff;
    background: #999;
}
div#footer a{
    color: #99Ff33;
}
div#footer a:hover {
	color: #99ff66;
}
#content {
	margin:10px;
}
#application {
	margin:10px;
	margin-left:20px;
	margin-right:20px;
}
.original {
	font-size:0.9em;
	font-style:italic;
	margin:2px;
	margin-left:30px;
	padding:0;
}


</style>
</head>
<body>
<div id="header"><h1>EMBRIO - a simple PyWPS AJAX Web Interface</h1>
</div>
<div id="content">
<p>This 
page is intended 
to show the development status of a<strong> Web User Interface 
</strong>for 
<a href="http://pywps.wald.intevation.org/index.psp" target="_blank">PyWPS</a></p>
</div>
<h2>Demo applications</h2>
<div class="subcontent">
<ul>
<li><a href="embrio/vector/v_buff/v_buff.php">V.Buffer</a> - Create a buffer around 
features of given type (areas must contain centroid).</li>
<li><a href="embrio/raster/r_los/r_los.php">R.Los</a> - Generates a raster map output in which the cells that are visible from a user-specified observer location are marked with integer values that represent the vertical angle (in degrees) required to see those cells (viewshed)..</li>
<li><a href="embrio/vector/v_net_path/v_net_path.php">V.Net.Path</a> - Find shortest path on vector network.</li>
</ul>
</div>
<h2>Developers</h2>
<div class="subcontent">
<ul>
<li><strong>doktoreas</strong></li>
<li><strong>ominiverdi</strong></li>
<!--<li><strong>kappu</strong></li>-->
</ul>
</div>
<h2>Used technologies</h2>
<div class=subcontent">
<ul>
<li>AJAX</li>
<li>PHP/MAPSCRIPT</li>
<li>PyWPS</li>
<li>GRASS</li>
</ul>
</div>
<h2>Links</h2>
<div class="subcontent">
<ul>
<li><a href="https://wald.intevation.org/projects/pywps/" target="_blank">PyWPS community site</a></li>
<li><a href="http://grass.itc.it/" target="_blank">GRASS official Site</a></li>
<li><a href="http://www.maptools.org/php_mapscript/" target="_blank">PHP/Mapscript</a></li>
 </ul>
<div id="footer"><ul>
<li>hosted by: <a href="http://www.ominiverdi.org">ominiverdi.org</a></li>
</ul>
</div>

</body>
</html>

