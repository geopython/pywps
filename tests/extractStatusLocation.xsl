<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  
  

  


  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>
      extractStatusLocation.xsl on ZOOWPSImplementationReport – Attachment
     – ZOO Project Trac
    </title>
        <link rel="search" href="/trac/search" />
        <link rel="help" href="/trac/wiki/TracGuide" />
        <link rel="alternate" href="/trac/raw-attachment/wiki/ZOOWPSImplementationReport/extractStatusLocation.xsl" type="application/xsl+xml; charset=utf-8" title="Original Format" />
        <link rel="up" href="/trac/wiki/ZOOWPSImplementationReport" title="ZOOWPSImplementationReport" />
        <link rel="start" href="/trac/wiki" />
        <link rel="stylesheet" href="/trac/chrome/common/css/trac.css" type="text/css" /><link rel="stylesheet" href="/trac/chrome/common/css/code.css" type="text/css" />
        <link rel="shortcut icon" href="http://svn.zoo-project.org/favicon.ico" type="image/x-icon" />
        <link rel="icon" href="http://svn.zoo-project.org/favicon.ico" type="image/x-icon" />
      <link type="application/opensearchdescription+xml" rel="search" href="/trac/search/opensearch" title="Search ZOO Project Trac" />
    <script type="text/javascript" src="/trac/chrome/common/js/jquery.js"></script><script type="text/javascript" src="/trac/chrome/common/js/trac.js"></script><script type="text/javascript" src="/trac/chrome/common/js/search.js"></script><script type="text/javascript" src="/trac/chrome/tracsectionedit/js/tracsectionedit.js"></script>
    <!--[if lt IE 7]>
    <script type="text/javascript" src="/trac/chrome/common/js/ie_pre7_hacks.js"></script>
    <![endif]-->
    <script type="text/javascript" src="/trac/chrome/common/js/folding.js"></script><script type="text/javascript">
        jQuery(document).ready(function($) {
          $('#preview table.code').enableCollapsibleColumns($('#preview table.code thead th.content'));
        });
      </script>
    <link rel="stylesheet" type="text/css" href="/trac/chrome/site/default.css" />
    <link rel="stylesheet" type="text/css" href="/trac/chrome/site/menu.css" />
    <link rel="stylesheet" type="text/css" href="/trac/chrome/site/menut.css" />
  </head>
  <body>
  <div id="logo">
    <a href="http://svn.zoo-project.org/trac/">
    <img src="/trac/chrome/site/images/hdr.png" /><br /> <br />
    </a>
    <!-- <h1><a href="${chrome.logo.link}">${project.descr or project.description}</a></h1>
    -->
     <h1>Open WPS Platform</h1>
  </div>
  <div id="header">
    <div id="menu">
      <ul class="topnav">
      <li class="default"><a href="/">Home</a></li>
      <li class="default first active"><a href="/trac/wiki">Wiki</a></li><li class="default "><a href="/trac/timeline">Timeline</a></li><li class="default "><a href="/trac/roadmap">Roadmap</a></li><li class="default "><a href="/trac/browser">Browse Source</a></li><li class="default "><a href="/trac/report">View Tickets</a></li><li class="default last"><a href="/trac/search">Search</a></li>
    </ul>
    </div>
  </div>
 <div id="wrapper">
<!-- start page -->
<div id="page">
    <div id="content">
      <div class="post">
    <div id="content" class="attachment">
        <h1><a href="/trac/wiki/ZOOWPSImplementationReport">ZOOWPSImplementationReport</a>: extractStatusLocation.xsl</h1>
        <table id="info" summary="Description">
          <tbody>
            <tr>
              <th scope="col">File extractStatusLocation.xsl,
                <span title="435 bytes">435 bytes</span>
                (added by djay,  <a class="timeline" href="/trac/timeline?from=2010-09-19T20%3A48%3A39%2B02%3A00&amp;precision=second" title="2010-09-19T20:48:39+02:00 in Timeline">2 days</a> ago)</th>
            </tr>
            <tr>
              <td class="message searchable">
                <p>
extractStatusLocation.xsl XSL file used to extract the attribute statusLocation from a wps:ExecuteResponse document
</p>

              </td>
            </tr>
          </tbody>
        </table>
        <div id="preview" class="searchable">
          
  <table class="code"><thead><tr><th class="lineno" title="Line numbers">Line</th><th class="content"> </th></tr></thead><tbody><tr><th id="L1"><a href="#L1">1</a></th><td>&lt;?xml version="1.0"  encoding="UTF-8"?&gt;</td></tr><tr><th id="L2"><a href="#L2">2</a></th><td></td></tr><tr><th id="L3"><a href="#L3">3</a></th><td>&lt;xsl:stylesheet version="1.0"</td></tr><tr><th id="L4"><a href="#L4">4</a></th><td>                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"</td></tr><tr><th id="L5"><a href="#L5">5</a></th><td>                xmlns:ows="http://www.opengis.net/ows/1.1"</td></tr><tr><th id="L6"><a href="#L6">6</a></th><td>                xmlns:wps="http://www.opengis.net/wps/1.0.0"</td></tr><tr><th id="L7"><a href="#L7">7</a></th><td>                xmlns:xlink="http://www.w3.org/1999/xlink"&gt;</td></tr><tr><th id="L8"><a href="#L8">8</a></th><td></td></tr><tr><th id="L9"><a href="#L9">9</a></th><td>  &lt;xsl:output method="text"/&gt;</td></tr><tr><th id="L10"><a href="#L10">10</a></th><td></td></tr><tr><th id="L11"><a href="#L11">11</a></th><td>  &lt;xsl:template match="wps:ExecuteResponse"&gt;</td></tr><tr><th id="L12"><a href="#L12">12</a></th><td>    &lt;xsl:value-of select="@statusLocation" /&gt;</td></tr><tr><th id="L13"><a href="#L13">13</a></th><td>  &lt;/xsl:template&gt; </td></tr><tr><th id="L14"><a href="#L14">14</a></th><td></td></tr><tr><th id="L15"><a href="#L15">15</a></th><td>&lt;/xsl:stylesheet&gt;</td></tr></tbody></table>

        </div>
    </div>
    <div id="altlinks">
      <h3>Download in other formats:</h3>
      <ul>
        <li class="last first">
          <a rel="nofollow" href="/trac/raw-attachment/wiki/ZOOWPSImplementationReport/extractStatusLocation.xsl">Original Format</a>
        </li>
      </ul>
    </div>
      </div>
    </div>
  <div id="sidebar">
    <ul>
	<li id="search_li">
          <h2>Search</h2>
     <form action="/trac/search" method="get">
        <fieldset>
         <input type="text" id="proj-search" name="q" size="18" value="" />
          <input type="submit" value="Search" />
        </fieldset>
      </form>
	</li>
	<li>
	  <h2>Context Navigation</h2>
          <ul>
              <li><a href="/trac/wiki/ZOOWPSImplementationReport">Back to ZOOWPSImplementationReport</a></li>
          </ul>
	</li>
	<li>
	  <h2>Main Navigation</h2>
       	<ul>
      <li><a href="/trac/login">Login</a></li><li><a href="/trac/wiki/TracGuide">Help/Guide</a></li><li><a href="/trac/about">About Trac</a></li><li><a href="/trac/register">Register</a></li><li><a href="/trac/reset_password">Forgot your password?</a></li><li><a href="/trac/prefs">Preferences</a></li>
    </ul>
	</li>
     </ul>
    </div>
    	<!-- end sidebar -->
	<div style="clear: both;"> </div>
</div>
</div>
    <div id="footer">
      	<div id="innerfooter">
	<div class="tribe">
	 <h2>ZOO is proudly sponsored by:</h2>
	      <a href="http://www.geolabs.fr"><img src="/trac/chrome/site/img/geolabs-logo.png" /></a>
	    <a href="http://www.3liz.com"><img src="/trac/chrome/site/img/3liz-logo.png" /></a>
	       <a href="http://www.neogeo-online.net/"><img src="/trac/chrome/site/img/neogeo-logo.png" /></a>
	                <a href="http://www.apptec.co.jp/"><img src="/trac/chrome/site/img/apptech-logo.png" /></a>
		   <a href="http://www.gatewaygeomatics.com/"><img src="/trac/chrome/site/img/gateway-logo.png" /></a>
		     </div>
		       <div class="know-partners">
		        <h2>ZOO Knowledge Partners:</h2>
			<center>
			<a href="http://www.osaka-cu.ac.jp/index-e.html"><img src="/trac/chrome/site/img/ocu-logo.png" /></a>
			<a href="http://www.gucas.ac.cn/gscasenglish/index.aspx"><img src="/trac/chrome/site/img/gucas-logo.png" /></a>
			</center>
			 </div>
			 <p id="legal">© copyright 2009 - 2010 - <a href="http://www.zoo-project.org">ZOO Project</a> - All Rights Reserved. </p>
			 </div>
    </div>
  </body>
</html>