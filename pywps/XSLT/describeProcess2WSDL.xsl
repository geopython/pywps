<?xml version="1.0" encoding="UTF-8"?>
	<!--
		Author: Author: Jorge de Jesus, http://rsg.pml.ac.uk,jmdj@pml.ac.uk
	-->
	<!-- License: GPL -->
	<!-- ${workspace_loc:/GetCapabilities2WSDL/getCapabilities.xml} -->
	<!-- REPLACEME == serverURL  and it needs to be done externaly-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:tns="REPLACEME_wsdl" xmlns="http://schemas.xmlsoap.org/wsdl/"
	xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:wps="http://www.opengis.net/wps/1.0.0"
	xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
	xmlns:wsdl="http://schemas.xmlsoap.org/wsdl" xmlns:fn="http://pywps.wald.intevation.org/functions"
	version="1.0">
	<xsl:output method="xml" indent="yes" omit-xml-declaration="no" />
	<!-- External variables passed by Python to the XSLT transformer -->
	<xsl:param name="serverURL" />
	<xsl:param name="serverName" />
	<!-- No longer necessary to set serverURL and serverName -->
	<!--
		<xsl:variable name="serverURL"><xsl:value-of
		select="'http://localhost/wps.cgi'"></xsl:value-of></xsl:variable>
	-->
	<!--
		<xsl:variable name="serverName"><xsl:value-of
		select="'PywpsServer'"></xsl:value-of></xsl:variable>
	-->
	<!--  Example of regex with EXSTL -->
	<!--
		<xsl:attribute name="name"><xsl:value-of
		select="concat(regexp:replace(./*[local-name()='Identifier'],'^[^_:A-Za-z]','g',''),'Result')"></xsl:value-of></xsl:attribute>
	-->
	<xsl:template match="/">
		<xsl:element name="definitions">
			<!--  Hack, the namespaces are copied from the <stylesheet> element -->
			<xsl:copy-of
				select="document('')/xsl:stylesheet/namespace::*[name()!='xsl' and name()!='fn']" />
			<xsl:attribute name="targetNamespace">
        <xsl:value-of select="concat($serverURL,'_wsdl')" />
      </xsl:attribute>
			<xsl:element name="types">
				<!-- Generic WPS support -->
				<!--
					Special type for any sort of XML inside the response, this allows
					for some used of the XMLsplitter in taverna. The xsd: namespace is
					necessary here otherwise the parser will assume wsdl: and will
					crash. Everything we have an undefined dataType the system will use
					this
				-->
				<!--
					<xsd:schema><xsd:complexType name="anyXMLType"
					xmlns="http://www.w3.org/2001/XMLSchema"
					targetNamespace="http://www.opengis.net/wps/1.0.0"> <xsd:sequence>
					<xsd:any namespace="##any" processContents="lax" minOccurs="1"
					maxOccurs="1"></xsd:any> </xsd:sequence>
					</xsd:complexType></xsd:schema>
				-->
				<!-- Exception report -->

				<!-- REMOVED DUE TO OGC RECURSIVE LOOP -->
				<!--

					<xsl:element name="schema"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="targetNamespace"> <xsl:value-of
					select="'http://www.opengis.net/ows/1.1'" /> </xsl:attribute>
					<xsl:element name="include"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="schemaLocation"> <xsl:value-of
					select="'http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd'"
					/> </xsl:attribute> </xsl:element> </xsl:element>
				--><!-- GetCapabilities report -->
				<!-- REMOVED DUE TO OGC RECURSIVE LOOP -->
				<!--
					<xsl:element name="schema"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="targetNamespace"> <xsl:value-of
					select="'http://www.opengis.net/wps/1.0.0'" /> </xsl:attribute>
					<xsl:element name="include"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="schemaLocation"> <xsl:value-of
					select="'http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_request.xsd'"
					/> </xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="schema" namespace="http://www.w3.org/2001/XMLSchema">
					<xsl:attribute name="targetNamespace"> <xsl:value-of
					select="'http://www.opengis.net/wps/1.0.0'" /> </xsl:attribute>
					<xsl:element name="include"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="schemaLocation"> <xsl:value-of
					select="'http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd'"
					/> </xsl:attribute> </xsl:element> </xsl:element>
				-->
				<!-- REMOVED DUE TO OGC RECURSIVE LOOP -->
				<!-- DescribeProcess report -->
				<!--
					<xsl:element name="schema"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="targetNamespace"> <xsl:value-of
					select="'http://www.opengis.net/wps/1.0.0'" /> </xsl:attribute>
					<xsl:element name="include"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="schemaLocation"> <xsl:value-of
					select="'http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_request.xsd'"
					/> </xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="schema" namespace="http://www.w3.org/2001/XMLSchema">
					<xsl:attribute name="targetNamespace"> <xsl:value-of
					select="'http://www.opengis.net/wps/1.0.0'" /> </xsl:attribute>
					<xsl:element name="include"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="schemaLocation"> <xsl:value-of
					select="'http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'"
					/> </xsl:attribute> </xsl:element> </xsl:element>
				-->
				<!-- Execute report -->
				<!-- REMOVED DUE TO OGC RECURSIVE LOOP -->
				<!--
					<xsl:element name="schema"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="targetNamespace"> <xsl:value-of
					select="'http://www.opengis.net/wps/1.0.0'" /> </xsl:attribute>
					<xsl:element name="include"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="schemaLocation"> <xsl:value-of
					select="'http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd'"
					/> </xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="schema" namespace="http://www.w3.org/2001/XMLSchema">
					<xsl:attribute name="targetNamespace"> <xsl:value-of
					select="'http://www.opengis.net/wps/1.0.0'" /> </xsl:attribute>
					<xsl:element name="include"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="schemaLocation"> <xsl:value-of
					select="'http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd'"
					/> </xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="schema" namespace="http://www.w3.org/2001/XMLSchema">
					<xsl:attribute name="targetNamespace"> <xsl:value-of
					select="'http://www.opengis.net/ows/1.1'" /> </xsl:attribute>
					<xsl:element name="include"
					namespace="http://www.w3.org/2001/XMLSchema"> <xsl:attribute
					name="schemaLocation"> <xsl:value-of
					select="'http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd'"
					/> </xsl:attribute> </xsl:element> </xsl:element>
				-->

				<!-- ADDED EXCEPTION DESCRIPTION DUE TO OGC RECURSIVE LOOP -->
				<schema xmlns="http://www.w3.org/2001/XMLSchema"
					targetNamespace="http://www.opengis.net/ows/1.1"
					elementFormDefault="qualified" xmlns:ows="http://www.opengis.net/ows/1.1"
					version="1.1.0 2011-02-07" xml:lang="en">
					<element name="ExceptionReport">
						<annotation>
							<documentation>Report message returned to the client that
								requested any OWS operation when the server detects an error
								while processing that operation request. </documentation>
						</annotation>
						<complexType>
							<sequence>
								<element ref="ows:Exception" maxOccurs="unbounded">
									<annotation>
										<documentation>Unordered list of one or more Exception
											elements that each describes an error. These Exception
											elements shall be interpreted by clients as being independent
											of one another (not hierarchical). </documentation>
									</annotation>
								</element>
							</sequence>
							<attribute name="version" use="required">
								<annotation>
									<documentation>Specification version for OWS operation. The
										string value shall contain one x.y.z "version" value (e.g.,
										"2.1.3"). A version number shall contain three non-negative
										integers separated by decimal points, in the form "x.y.z". The
										integers y and z shall not exceed 99. Each version shall be
										for the Implementation Specification (document) and the
										associated XML Schemas to which requested operations will
										conform. An Implementation Specification version normally
										specifies XML Schemas against which an XML encoded operation
										response must conform and should be validated. See Version
										negotiation subclause for more information. </documentation>
								</annotation>
								<simpleType>
									<restriction base="string">
										<pattern value="\d+\.\d?\d\.\d?\d" />
									</restriction>
								</simpleType>
							</attribute>
							<!-- REMOVED PROBLEMS  WITH SUDS DUE TO LACK OF DEFINITON -->
							<!-- 
							<attribute ref="xml:lang" use="optional">
								<annotation>
									<documentation>Identifier of the language used by all included
										exception text values. These language identifiers shall be as
										specified in IETF RFC 4646. When this attribute is omitted,
										the language used is not identified. </documentation>
								</annotation>
							</attribute>
							 -->
						</complexType>
					</element>
					<!--
						=======================================================
					-->
					<element name="Exception" type="ows:ExceptionType" />
					<!--
						=======================================================
					-->
					<complexType name="ExceptionType">
						<annotation>
							<documentation>An Exception element describes one detected error
								that a server chooses to convey to the client. </documentation>
						</annotation>
						<sequence>
							<element name="ExceptionText" type="string" minOccurs="0"
								maxOccurs="unbounded">
								<annotation>
									<documentation>Ordered sequence of text strings that describe
										this specific exception or error. The contents of these
										strings are left open to definition by each server
										implementation. A server is strongly encouraged to include at
										least one ExceptionText value, to provide more information
										about the detected error than provided by the exceptionCode.
										When included, multiple ExceptionText values shall provide
										hierarchical information about one detected error, with the
										most significant information listed first. </documentation>
								</annotation>
							</element>
						</sequence>
						<attribute name="exceptionCode" type="string" use="required">
							<annotation>
								<documentation>A code representing the type of this exception,
									which shall be selected from a set of exceptionCode values
									specified for the specific service operation and server.
								</documentation>
							</annotation>
						</attribute>
						<attribute name="locator" type="string" use="optional">
							<annotation>
								<documentation>When included, this locator shall indicate to the
									client where an exception was encountered in servicing the
									client's operation request. This locator should be included
									whenever meaningful information can be provided by the server.
									The contents of this locator will depend on the specific
									exceptionCode and OWS service, and shall be specified in the
									OWS Implementation Specification. </documentation>
							</annotation>
						</attribute>
					</complexType>


				</schema>

				<!-- End of General WPS support -->
				<!-- ExecuteProcess support -->
				<!-- loop thru processes and set the xsd types -->
				<xsl:for-each select="//*[local-name()='ProcessDescription']">
					<xsl:call-template name="typeDescribe">
						<xsl:with-param name="async" select="false()" />
						<xsl:with-param name="processID"
							select="concat('ExecuteProcess_',./*[local-name()='Identifier'])" />
					</xsl:call-template>
					<xsl:if
						test="string(./@storeSupported)='true' and string(./@statusSupported)='true'">
						<xsl:call-template name="typeDescribe">
							<xsl:with-param name="async" select="true()" />
							<xsl:with-param name="processID"
								select="concat('ExecuteProcessAsync_',./*[local-name()='Identifier'])" />
						</xsl:call-template>
					</xsl:if>
				</xsl:for-each>
				<!-- End of DescribeProcess loop for types -->
			</xsl:element>
			<!-- End of types element -->
			<!-- message sections -->
			<!-- Default WPS request/response messages -->


			<!-- REMOVED DUE TO OGC RECURSIVE LOOP -->
			<!--
				<xsl:element name="message"> <xsl:attribute name="name">
				<xsl:value-of select="'GetCapabilitiesRequest'" /> </xsl:attribute>
				<xsl:element name="part"> <xsl:attribute name="name"> <xsl:value-of
				select="'msg'" /> </xsl:attribute> <xsl:attribute name="element">
				<xsl:value-of select="'wps:GetCapabilities'" /> </xsl:attribute>
				</xsl:element> </xsl:element> <xsl:element name="message">
				<xsl:attribute name="name"> <xsl:value-of
				select="'GetCapabilitiesResponse'" /> </xsl:attribute> <xsl:element
				name="part"> <xsl:attribute name="name"> <xsl:value-of
				select="'msg'" /> </xsl:attribute> <xsl:attribute name="element">
				<xsl:value-of select="'wps:Capabilities'" /> </xsl:attribute>
				</xsl:element> </xsl:element> <xsl:element name="message">
				<xsl:attribute name="name"> <xsl:value-of
				select="'DescribeProcessRequest'" /> </xsl:attribute> <xsl:element
				name="part"> <xsl:attribute name="name"> <xsl:value-of
				select="'msg'" /> </xsl:attribute> <xsl:attribute name="element">
				<xsl:value-of select="'wps:DescribeProcess'" /> </xsl:attribute>
				</xsl:element> </xsl:element> <xsl:element name="message">
				<xsl:attribute name="name"> <xsl:value-of
				select="'DescribeProcessResponse'" /> </xsl:attribute> <xsl:element
				name="part"> <xsl:attribute name="name"> <xsl:value-of
				select="'msg'" /> </xsl:attribute> <xsl:attribute name="element">
				<xsl:value-of select="'wps:ProcessDescriptions'" /> </xsl:attribute>
				</xsl:element> </xsl:element>
			-->
			<!--
				<xsl:element name="message"> <xsl:attribute name="name">
				<xsl:value-of select="'ExecuteRequest'" /> </xsl:attribute>
				<xsl:element name="part"> <xsl:attribute name="name"> <xsl:value-of
				select="'msg'" /> </xsl:attribute> <xsl:attribute name="element">
				<xsl:value-of select="'wps:Execute'" /> </xsl:attribute>
				</xsl:element> </xsl:element> <xsl:element name="message">
				<xsl:attribute name="name"> <xsl:value-of select="'ExecuteResponse'"
				/> </xsl:attribute> <xsl:element name="part"> <xsl:attribute
				name="name"> <xsl:value-of select="'msg'" /> </xsl:attribute>
				<xsl:attribute name="element"> <xsl:value-of
				select="'wps:ExecuteResponse'" /> </xsl:attribute> </xsl:element>
				</xsl:element> 
				
				-->
				<xsl:element name="message">
	<xsl:attribute name="name"> <xsl:value-of select="'ExceptionResponse'" />
				</xsl:attribute>
	<xsl:element name="part">
		<xsl:attribute name="name"> <xsl:value-of select="'msg'" /> </xsl:attribute>
		<xsl:attribute name="element"> <xsl:value-of select="'ows:Exception'" /> </xsl:attribute>
	</xsl:element>
</xsl:element>
			
			<!-- End of default WPS request/response messages -->
			<!--  Process loop to fetch name -->
			<!--
				Its better to do another loop than one giant loop with everythin
			-->
			<xsl:for-each select="//*[local-name()='ProcessDescription']">
				<xsl:call-template name="messageDescribe">
					<xsl:with-param name="async" select="false()" />
					<xsl:with-param name="processID"
						select="concat('ExecuteProcess_',./*[local-name()='Identifier'])" />
				</xsl:call-template>
				<xsl:if
					test="string(./@storeSupported)='true' and string(./@statusSupported)='true'">
					<xsl:call-template name="messageDescribe">
						<xsl:with-param name="async" select="true()" />
						<xsl:with-param name="processID"
							select="concat('ExecuteProcessAsync_',./*[local-name()='Identifier'])" />
					</xsl:call-template>
				</xsl:if>
			</xsl:for-each>
			<!-- End of process description loop for message -->
			<!-- portType structure  -->
			<xsl:element name="portType">
				<xsl:attribute name="name">
          <xsl:value-of select="concat($serverName,'_PortType')" />
        </xsl:attribute>
				<!-- Loop operations -->
				<!-- General WPS compliance -->

				<!-- REMOVED DUE TO OGC RECURSIVE LOOP -->
				<!--
					<xsl:element name="operation"> <xsl:attribute name="name">
					<xsl:value-of select="'GetCapabilities'" /> </xsl:attribute>
					<xsl:element name="input"> <xsl:attribute name="message">
					<xsl:value-of select="'tns:GetCapabilitiesRequest'" />
					</xsl:attribute> </xsl:element> <xsl:element name="output">
					<xsl:attribute name="message"> <xsl:value-of
					select="'tns:GetCapabilitiesResponse'" /> </xsl:attribute>
					</xsl:element> <xsl:element name="fault"> <xsl:attribute
					name="name"> <xsl:value-of select="'ExceptionResponse'" />
					</xsl:attribute> <xsl:attribute name="message"> <xsl:value-of
					select="'tns:ExceptionResponse'" /> </xsl:attribute> </xsl:element>
					</xsl:element>
				-->
				<!--
					<xsl:element name="operation"> <xsl:attribute name="name">
					<xsl:value-of select="'DescribeProcess'" /> </xsl:attribute>
					<xsl:element name="input"> <xsl:attribute name="message">
					<xsl:value-of select="'tns:DescribeProcessRequest'" />
					</xsl:attribute> </xsl:element> <xsl:element name="output">
					<xsl:attribute name="message"> <xsl:value-of
					select="'tns:DescribeProcessResponse'" /> </xsl:attribute>
					</xsl:element> <xsl:element name="fault"> <xsl:attribute
					name="name"> <xsl:value-of select="'ExceptionResponse'" />
					</xsl:attribute> <xsl:attribute name="message"> <xsl:value-of
					select="'tns:ExceptionResponse'" /> </xsl:attribute> </xsl:element>
					</xsl:element> <xsl:element name="operation"> <xsl:attribute
					name="name"> <xsl:value-of select="'Execute'" /> </xsl:attribute>
					<xsl:element name="input"> <xsl:attribute name="message">
					<xsl:value-of select="'tns:ExecuteRequest'" /> </xsl:attribute>
					</xsl:element> <xsl:element name="output"> <xsl:attribute
					name="message"> <xsl:value-of select="'tns:ExceptionResponse'" />
					</xsl:attribute> </xsl:element> <xsl:element name="fault">
					<xsl:attribute name="name"> <xsl:value-of
					select="'ExceptionResponse'" /> </xsl:attribute> <xsl:attribute
					name="message"> <xsl:value-of select="'tns:ExceptionResponse'" />
					</xsl:attribute> </xsl:element> </xsl:element>
				-->
				<!--  end of operation -->
				<!-- Processes operations -->
				<xsl:for-each select="//*[local-name()='ProcessDescription']">
					<xsl:call-template name="operationDescribe">
						<xsl:with-param name="async" select="false()" />
						<xsl:with-param name="processID"
							select="concat('ExecuteProcess_',./*[local-name()='Identifier'])" />
					</xsl:call-template>
					<xsl:if
						test="string(./@storeSupported)='true' and string(./@statusSupported)='true'">
						<xsl:call-template name="operationDescribe">
							<xsl:with-param name="async" select="true()" />
							<xsl:with-param name="processID"
								select="concat('ExecuteProcessAsync_',./*[local-name()='Identifier'])" />
						</xsl:call-template>
					</xsl:if>
				</xsl:for-each>
				<!--  end of operation -->
			</xsl:element>
			<!-- End of portType -->
			<!-- Start of binding definition -->
			<xsl:element name="binding">
				<xsl:attribute name="name">
          <xsl:value-of select="concat($serverName,'_Binding')" />
        </xsl:attribute>
				<xsl:attribute name="type">
          <xsl:value-of select="concat('tns:',$serverName,'_PortType')" />
        </xsl:attribute>
				<xsl:element name="binding"
					namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="style">
            <xsl:value-of select="'document'" />
          </xsl:attribute>
					<xsl:attribute name="transport">
            <xsl:value-of select="'http://schemas.xmlsoap.org/soap/http'" />
          </xsl:attribute>
				</xsl:element>
				<!-- Operations inside SOAP -->
				<!-- Standard WPS SOAP operations -->
				<!-- REMOVED DUE TO OGC RECURSIVE LOOP -->
				<!--
					<xsl:element name="operation"> <xsl:attribute name="name">
					<xsl:value-of select="'GetCapabilities'" /> </xsl:attribute>
					<xsl:element name="operation"
					namespace="http://schemas.xmlsoap.org/wsdl/soap/"> <xsl:attribute
					name="soapAction"> <xsl:value-of
					select="concat($serverURL,'/GetCapabilities')" /> </xsl:attribute>
					<xsl:attribute name="style"> <xsl:value-of select="'document'" />
					</xsl:attribute> </xsl:element> <xsl:element name="input">
					<xsl:attribute name="name"> <xsl:value-of
					select="'GetCapabilitiesRequest'" /> </xsl:attribute> <xsl:element
					name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="use"> <xsl:value-of select="'literal'" />
					</xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="output"> <xsl:attribute name="name"> <xsl:value-of
					select="'GetCapabilitiesResponse'" /> </xsl:attribute> <xsl:element
					name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="use"> <xsl:value-of select="'literal'" />
					</xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="fault"> <xsl:attribute name="name"> <xsl:value-of
					select="'ExceptionResponse'" /> </xsl:attribute> <xsl:element
					name="fault" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="name"> <xsl:value-of
					select="'ExceptionResponse'" /> </xsl:attribute> <xsl:attribute
					name="use"> <xsl:value-of select="'literal'" /> </xsl:attribute>
					</xsl:element> </xsl:element> </xsl:element> <xsl:element
					name="operation"> <xsl:attribute name="name"> <xsl:value-of
					select="'DescribeProcess'" /> </xsl:attribute> <xsl:element
					name="operation" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="soapAction"> <xsl:value-of
					select="concat($serverURL,'/DescribeProcess')" /> </xsl:attribute>
					<xsl:attribute name="style"> <xsl:value-of select="'document'" />
					</xsl:attribute> </xsl:element> <xsl:element name="input">
					<xsl:attribute name="name"> <xsl:value-of
					select="'DescribeProcessRequest'" /> </xsl:attribute> <xsl:element
					name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="use"> <xsl:value-of select="'literal'" />
					</xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="output"> <xsl:attribute name="name"> <xsl:value-of
					select="'DescribeProcessResponse'" /> </xsl:attribute> <xsl:element
					name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="use"> <xsl:value-of select="'literal'" />
					</xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="fault"> <xsl:attribute name="name"> <xsl:value-of
					select="'ExceptionResponse'" /> </xsl:attribute> <xsl:element
					name="fault" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="name"> <xsl:value-of
					select="'ExceptionResponse'" /> </xsl:attribute> <xsl:attribute
					name="use"> <xsl:value-of select="'literal'" /> </xsl:attribute>
					</xsl:element> </xsl:element> </xsl:element> <xsl:element
					name="operation"> <xsl:attribute name="name"> <xsl:value-of
					select="'Execute'" /> </xsl:attribute> <xsl:element
					name="operation" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="soapAction"> <xsl:value-of
					select="concat($serverURL,'/Execute')" /> </xsl:attribute>
					<xsl:attribute name="style"> <xsl:value-of select="'document'" />
					</xsl:attribute> </xsl:element> <xsl:element name="input">
					<xsl:attribute name="name"> <xsl:value-of select="'ExecuteRequest'"
					/> </xsl:attribute> <xsl:element name="body"
					namespace="http://schemas.xmlsoap.org/wsdl/soap/"> <xsl:attribute
					name="use"> <xsl:value-of select="'literal'" /> </xsl:attribute>
					</xsl:element> </xsl:element> <xsl:element name="output">
					<xsl:attribute name="name"> <xsl:value-of
					select="'ExecuteResponse'" /> </xsl:attribute> <xsl:element
					name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="use"> <xsl:value-of select="'literal'" />
					</xsl:attribute> </xsl:element> </xsl:element> <xsl:element
					name="fault"> <xsl:attribute name="name"> <xsl:value-of
					select="'ExceptionResponse'" /> </xsl:attribute> <xsl:element
					name="fault" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="name"> <xsl:value-of
					select="'ExceptionResponse'" /> </xsl:attribute> <xsl:attribute
					name="use"> <xsl:value-of select="'literal'" /> </xsl:attribute>
					</xsl:element> </xsl:element> </xsl:element>
				-->
				<!-- end operation  -->
				<!-- Loop for each operation -->
				<xsl:for-each select="//*[local-name()='ProcessDescription']">
					<xsl:variable name="processID"
						select="concat('ExecuteProcess_',./*[local-name()='Identifier'])" />
					<!-- Note: variable only exist inside the loop -->
					<xsl:call-template name="bindingDescribe">
						<xsl:with-param name="async" select="false()" />
						<xsl:with-param name="processID"
							select="concat('ExecuteProcess_',./*[local-name()='Identifier'])" />
					</xsl:call-template>
					<xsl:if
						test="string(./@storeSupported)='true' and string(./@statusSupported)='true'">
						<xsl:call-template name="bindingDescribe">
							<xsl:with-param name="async" select="true()" />
							<xsl:with-param name="processID"
								select="concat('ExecuteProcessAsync_',./*[local-name()='Identifier'])" />
						</xsl:call-template>
					</xsl:if>
				</xsl:for-each>
				<!-- End of SOAP operation for each process -->
			</xsl:element>
			<!--End of binding -->
			<!-- service server description -->
			<xsl:element name="service">
				<xsl:attribute name="name">
          <xsl:value-of select="$serverName" />
        </xsl:attribute>
				<xsl:element name="documentation">
					<xsl:value-of select="None" />
				</xsl:element>
				<xsl:element name="port">
					<xsl:attribute name="name">
            <xsl:value-of select="concat($serverName,'_Port')" />
          </xsl:attribute>
					<xsl:attribute name="binding">
            <xsl:value-of select="concat('tns:',$serverName,'_Binding')" />
          </xsl:attribute>
					<xsl:element name="address"
						namespace="http://schemas.xmlsoap.org/wsdl/soap/">
						<xsl:attribute name="location">
              <xsl:value-of select="$serverURL" />
            </xsl:attribute>
					</xsl:element>
				</xsl:element>
				<!-- end of port element -->
			</xsl:element>
			<!-- end of service element -->
		</xsl:element>
		<!-- End of definitions, end of WSDL -->
	</xsl:template>
	<!-- types ProcessDescription template-->
	<xsl:template name="typeDescribe">
		<xsl:param name="async" />
		<xsl:param name="processID" />
		<!-- Inputs -->
		<xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema">
			<xsl:attribute name="targetNamespace">
        <xsl:value-of select="'http://www.opengis.net/wps/1.0.0'" />
      </xsl:attribute>
			<xsl:element name="element" namespace="http://www.w3.org/2001/XMLSchema">
				<xsl:attribute name="name">
          <xsl:value-of select="$processID" />
        </xsl:attribute>
				<xsl:element name="complexType" namespace="http://www.w3.org/2001/XMLSchema">
					<xsl:element name="sequence" namespace="http://www.w3.org/2001/XMLSchema">
						<!--
							Getting the Input value: minOccurs, maxOccurs,Identifier, and
							datatype (LiteralData) from each input
						-->
						<xsl:for-each select="./*/*[local-name()='Input']">
							<xsl:element name="element" namespace="http://www.w3.org/2001/XMLSchema">
								<xsl:attribute name="minOccurs">
                  <xsl:value-of select="./@minOccurs" />
                </xsl:attribute>
								<xsl:attribute name="maxOccurs">
                  <xsl:value-of select="./@maxOccurs" />
                </xsl:attribute>
								<xsl:attribute name="name">
                  <xsl:value-of
									select="fn:flagRemover(string(./*[local-name()='Identifier']))" />
                </xsl:attribute>
								<!--
									If to fecth datatype, its not safe to use ows:reference better
									to get the element value
								-->
								<!--  If no dataType then we need to  -->
								<xsl:if test="./*/*[local-name()='DataType']">
									<xsl:attribute name="type">
                    <xsl:value-of
										select="concat('xsd:',./*/*[local-name()='DataType'])" />
                  </xsl:attribute>
								</xsl:if>
							</xsl:element>
							<!-- End of element inside sequence -->
						</xsl:for-each>
						<!-- end of Input loop -->
					</xsl:element>
					<!--  End of sequence -->
				</xsl:element>
				<!-- End of complexType -->
			</xsl:element>
			<!-- End of element ExecuteProcess  Input definition -->
		</xsl:element>
		<!-- End of xsd:schema End of inputs -->
		<!--  Outputs/Response -->
		<xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema">
			<xsl:attribute name="targetNamespace">
        <xsl:value-of select="'http://www.opengis.net/wps/1.0.0'" />
      </xsl:attribute>
			<xsl:element name="element" namespace="http://www.w3.org/2001/XMLSchema">
				<!-- Using processID from above -->
				<xsl:attribute name="name">
          <xsl:value-of select="concat($processID,'Response')" />
        </xsl:attribute>
				<xsl:element name="complexType" namespace="http://www.w3.org/2001/XMLSchema">
					<xsl:element name="sequence" namespace="http://www.w3.org/2001/XMLSchema">
						<!--
							Getting the Ouput value: ,Identifier, and datatype (LiteralData)
							from each input
						-->
						<!-- If we have ascyn process then there is only one result -->
						<xsl:choose>
							<xsl:when test="$async">
								<!-- Element supporting URL -->
								<xsl:element name="element" namespace="http://www.w3.org/2001/XMLSchema">
									<xsl:attribute name="name">
                    <xsl:value-of select="'statusURLResult'" />
                  </xsl:attribute>
									<xsl:attribute name="minOccurs">
                    <xsl:value-of select="'1'" />
                  </xsl:attribute>
									<xsl:attribute name="maxOccurs">
                    <xsl:value-of select="'1'" />
                  </xsl:attribute>
								</xsl:element>
							</xsl:when>
							<xsl:otherwise>
								<xsl:for-each select="./*/*[local-name()='Output']">
									<xsl:element name="element"
										namespace="http://www.w3.org/2001/XMLSchema">
										<xsl:attribute name="name">
                      <xsl:value-of
											select="concat(fn:flagRemover(string(./*[local-name()='Identifier'])),'Result')" />
                    </xsl:attribute>
										<!--  not certain if a default minOccurs and maxOccurs should be set -->
										<xsl:attribute name="minOccurs">
                      <xsl:value-of select="'1'" />
                    </xsl:attribute>
										<xsl:attribute name="maxOccurs">
                      <xsl:value-of select="'1'" />
                    </xsl:attribute>
										<xsl:if test="./*/*[local-name()='DataType']">
											<xsl:attribute name="type">
                        <xsl:value-of
												select="concat('xsd:',./*/*[local-name()='DataType'])" />
                      </xsl:attribute>
										</xsl:if>
										<!--
											<xsl:choose> <xsl:when test="./*/*[local-name()='DataType']">
											<xsl:attribute name="type"><xsl:value-of
											select="concat('xsd:',./*/*[local-name()='DataType'])"></xsl:value-of></xsl:attribute>
											</xsl:when> <xsl:otherwise> <xsl:attribute
											name="type"><xsl:value-of
											select="'wps:anyXMLType'"></xsl:value-of></xsl:attribute>

											</xsl:otherwise> </xsl:choose>
										-->
										<xsl:if test="./*/*[local-name()='DataType']">
											<xsl:attribute name="type">
                        <xsl:value-of
												select="concat('xsd:',./*/*[local-name()='DataType'])" />
                      </xsl:attribute>
										</xsl:if>
									</xsl:element>
									<!-- response result element -->
								</xsl:for-each>
								<!-- End of output loop -->
							</xsl:otherwise>
							<!-- End of sync reponse from choose -->
						</xsl:choose>
						<!-- end of Async or sync output -->
					</xsl:element>
					<!-- sequence element end -->
				</xsl:element>
				<!-- ComplexType end -->
			</xsl:element>
			<!-- End of elemement with process response name -->
			<!-- adding anyXMLType -->
			<!--
				<complexType name="anyXMLType"
				xmlns="http://www.w3.org/2001/XMLSchema"
				targetNamespace="http://www.opengis.net/wps/1.0.0"> <sequence> <any
				namespace="##any" processContents="lax" minOccurs="1"
				maxOccurs="1"></any> </sequence> </complexType>
			-->
		</xsl:element>
		<!-- End of xsd:schema End of output -->
	</xsl:template>
	<xsl:template name="messageDescribe">
		<xsl:param name="async" />
		<xsl:param name="processID" />
		<!-- request message -->
		<xsl:element name="message">
			<xsl:attribute name="name">
        <xsl:value-of select="concat($processID,'Request')" />
      </xsl:attribute>
			<xsl:element name="part">
				<xsl:attribute name="name">
          <xsl:value-of select="'DataInputs'" />
        </xsl:attribute>
				<xsl:attribute name="element">
          <xsl:value-of select="concat('wps:',$processID)" />
        </xsl:attribute>
			</xsl:element>
		</xsl:element>
		<!--  response message -->
		<xsl:element name="message">
			<xsl:attribute name="name">
        <xsl:value-of select="concat($processID,'Response')" />
      </xsl:attribute>
			<xsl:element name="part">
				<xsl:attribute name="name">
          <xsl:value-of select="'ProcessOutputs'" />
        </xsl:attribute>
				<xsl:attribute name="element">
          <xsl:value-of select="concat('wps:',$processID,'Response')" />
        </xsl:attribute>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<xsl:template name="operationDescribe">
		<xsl:param name="async" />
		<xsl:param name="processID" />
		<!-- Operation section inside portType -->
		<xsl:element name="operation">
			<xsl:attribute name="name">
        <xsl:value-of select="$processID" />
      </xsl:attribute>
			<xsl:element name="input">
				<xsl:attribute name="message">
          <xsl:value-of select="concat('tns:',$processID,'Request')" />
        </xsl:attribute>
			</xsl:element>
			<xsl:element name="output">
				<xsl:attribute name="message">
          <xsl:value-of select="concat('tns:',$processID,'Response')" />
        </xsl:attribute>
			</xsl:element>
			<xsl:element name="fault">
				<xsl:attribute name="name">
          <xsl:value-of select="'ExceptionResponse'" />
        </xsl:attribute>
				<xsl:attribute name="message">
          <xsl:value-of select="'tns:ExceptionResponse'" />
        </xsl:attribute>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<xsl:template name="bindingDescribe">
		<xsl:param name="async" />
		<xsl:param name="processID" />
		<xsl:element name="operation">
			<xsl:attribute name="name">
        <xsl:value-of select="$processID" />
      </xsl:attribute>
			<xsl:element name="operation" namespace="http://schemas.xmlsoap.org/wsdl/soap/">
				<xsl:attribute name="soapAction">
          <xsl:value-of select="concat($serverURL,'/',$processID)" />
        </xsl:attribute>
				<xsl:attribute name="style">
          <xsl:value-of select="'document'" />
        </xsl:attribute>
			</xsl:element>
			<xsl:element name="input">
				<xsl:attribute name="name">
          <xsl:value-of select="concat($processID,'Request')" />
        </xsl:attribute>
				<xsl:element name="body"
					namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="use">
            <xsl:value-of select="'literal'" />
          </xsl:attribute>
				</xsl:element>
			</xsl:element>
			<!-- end input -->
			<xsl:element name="output">
				<xsl:attribute name="name">
          <xsl:value-of select="concat($processID,'Response')" />
        </xsl:attribute>
				<xsl:element name="body"
					namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="use">
            <xsl:value-of select="'literal'" />
          </xsl:attribute>
				</xsl:element>
			</xsl:element>
			<!-- end input -->
			<xsl:element name="fault">
				<xsl:attribute name="name">
          <xsl:value-of select="'ExceptionResponse'" />
        </xsl:attribute>
				<xsl:element name="fault"
					namespace="http://schemas.xmlsoap.org/wsdl/soap/">
					<xsl:attribute name="name">
            <xsl:value-of select="'ExceptionResponse'" />
          </xsl:attribute>
					<xsl:attribute name="use">
            <xsl:value-of select="'literal'" />
          </xsl:attribute>
				</xsl:element>
			</xsl:element>
			<!-- end input -->
		</xsl:element>
		<!-- end operation  -->
	</xsl:template>
</xsl:stylesheet>
