<?xml version="1.0" encoding="UTF-8"?>
	<!--
		Author: Author: Jorge de Jesus, http://rsg.pml.ac.uk,jmdj@pml.ac.uk
	-->
	<!-- License: GPL -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:fn="http://pywps.wald.intevation.org/functions" version="1.0">
	<xsl:template match="/">
		<!--
			Either the response is a processAccepted (async) or ProcessSucceeded
			(sync or final result from async)
		-->
		<!-- <wps:ProcessAccepted> then we have an async call -->
		<xsl:variable name="async"
			select="boolean(//*[local-name()='ProcessAccepted'])" />
		<xsl:variable name="identifier" select="//*[local-name() = 'Identifier']" />
		<xsl:variable name="identifierSOAP">
			<xsl:choose>
				<xsl:when test="$async">
					<xsl:value-of
						select="concat('ExecuteProcessAsync_',$identifier,'Response')" />
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="concat('ExecuteProcess_',$identifier,'Response')" />
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<xsl:element name="{$identifierSOAP}">
			<xsl:choose>
				<xsl:when test="$async">
					<!-- statusURL reply -->
					<xsl:element name="statusURLResult">
						<xsl:value-of
							select="//*[local-name()='ExecuteResponse']/@statusLocation" />
					</xsl:element>
				</xsl:when>
				<xsl:otherwise>
					<xsl:for-each select="//*[local-name()='Output']">
						<xsl:choose>
							<xsl:when test="count(./*/*[local-name()='LiteralData'])&gt;0">
								<!--LiteralData type -->
								<xsl:variable name="literalIdentifier"
									select="concat(fn:flagRemover(string(./*[local-name()='Identifier']/text())),'Result')" />
								<xsl:element name="{$literalIdentifier}">
									<xsl:value-of select="./*/*[local-name()='LiteralData']/text()" />
								</xsl:element>
							</xsl:when>
							<xsl:otherwise>
								<!--  ComplexData -->
								<!-- ATTENTION THE LITERALDATA AS REFERENCE WILL OUTPUT FROM HERE, NOT ELEGANT :( -->
								<xsl:variable name="complexIdentifier"
									select="concat(fn:flagRemover(string(./*[local-name()='Identifier']/text())),'Result')" />
								<!--ComplexData may contain XML or string -->
								<xsl:choose>
									<xsl:when test="./*/*/*">
										<xsl:element name="{$complexIdentifier}">
											<xsl:copy-of select="./*/*/*" />
										</xsl:element>
									</xsl:when>
									<xsl:otherwise>
										
										<xsl:element name="{$complexIdentifier}">
											<!-- 2 Posibilities content or reference -->
											<xsl:choose>
												<xsl:when test="./*[local-name()='Reference']/@href">
													<xsl:value-of select="./*[local-name()='Reference']/@href" />
													</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="./*/*/text()" />
												</xsl:otherwise>
											</xsl:choose>
										</xsl:element>
									</xsl:otherwise>
								</xsl:choose>
								<!-- End of complexData type choose -->
							</xsl:otherwise>
						</xsl:choose>
						<!-- end of literal complexdata choose -->
					</xsl:for-each>
					<!--  end of Outoput output-->
				</xsl:otherwise>
				<!-- end of sync option -->
			</xsl:choose>
			<!-- end of async/sync choose -->
		</xsl:element>
		<!-- end of ExecuteProcess_fooResponse -->
	</xsl:template>
</xsl:stylesheet>
