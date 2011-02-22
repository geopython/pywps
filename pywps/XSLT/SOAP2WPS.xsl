<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" 
xmlns:wps="http://www.opengis.net/wps/1.0.0" 
xmlns:ows="http://www.opengis.net/ows/1.1"
xmlns:fn="http://pywps.wald.intevation.org/functions">
  <xsl:template match="/">
    <!-- Determine the Execute process id -->
    <!-- It gets the root element and passed the string after ExecuteProcess-->
    
    <!-- Check if its sync or async -->
    
    <xsl:variable name="async" select="boolean(contains(name(./*),'Async'))"/>
       

    <xsl:variable name="processID" select="substring-after(name(./*),'_')"/>
    <!-- default HTTP method  -->
    <xsl:variable name="HTTP_METHOD">GET</xsl:variable>
    <!-- xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  -->
    <!-- xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd" -->
    <!--  -->

    <!-- Execute element -->
    <xsl:element name="Execute" namespace="http://www.opengis.net/wps/1.0.0">
     <xsl:copy-of select="document('')/xsl:stylesheet/namespace::*[name()!='xsl' and name()!='fn']"/>
    <xsl:attribute name="service"><xsl:value-of select="'WPS'"></xsl:value-of></xsl:attribute>
     <xsl:attribute name="version"><xsl:value-of select="'1.0.0'"></xsl:value-of></xsl:attribute>
     
    
  <!--  <wps:Execute xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:wps="http://www.opengis.net/wps/1.0.0" service="WPS" version="1.0.0" >  --> 
      <ows:Identifier>
        <xsl:value-of select="$processID"/>
      </ows:Identifier>
      <wps:DataInputs>
        <xsl:for-each select="./*/*">
          <!--Gets all children after /Execute_...-->
          <xsl:choose>
            <!-- no BBOX support for now -->
            <xsl:when test="count(./*)&gt;0">
              <!-- ComplexData-->
              <wps:Input>
                <ows:Identifier>
                  <xsl:value-of select="fn:getCorrectInputID(name(.))"/>
                </ows:Identifier>
                <wps:Data>
                  <wps:ComplexData>
                
              <xsl:copy-of select="./*"/> 
             
            
                    <!--embedded XML begins here.xsl:copy-of select=".*" /-->
                    
                    <!--embedded XML ends here.-->
                  </wps:ComplexData>
                </wps:Data>
              </wps:Input>
            </xsl:when>
            <xsl:otherwise>
              <!-- LiteralData or ComplexData Reference-->
              <!-- 2 options Data or ComplexData URL reference -->
              <xsl:choose>
                <xsl:when test="starts-with(./text(),'http://') or starts-with(./text(),'http%3A%2F%2F')">
                  <!--ComplexData URLReference -->
                  <wps:Input xmlns:xlink="http://www.w3.org/1999/xlink">
                    <ows:Identifier>
                      <xsl:value-of select="fn:getCorrectInputID(name(.))"/>
                    </ows:Identifier>
                    <wps:Reference>
                      <xsl:attribute name="xlink:href">
                        <xsl:value-of select="./text()"/>
                      </xsl:attribute>
                      <xsl:attribute name="method">
                        <xsl:value-of select="$HTTP_METHOD"/>
                      </xsl:attribute>
                    </wps:Reference>
                  </wps:Input>
                </xsl:when>
                <xsl:otherwise>
                  <!-- Simple LiteralData -->
                  <wps:Input xmlns:xlink="http://www.w3.org/1999/xlink">
                    <ows:Identifier>
                      <xsl:value-of select="fn:getCorrectInputID(name(.))"/>
                    </ows:Identifier>
                    <wps:Data>
                      <wps:LiteralData>
                        <xsl:value-of select="."/>
                      </wps:LiteralData>
                    </wps:Data>
                  </wps:Input>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:otherwise>
          </xsl:choose>
          <!-- from ComplexData / LiteralData-->
        </xsl:for-each>
      </wps:DataInputs>
      <wps:ResponseForm>
      <!-- Response document either sync or async -->
      <xsl:element name="ResponseDocument">
      <xsl:attribute name="lineage"><xsl:value-of select="'false'"></xsl:value-of></xsl:attribute>
       <xsl:choose>
     <xsl:when test="$async">
     	<xsl:attribute name="storeExecuteResponse"><xsl:value-of select="'true'"></xsl:value-of></xsl:attribute>
        <xsl:attribute name="status"><xsl:value-of select="'true'"></xsl:value-of></xsl:attribute>
     </xsl:when><xsl:otherwise>
        <xsl:attribute name="storeExecuteResponse"><xsl:value-of select="'false'"></xsl:value-of></xsl:attribute>
        <xsl:attribute name="status"><xsl:value-of select="'false'"></xsl:value-of></xsl:attribute>
     </xsl:otherwise>
   </xsl:choose>
      </xsl:element> <!--  end of response document -->

      </wps:ResponseForm>
    </xsl:element><!-- End of execute element -->   
  </xsl:template>
</xsl:stylesheet>