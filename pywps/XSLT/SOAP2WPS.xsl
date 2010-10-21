<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="/">
    <!-- Determine the Execute process id -->
    <!-- It gets the root element and passed the string after ExecuteProcess-->
    <!-- PROBLEM: Namespaces in the WPS:Execute aren't passed to ComplexData (mainly OWS and WPS) -->
    <!-- xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" -->
   <!--  xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd" -->
    <!-- xmlns:ows="http://www.opengis.net/ows/1.1" -->
    <!-- xmlns:wps="http://www.opengis.net/wps/1.0.0" -->
    <xsl:variable name="processID" select="substring-after(name(./*),'ExecuteProcess_')"/>
    <xsl:variable name="HTTP_METHOD">GET</xsl:variable>
    <wps:Execute  xmlns:ows="http://REPLACEME/ows/1.1" xmlns:wps="http://REPLACEME/wps/1.0.0" service="WPS" version="1.0.0">
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
                  <xsl:value-of select="name(.)"/>
                </ows:Identifier>
                <wps:Data>
                  <wps:ComplexData>
                    <!--embedded XML begins here.-->
                    
                    <xsl:copy-of select="./*" />
                   
                 
                    
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
                      <xsl:value-of select="name(.)"/>
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
                      <xsl:value-of select="name(.)"/>
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
        <wps:ResponseDocument lineage="false">
        </wps:ResponseDocument>
      </wps:ResponseForm>
    </wps:Execute>
  </xsl:template>
  
</xsl:stylesheet>