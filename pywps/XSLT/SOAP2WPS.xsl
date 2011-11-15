<?xml version="1.0" encoding="UTF-8"?>
	<!--
		Author: Author: Jorge de Jesus, http://rsg.pml.ac.uk,jmdj@pml.ac.uk
	-->
	<!-- License: GPL -->
	<!--
		decision tree: if url: reference output else: isComplexData==True
		-ComplexData else: -LiteralData
	-->
	<!-- no BBOX support for now -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1"
	xmlns:fn="http://pywps.wald.intevation.org/functions" version="1.0">
	<xsl:template match="/">
		<!-- Determine the Execute process id -->
		<!--
			It gets the root element and passed the string after ExecuteProcess
		-->
		<!-- Check if its sync or async -->
		<xsl:variable name="async" select="boolean(contains(name(./*),'Async'))" />
		<xsl:variable name="processID" select="substring-after(name(./*),'_')" />
		<!-- default HTTP method  -->
		<xsl:variable name="HTTP_METHOD">GET</xsl:variable>
		<!-- xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  -->
		<!--
			xsi:schemaLocation="http://www.opengis.net/wps/1.0.0
			http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd"
		-->
		<!--  -->
		<!-- Execute element -->
		<xsl:element name="Execute" namespace="http://www.opengis.net/wps/1.0.0">
			<xsl:copy-of
				select="document('')/xsl:stylesheet/namespace::*[name()!='xsl' and name()!='fn']" />
			<xsl:attribute name="service">
        <xsl:value-of select="'WPS'" />
      </xsl:attribute>
			<xsl:attribute name="version">
        <xsl:value-of select="'1.0.0'" />
      </xsl:attribute>
			<!--
				<wps:Execute xmlns:ows="http://www.opengis.net/ows/1.1"
				xmlns:wps="http://www.opengis.net/wps/1.0.0" service="WPS"
				version="1.0.0" >
			-->
			<ows:Identifier>
				<xsl:value-of select="$processID" />
			</ows:Identifier>
			<wps:DataInputs>
				<xsl:for-each select="./*/*">
					<!--Gets all children after /Execute_...-->
					<xsl:choose>
						<!--  URL CASE -->
						<xsl:when
							test="starts-with(./text(),'http://') or starts-with(./text(),'http%3A%2F%2F')">
							<xsl:call-template name="referenceSection">
								<xsl:with-param name="HTTP_METHOD" select="$HTTP_METHOD" />
							</xsl:call-template>
						</xsl:when>
						<!--  ComplexData or LiteraInput -->
						<xsl:otherwise>
							<xsl:choose>
								<!-- ComplexData-->
								<xsl:when test="fn:isComplexData(fn:getCorrectInputID(name(.)))">
									<xsl:call-template name="complexDataSection" />
								</xsl:when>
								<!-- LiteralData -->
								<xsl:otherwise>
									<xsl:call-template name="literalData" />
								</xsl:otherwise>
							</xsl:choose>
							<!-- End of ComplexData LiteralInput if -->
						</xsl:otherwise>
						<!--  End of ComplexData LiteralInput if  -->
					</xsl:choose>
					<!-- URL content or Actual content -->
				</xsl:for-each>
				<!-- end of lopp for each element -->
			</wps:DataInputs>
			<!-- responseform section -->
			<wps:ResponseForm>
				<!-- Response document either sync or async -->
				<xsl:call-template name="responseSection">
					<xsl:with-param name="async" select="$async" />
				</xsl:call-template>
			</wps:ResponseForm>
		</xsl:element>
		<!-- End of execute element root element -->
	</xsl:template>
	<!-- end of main template -->
	<!-- Subtemplate section -->
	<!-- URL reference -->
	<xsl:template name="referenceSection">
		<xsl:param name="HTTP_METHOD" />
		<!--ComplexData URLReference -->
		<wps:Input xmlns:xlink="http://www.w3.org/1999/xlink">
			<ows:Identifier>
				<xsl:value-of select="fn:getCorrectInputID(name(.))" />
			</ows:Identifier>
			<wps:Reference>
				<xsl:attribute name="xlink:href">
          <xsl:value-of select="./text()" />
        </xsl:attribute>
				<xsl:attribute name="method">
          <xsl:value-of select="$HTTP_METHOD" />
        </xsl:attribute>
			</wps:Reference>
		</wps:Input>
	</xsl:template>
	<!-- ComplexData section -->
	<xsl:template name="complexDataSection">
		<wps:Input>
			<ows:Identifier>
				<xsl:value-of select="fn:getCorrectInputID(name(.))" />
			</ows:Identifier>
			<wps:Data>
				<wps:ComplexData>
					<!-- if XML get everything below  xsl:copy-of select="./*"-->
					<!-- if base64 xsl:value-of select="."-->
					<xsl:choose>
						<!--  choose type of complex data XML or string -->
						<xsl:when test="count(./*)&gt;0">
							<xsl:copy-of select="./*" />
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="." />
						</xsl:otherwise>
					</xsl:choose>
				</wps:ComplexData>
			</wps:Data>
		</wps:Input>
	</xsl:template>
	<!-- LiteralData section -->
	<xsl:template name="literalData">
		<wps:Input xmlns:xlink="http://www.w3.org/1999/xlink">
			<ows:Identifier>
				<xsl:value-of select="fn:getCorrectInputID(name(.))" />
			</ows:Identifier>
			<wps:Data>
				<wps:LiteralData>
					<xsl:value-of select="." />
				</wps:LiteralData>
			</wps:Data>
		</wps:Input>
	</xsl:template>
	<!-- response sync or async -->
	<xsl:template name="responseSection">
		<xsl:param name="async" />
		<xsl:element name="ResponseDocument">
			<xsl:attribute name="lineage">
        <xsl:value-of select="'false'" />
      </xsl:attribute>
			<xsl:choose>
				<xsl:when test="$async">
					<xsl:attribute name="storeExecuteResponse">
            <xsl:value-of select="'true'" />
          </xsl:attribute>
					<xsl:attribute name="status">
            <xsl:value-of select="'true'" />
          </xsl:attribute>
				</xsl:when>
				<xsl:otherwise>
					<xsl:attribute name="storeExecuteResponse">
            <xsl:value-of select="'false'" />
          </xsl:attribute>
					<xsl:attribute name="status">
            <xsl:value-of select="'false'" />
          </xsl:attribute>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
		<!--  end of response document -->
	</xsl:template>
</xsl:stylesheet>
