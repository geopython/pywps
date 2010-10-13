<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:template match="/">
		<!-- Getting Identifier and concerning it -->
		<xsl:variable name="identifier" select="//*[local-name() = 'Identifier']"/>
		<xsl:variable name="identifierSOAP" select="concat('ExecuteProcess_',$identifier,'Response')"/>
	<xsl:value-of select="$identifierSOAP"></xsl:value-of>
	<xsl:element name="{$identifierSOAP}">
		<xsl:for-each select="//*[local-name()='Output']">
			
			<xsl:choose>
			<xsl:when test="count(./*/*[local-name()='LiteralData'])>0"> <!--LiteralData type -->
				<xsl:variable name="literalIdentifier" select="concat(./*[local-name()='Identifier']/text(),'Result')"/>
				<xsl:element name="{$literalIdentifier}"><xsl:value-of select="./*/*[local-name()='LiteralData']/text()"/></xsl:element>			
			</xsl:when>
			<xsl:otherwise> <!--  ComplexData -->
			<xsl:variable name="complexIdentifier" select="concat(./*[local-name()='Identifier']/text(),'Result')"/>
			  <!--ComplexData may contain XML or string -->
			  <xsl:choose>
			  <xsl:when test="./*/*/*">
			  	<xsl:element name="{$complexIdentifier}"><xsl:copy-of select="./*/*/*" /></xsl:element>
			  </xsl:when>
			  <xsl:otherwise test="./*/*/text()">
			    <xsl:element name="{$complexIdentifier}"><xsl:value-of select="./*/*/text()" /></xsl:element>
			  </xsl:otherwise>
			  </xsl:choose> <!-- End of complexData type choose -->
			  
			</xsl:otherwise>
			</xsl:choose> <!-- end of literal complexdata choose -->
		
		</xsl:for-each> <!--  end of Outoput output-->
	
	</xsl:element> <!-- end of ExecuteProcess_fooResponse -->	
	</xsl:template>
</xsl:stylesheet>