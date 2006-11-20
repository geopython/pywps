<?xml version="1.0" encoding="UTF-8"?>
<html xsl:version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">
<head>
<link rel="stylesheet" type="text/css" href="table.css"></link>
</head>
  <body >
<div id="main">
    <xsl:for-each select="query/layer">
      <div class="layer">
      <table>
      <caption>   
      Layer: <span style="font-weight:bold;color:white">
        <xsl:value-of select="name"/></span>
       Group:<span style="font-weight:bold;color:white">
        <xsl:value-of select="group"/></span>
   	</caption>   
 	  <thead>
 	  <tr><th><img src="../../images/icon_set_nomad/tool_zoomin_1.png" /></th>		  
      <xsl:for-each select="fields/field">
      <xsl:choose>
          <xsl:when test='alias=""'>
            <th><xsl:value-of select='name'/></th>
          </xsl:when>
          <xsl:otherwise>
           	<th><xsl:value-of select="alias"/></th>
          </xsl:otherwise>
        </xsl:choose>
        
      </xsl:for-each>
     </tr>	
 	   </thead>
     <tbody>
 	 <xsl:for-each select="records/rec">
 	  <tr>
      	<td>
 	   <img src="../../images/icon_set_nomad/tool_zoomin_1.png">
        <xsl:attribute name="onclick">
        window.opener.document.getElementById("qKamap").qM.zoomToSelected(<xsl:value-of select="translate(ext,' ',',')"/>);
        </xsl:attribute>
        <xsl:attribute name="onmouseover">this.style.cursor="pointer";</xsl:attribute>
        <xsl:attribute name="title">Zoom to selected!</xsl:attribute>
      	</img>
      	</td>
      	 <xsl:for-each select="val">
      	 <xsl:choose>
         	<xsl:when test='contains(.,"http://")'>
      	   	<td><a><xsl:attribute name="href"><xsl:value-of select="." /></xsl:attribute>Link
      	   </a></td>
         </xsl:when>
         <xsl:otherwise>
         	<td><span><xsl:value-of select="." /> </span></td>
          </xsl:otherwise>
        </xsl:choose>
        
      	</xsl:for-each>  
     </tr>
     </xsl:for-each>   	
     
     </tbody>
 	 
 	  
	  </table>	      
      </div>
    </xsl:for-each>
    </div>
  </body>

</html>