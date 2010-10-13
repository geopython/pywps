<?xml version="1.0" encoding="UTF-8"?>
<!-- ${workspace_loc:/GetCapabilities2WSDL/getCapabilities.xml} -->

<!-- REPLACEME == serverURL  and it needs to be done externaly-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:tns="REPLACEME_wsdl"
		xmlns="http://schemas.xmlsoap.org/wsdl/"
        xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
        xmlns:wps="http://www.opengis.net/wps/1.0.0"
        xmlns:ows="http://www.opengis.net/ows/1.1"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:wsdl="http://schemas.xmlsoap.org/wsdl">
<xsl:output method="xml" indent="yes" omit-xml-declaration="no"/>        
<!-- External variables passed by Python to the XSLT transformer -->                
<xsl:param name="serverURL"/>
<xsl:param name="serverName"/>

<!-- No longer necessary to set serverURL and serverName -->
<!--  
<xsl:variable name="serverURL"><xsl:value-of select="'http://localhost/wps.cgi'"></xsl:value-of></xsl:variable>
<xsl:variable name="serverName"><xsl:value-of select="'PywpsServer'"></xsl:value-of></xsl:variable> 
-->
	
	<xsl:template match="/">
	

		  <xsl:element name="definitions">
		  <!--  Hack, the namespaces are copied from the <stylesheet> element -->
		  <xsl:copy-of select="document('')/xsl:stylesheet/namespace::*[name()!='xsl']"/>
            <xsl:attribute name="targetNamespace"><xsl:value-of select="concat($serverURL,'_wsdl')" /></xsl:attribute>
		  
		  <xsl:element name="types">
		  		<!-- Generic WPS support -->
		  		<!-- Special type for any sort of XML inside the response, this allows for some used of the XMLsplitter in taverna.
		  		The xsd: namespace is necessary here otherwise the parser will assume wsdl: and will crash. Everything we have an undefined dataType the system will use this -->
		  <!-- 		<xsd:schema><xsd:complexType name="anyXMLType" xmlns="http://www.w3.org/2001/XMLSchema" targetNamespace="http://www.opengis.net/wps/1.0.0">
                							<xsd:sequence>
            								<xsd:any namespace="##any" processContents="lax" minOccurs="1" maxOccurs="1"></xsd:any>
            								</xsd:sequence>
            								</xsd:complexType></xsd:schema> -->
		  		
		  		<!-- Exception report -->
		  	 <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/ows/1.1'"></xsl:value-of></xsl:attribute>
				<xsl:element name="include" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="schemaLocation"><xsl:value-of select="'http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd'" /></xsl:attribute></xsl:element>	  	
		     </xsl:element>
		     <!-- GetCapabilities report -->
		  	 <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/wps/1.0.0'"></xsl:value-of></xsl:attribute>
				<xsl:element name="include" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="schemaLocation"><xsl:value-of select="'http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_request.xsd'" /></xsl:attribute></xsl:element>	  	
		     </xsl:element>
		     <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/wps/1.0.0'"></xsl:value-of></xsl:attribute>
				<xsl:element name="include" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="schemaLocation"><xsl:value-of select="'http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd'" /></xsl:attribute></xsl:element>	  	
		     </xsl:element>		
			<!-- DescribeProcess report -->
			<xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/wps/1.0.0'"></xsl:value-of></xsl:attribute>
				<xsl:element name="include" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="schemaLocation"><xsl:value-of select="'http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_request.xsd'" /></xsl:attribute></xsl:element>	  	
		     </xsl:element>
		     <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/wps/1.0.0'"></xsl:value-of></xsl:attribute>
				<xsl:element name="include" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="schemaLocation"><xsl:value-of select="'http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'" /></xsl:attribute></xsl:element>	  	
		     </xsl:element>
		     <!-- Execute report -->
		     <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/wps/1.0.0'"></xsl:value-of></xsl:attribute>
				<xsl:element name="include" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="schemaLocation"><xsl:value-of select="'http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd'" /></xsl:attribute></xsl:element>	  	
		     </xsl:element>
		     <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/wps/1.0.0'"></xsl:value-of></xsl:attribute>
				<xsl:element name="include" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="schemaLocation"><xsl:value-of select="'http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd'" /></xsl:attribute></xsl:element>	  	
		     </xsl:element>
		       <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/ows/1.1'"></xsl:value-of></xsl:attribute>
				<xsl:element name="include" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="schemaLocation"><xsl:value-of select="'http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd'" /></xsl:attribute></xsl:element>	  	
		     </xsl:element>	
		     
		   	
		  	<!-- End of General WPS support -->
		  <!-- ExecuteProcess support -->
		  <!-- loop thru processes and set the xsd types -->
		  <xsl:for-each select="//*[local-name()='ProcessDescription']">
		  	         <xsl:variable name="processID" select="concat('ExecuteProcess_',./*[local-name()='Identifier'])"></xsl:variable>
		  	         <!-- Inputs -->
					 <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/wps/1.0.0'"></xsl:value-of></xsl:attribute>
		  	         <xsl:element name="element" namespace="http://www.w3.org/2001/XMLSchema">
		  	         	
		  	         	<xsl:attribute name="name"><xsl:value-of select="$processID"></xsl:value-of></xsl:attribute>
		  	             <xsl:element name="complexType" namespace="http://www.w3.org/2001/XMLSchema">
		  	             	<xsl:element name="sequence" namespace="http://www.w3.org/2001/XMLSchema">
		  	             		<!-- Getting the Input value: minOccurs, maxOccurs,Identifier, and datatype (LiteralData) from each input -->
		  	             		<xsl:for-each select="./*/*[local-name()='Input']">
		  	             			<xsl:element name="element" namespace="http://www.w3.org/2001/XMLSchema">
		  	             				<xsl:attribute name="minOccurs"><xsl:value-of select="./@minOccurs"></xsl:value-of></xsl:attribute>
		  	             				<xsl:attribute name="maxOccurs"><xsl:value-of select="./@maxOccurs"></xsl:value-of></xsl:attribute>
		  	             				<xsl:attribute name="name"><xsl:value-of select="./*[local-name()='Identifier']"></xsl:value-of></xsl:attribute>
		  	             				<!--  If to fecth datatype, its not safe to use ows:reference better to get the element value -->
		  	             					<!--  If no dataType then we need to  -->
		  	             					
		  	             					<xsl:if test="./*/*[local-name()='DataType']">
		  	             					<xsl:attribute name="type"><xsl:value-of select="concat('xsd:',./*/*[local-name()='DataType'])"></xsl:value-of></xsl:attribute>
		  	             				    </xsl:if>
		  	             				  
		  	             				    	
		  	             				   
		  	        				    
		  	             
		  	             			</xsl:element><!-- End of element inside sequence -->		
		  	             		
		  	             		</xsl:for-each> <!-- end of Input loop -->
		  	             	
		  	             	
		  	             	
		  	             	</xsl:element><!--  End of sequence --> 
		  	             
		  	             </xsl:element> <!-- End of complexType -->
		  	             
		  			</xsl:element><!-- End of element ExecuteProcess  Input definition -->
		  			</xsl:element><!-- End of xsd:schema End of inputs -->
		  			<!--  Outputs/Response -->
		  			 <xsl:element name="schema" namespace="http://www.w3.org/2001/XMLSchema"><xsl:attribute name="targetNamespace"><xsl:value-of select="'http://www.opengis.net/wps/1.0.0'"></xsl:value-of></xsl:attribute>
		  			 <xsl:element name="element" namespace="http://www.w3.org/2001/XMLSchema">
		  			 <!-- Using processID from above -->
		  			 <xsl:attribute name="name"><xsl:value-of select="concat($processID,'Response')"></xsl:value-of></xsl:attribute>
		  			 	 <xsl:element name="complexType" namespace="http://www.w3.org/2001/XMLSchema">
		  			 	 <xsl:element name="sequence" namespace="http://www.w3.org/2001/XMLSchema">
		  			 	 <!-- Getting the Ouput value: ,Identifier, and datatype (LiteralData) from each input -->
		  			 	 <xsl:for-each select="./*/*[local-name()='Output']">
		  			 	 <xsl:element name="element" namespace="http://www.w3.org/2001/XMLSchema">
		  			 	 <xsl:attribute name="name"><xsl:value-of select="concat(./*[local-name()='Identifier'],'Result')"></xsl:value-of></xsl:attribute>
		  			 	 <!--  not certain if a default minOccurs and maxOccurs should be set -->
		  			 	 <xsl:attribute name="minOccurs"><xsl:value-of select="'1'"></xsl:value-of></xsl:attribute>
		  	             <xsl:attribute name="maxOccurs"><xsl:value-of select="'1'"></xsl:value-of></xsl:attribute>
		  						<xsl:if test="./*/*[local-name()='DataType']">
		  	             					<xsl:attribute name="type"><xsl:value-of select="concat('xsd:',./*/*[local-name()='DataType'])"></xsl:value-of></xsl:attribute>
		  	             				    </xsl:if>
     				 		
		  	         <!--      <xsl:choose> 
		  	             					<xsl:when test="./*/*[local-name()='DataType']">
		  	             					<xsl:attribute name="type"><xsl:value-of select="concat('xsd:',./*/*[local-name()='DataType'])"></xsl:value-of></xsl:attribute>
		  	             				    </xsl:when>
		  	             				    <xsl:otherwise> 
		  	             				    <xsl:attribute name="type"><xsl:value-of select="'wps:anyXMLType'"></xsl:value-of></xsl:attribute>
		  	             				   
		  	             				    </xsl:otherwise>
		  	             				    	
		 	             </xsl:choose>
		 	              -->
		  	              
		  	             
		  	             <xsl:if test="./*/*[local-name()='DataType']">
		  	             					<xsl:attribute name="type"><xsl:value-of select="concat('xsd:',./*/*[local-name()='DataType'])"></xsl:value-of></xsl:attribute>
		  	             				    </xsl:if>
		  			 	 
		  			 	 </xsl:element><!-- response result element -->
		  			 	 
		  			 	 
		  			 	 
		  			 	 
		  			 	 </xsl:for-each> <!-- End of output loop -->
		  			 	 
		  			 	 </xsl:element> <!-- sequence element end -->
		  			 	 
		  			 	 
		  			 	 </xsl:element> <!-- ComplexType end -->
		  			 </xsl:element> <!-- End of elemement with process response name -->
		  			 
		  			 <!-- adding anyXMLType -->
		  			<!--    <complexType name="anyXMLType" xmlns="http://www.w3.org/2001/XMLSchema" targetNamespace="http://www.opengis.net/wps/1.0.0">
                							<sequence>
            								<any namespace="##any" processContents="lax" minOccurs="1" maxOccurs="1"></any>
            								</sequence>
            								</complexType>-->
		  			 
		  			 </xsl:element><!-- End of xsd:schema End of output -->
		  			 

		  
		  
		  </xsl:for-each><!-- End of DescribeProcess loop for types -->
		  
		  </xsl:element> <!-- End of types element -->
		  
<!-- message sections -->		  
	<!-- Default WPS request/response messages -->
	 <xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="'GetCapabilitiesRequest'"></xsl:value-of></xsl:attribute>
		  	         <xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'msg'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="'wps:GetCapabilities'"></xsl:value-of></xsl:attribute></xsl:element>
		</xsl:element>
		<xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="'GetCapabilitiesResponse'"></xsl:value-of></xsl:attribute>
		  	         <xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'msg'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="'wps:Capabilities'"></xsl:value-of></xsl:attribute></xsl:element>
		</xsl:element>
		
		 <xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="'DescribeProcessRequest'"></xsl:value-of></xsl:attribute>
		  	         <xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'msg'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="'wps:DescribeProcess'"></xsl:value-of></xsl:attribute></xsl:element>
		</xsl:element>
		<xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="'DescribeProcessResponse'"></xsl:value-of></xsl:attribute>
		  	         <xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'msg'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="'wps:ProcessDescriptions'"></xsl:value-of></xsl:attribute></xsl:element>
		</xsl:element>
		
		<xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="'ExecuteRequest'"></xsl:value-of></xsl:attribute>
		  	         <xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'msg'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="'wps:Execute'"></xsl:value-of></xsl:attribute></xsl:element>
		</xsl:element>
		<xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="'ExecuteResponse'"></xsl:value-of></xsl:attribute>
		  	         <xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'msg'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="'wps:ExecuteResponse'"></xsl:value-of></xsl:attribute></xsl:element>
		</xsl:element>
		<xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute>
		  	         <xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'msg'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="'ows:Exception'"></xsl:value-of></xsl:attribute></xsl:element>
		</xsl:element>
		
		<!-- End of default WPS request/response messages -->
		<!--  Process loop to fetch name -->
		<!-- Its better to do another loop than one giant loop with everythin -->
		<xsl:for-each select="//*[local-name()='ProcessDescription']">
		<xsl:variable name="processID" select="concat('ExecuteProcess_',./*[local-name()='Identifier'])"></xsl:variable>
		
			<!-- request message -->
			<xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="concat($processID,'Request')"></xsl:value-of></xsl:attribute>
				<xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'DataInputs'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="concat('wps:',$processID)"></xsl:value-of></xsl:attribute></xsl:element>
			</xsl:element>
			
			<!--  response message -->
			<xsl:element name="message"><xsl:attribute name="name"><xsl:value-of select="concat($processID,'Response')"></xsl:value-of></xsl:attribute>
				<xsl:element name="part"><xsl:attribute name="name"><xsl:value-of select="'ProcessOutputs'"></xsl:value-of></xsl:attribute>
		  	         <xsl:attribute name="element"><xsl:value-of select="concat('wps:',$processID,'Response')"></xsl:value-of></xsl:attribute></xsl:element>
			</xsl:element>

		</xsl:for-each> <!-- End of process description loop for message -->
		
		  <!-- portType structure  -->
		  <xsl:element name="portType"><xsl:attribute name="name"><xsl:value-of select="concat($serverName,'_PortType')"></xsl:value-of></xsl:attribute>
		   <!-- Loop operations -->
		   <!-- General WPS compliance -->
		    
		   <xsl:element name="operation"><xsl:attribute name="name"><xsl:value-of select="'GetCapabilities'"></xsl:value-of></xsl:attribute>
		     <xsl:element name="input"><xsl:attribute name="message"><xsl:value-of select="'tns:GetCapabilitiesRequest'"></xsl:value-of></xsl:attribute></xsl:element>
		     <xsl:element name="output"><xsl:attribute name="message"><xsl:value-of select="'tns:GetCapabilitiesResponse'"></xsl:value-of></xsl:attribute></xsl:element>
		     <xsl:element name="fault"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute><xsl:attribute name="message"><xsl:value-of select="'tns:ExceptionResponse'"></xsl:value-of></xsl:attribute></xsl:element>
		   </xsl:element><!--  end of operation -->
		   
		   <xsl:element name="operation"><xsl:attribute name="name"><xsl:value-of select="'DescribeProcess'"></xsl:value-of></xsl:attribute>
		     <xsl:element name="input"><xsl:attribute name="message"><xsl:value-of select="'tns:DescribeProcessRequest'"></xsl:value-of></xsl:attribute></xsl:element>
		     <xsl:element name="output"><xsl:attribute name="message"><xsl:value-of select="'tns:DescribeProcessResponse'"></xsl:value-of></xsl:attribute></xsl:element>
		     <xsl:element name="fault"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute><xsl:attribute name="message"><xsl:value-of select="'tns:ExceptionResponse'"></xsl:value-of></xsl:attribute></xsl:element>
		   </xsl:element><!--  end of operation -->
		   
		   <xsl:element name="operation"><xsl:attribute name="name"><xsl:value-of select="'Execute'"></xsl:value-of></xsl:attribute>
		     <xsl:element name="input"><xsl:attribute name="message"><xsl:value-of select="'tns:ExecuteRequest'"></xsl:value-of></xsl:attribute></xsl:element>
		     <xsl:element name="output"><xsl:attribute name="message"><xsl:value-of select="'tns:ExceptionResponse'"></xsl:value-of></xsl:attribute></xsl:element>
		     <xsl:element name="fault"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute><xsl:attribute name="message"><xsl:value-of select="'tns:ExceptionResponse'"></xsl:value-of></xsl:attribute></xsl:element>
		   </xsl:element><!--  end of operation -->
		
		   <!-- Processes operations -->
		   <xsl:for-each select="//*[local-name()='ProcessDescription']">
				<xsl:variable name="processID" select="concat('ExecuteProcess_',./*[local-name()='Identifier'])"></xsl:variable><!-- Note: variable only exist inside the loop -->
		     
		     	<xsl:element name="operation"><xsl:attribute name="name"><xsl:value-of select="$processID"></xsl:value-of></xsl:attribute>
		     	<xsl:element name="input"><xsl:attribute name="message"><xsl:value-of select="concat('tns:',$processID,'Request')"></xsl:value-of></xsl:attribute></xsl:element>
		     	<xsl:element name="output"><xsl:attribute name="message"><xsl:value-of select="concat('tns:',$processID,'Response')"></xsl:value-of></xsl:attribute></xsl:element>
		     	<xsl:element name="fault"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute><xsl:attribute name="message"><xsl:value-of select="'tns:ExceptionResponse'"></xsl:value-of></xsl:attribute></xsl:element>
		   	</xsl:element>  
		   </xsl:for-each>
		   <!--  end of operation -->
		   
		   </xsl:element> <!-- End of portType -->
		   
		   <!-- Start of binding definition -->
		   <xsl:element name="binding"><xsl:attribute name="name"><xsl:value-of select="concat($serverName,'_Binding')"></xsl:value-of></xsl:attribute><xsl:attribute name="type"><xsl:value-of select="concat('tns:',$serverName,'_PortType')"></xsl:value-of></xsl:attribute>
		   <xsl:element name="binding" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="style"><xsl:value-of select="'document'"></xsl:value-of></xsl:attribute><xsl:attribute name="transport"><xsl:value-of select="'http://schemas.xmlsoap.org/soap/http'"></xsl:value-of></xsl:attribute></xsl:element>
		   <!-- Operations inside SOAP -->
		   <!-- Standard WPS SOAP operations -->
		   <xsl:element name="operation"><xsl:attribute name="name"><xsl:value-of select="'GetCapabilities'"></xsl:value-of></xsl:attribute>
		   		<xsl:element name="operation" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="soapAction"><xsl:value-of select="concat($serverURL,'/GetCapabilities')"></xsl:value-of></xsl:attribute><xsl:attribute name="style"><xsl:value-of select="'document'"></xsl:value-of></xsl:attribute></xsl:element>
		   		
		   		<xsl:element name="input"><xsl:attribute name="name"><xsl:value-of select="'GetCapabilitiesRequest'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   		
		   		<xsl:element name="output"><xsl:attribute name="name"><xsl:value-of select="'GetCapabilitiesResponse'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   		
		   		<xsl:element name="fault"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="fault" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   </xsl:element><!-- end operation  -->
		   
		   <xsl:element name="operation"><xsl:attribute name="name"><xsl:value-of select="'DescribeProcess'"></xsl:value-of></xsl:attribute>
		   		<xsl:element name="operation" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="soapAction"><xsl:value-of select="concat($serverURL,'/DescribeProcess')"></xsl:value-of></xsl:attribute><xsl:attribute name="style"><xsl:value-of select="'document'"></xsl:value-of></xsl:attribute></xsl:element>
		   		
		   		<xsl:element name="input"><xsl:attribute name="name"><xsl:value-of select="'DescribeProcessRequest'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   		
		   		<xsl:element name="output"><xsl:attribute name="name"><xsl:value-of select="'DescribeProcessResponse'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   		
		   		<xsl:element name="fault"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="fault" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   </xsl:element><!-- end operation  -->
		   
		    <xsl:element name="operation"><xsl:attribute name="name"><xsl:value-of select="'Execute'"></xsl:value-of></xsl:attribute>
		   		<xsl:element name="operation" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="soapAction"><xsl:value-of select="concat($serverURL,'/Execute')"></xsl:value-of></xsl:attribute><xsl:attribute name="style"><xsl:value-of select="'document'"></xsl:value-of></xsl:attribute></xsl:element>
		   		
		   		<xsl:element name="input"><xsl:attribute name="name"><xsl:value-of select="'ExecuteRequest'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   		
		   		<xsl:element name="output"><xsl:attribute name="name"><xsl:value-of select="'ExecuteResponse'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   		
		   		<xsl:element name="fault"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="fault" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   </xsl:element><!-- end operation  -->
		   
		   <!-- Loop for each operation -->
		   <xsl:for-each select="//*[local-name()='ProcessDescription']">
		   <xsl:variable name="processID" select="concat('ExecuteProcess_',./*[local-name()='Identifier'])"></xsl:variable><!-- Note: variable only exist inside the loop -->
		   <xsl:element name="operation"><xsl:attribute name="name"><xsl:value-of select="$processID"></xsl:value-of></xsl:attribute>
		   		<xsl:element name="operation" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="soapAction"><xsl:value-of select="concat($serverURL,'/',$processID)"></xsl:value-of></xsl:attribute><xsl:attribute name="style"><xsl:value-of select="'document'"></xsl:value-of></xsl:attribute></xsl:element>
		   		
		   		<xsl:element name="input"><xsl:attribute name="name"><xsl:value-of select="concat($processID,'Request')"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   		
		   		<xsl:element name="output"><xsl:attribute name="name"><xsl:value-of select="concat($processID,'Response')"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="body" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   		
		   		<xsl:element name="fault"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute>
		   			<xsl:element name="fault" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="name"><xsl:value-of select="'ExceptionResponse'"></xsl:value-of></xsl:attribute><xsl:attribute name="use"><xsl:value-of select="'literal'"></xsl:value-of></xsl:attribute></xsl:element>
		   		</xsl:element><!-- end input -->
		   </xsl:element><!-- end operation  -->
		   
		   </xsl:for-each> <!-- End of SOAP operation for each process -->
		   
		   </xsl:element><!--End of binding -->


<!-- service server description -->
	<xsl:element name="service"><xsl:attribute name="name"><xsl:value-of select="$serverName"></xsl:value-of></xsl:attribute>
	<xsl:element name="documentation"><xsl:value-of select='None'></xsl:value-of></xsl:element>
	<xsl:element name="port">
		<xsl:attribute name="name"><xsl:value-of select="concat($serverName,'_Port')"></xsl:value-of></xsl:attribute>
		<xsl:attribute name="binding"><xsl:value-of select="concat('tns:',$serverName,'_Binding')"></xsl:value-of></xsl:attribute>
		<xsl:element name="address" namespace="http://schemas.xmlsoap.org/wsdl/soap/"><xsl:attribute name="location"><xsl:value-of select="$serverURL"></xsl:value-of></xsl:attribute></xsl:element>
	</xsl:element><!-- end of port element -->
	
	</xsl:element> <!-- end of service element -->		     
		  </xsl:element> <!-- End of definitions, end of WSDL -->
		 <foo><xsl:value-of select="$serverName" /></foo>
	</xsl:template>
</xsl:stylesheet>