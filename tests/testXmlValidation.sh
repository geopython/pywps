#!/bin/bash

TMP_DIR=/tmp/
ZOO_URL=$1
DESC_SERV="Buffer Boundary Centroid ConvexHull Simplify Union Intersection Difference SymDifference"

if [ -z "${ZOO_URL}" ] ; then
    echo "Usage : "
    echo " testXmlValiation.sh <ZOO Kernel URL>"
    echo ""
    echo "For example to test a local ZOO Kernel use the following :"
    echo "./testXmlValiation.sh http://localhost/cgi-bin/zoo_loader.cgi"
    exit;
fi

echo " * Test validity of the answer for GetCapabilities request"
xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd "${ZOO_URL}?REQUEST=GetCapabilities&SERVICE=WPS"

echo " * Test validity of the answer for DescribeProcess requests"
for i in ${DESC_SERV}; do 
    echo " * DescribeProcess for $i";
    xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd "${ZOO_URL}?REQUEST=DescribeProcess&SERVICE=WPS&version=1.0.0&Identifier=${i}";
done

echo " * DescribeProcess for ${DESC_SERV}"
xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd "${ZOO_URL}?REQUEST=DescribeProcess&SERVICE=WPS&version=1.0.0&Identifier=$(echo ${DESC_SERV} | sed 's: :,:g')"


echo " * Test validity of the answer for Execute requests"

echo " ** Test validity of the answer for a synchronous call using asReference"
curl -H "Content-Type: text/xml" -d '<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd">
<ows:Identifier>Buffer</ows:Identifier>
<wps:DataInputs>
<wps:Input>
<ows:Identifier>InputPolygon</ows:Identifier>
<ows:Title>Playground area</ows:Title>
<wps:Reference xlink:href="http://dreal-official.geolabs.fr/mapjax/webservices/wfs/dreal_lr_general/?VERSION=1.1.0&amp;version=1.0.0&amp;request=GetFeature&amp;typename=Znieff1&amp;maxfeatures=1"/></wps:Input>
<wps:Input>
<ows:Identifier>BufferDistance</ows:Identifier>
<ows:Title>Distance which people will walk to get to a playground.</ows:Title>
<wps:Data>
<wps:LiteralData>10</wps:LiteralData>
</wps:Data>
</wps:Input>
</wps:DataInputs>
<wps:ResponseForm>
<wps:ResponseDocument storeExecuteResponse="false">
<wps:Output asReference="true">
<ows:Identifier>Result</ows:Identifier>
</wps:Output>
</wps:ResponseDocument>
</wps:ResponseForm>
</wps:Execute>' "${ZOO_URL}" -o "${TMP_DIR}execute_sync_ref.xml" 2> "${TMP_DIR}log"

xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd "${TMP_DIR}execute_sync_ref.xml"


echo " ** Test validity of the answer for a synchronous call with data included"
curl -H "Content-Type: text/xml" -d '<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd">
<ows:Identifier>Buffer</ows:Identifier>
<wps:DataInputs>
<wps:Input>
<ows:Identifier>InputPolygon</ows:Identifier>
<ows:Title>Playground area</ows:Title>
<wps:Reference xlink:href="http://dreal-official.geolabs.fr/mapjax/webservices/wfs/dreal_lr_general/?VERSION=1.1.0&amp;version=1.0.0&amp;request=GetFeature&amp;typename=Znieff1&amp;maxfeatures=1"/></wps:Input>
<wps:Input>
<ows:Identifier>BufferDistance</ows:Identifier>
<ows:Title>Distance which people will walk to get to a playground.</ows:Title>
<wps:Data>
<wps:LiteralData>10</wps:LiteralData>
</wps:Data>
</wps:Input>
</wps:DataInputs>
<wps:ResponseForm>
<wps:ResponseDocument storeExecuteResponse="false">
<wps:Output asReference="false">
<ows:Identifier>Result</ows:Identifier>
</wps:Output>
</wps:ResponseDocument>
</wps:ResponseForm>
</wps:Execute>' http://www.zoo-project.org/cgi-bin-new1/zoo_loader.cgi -o "${TMP_DIR}execute_sync_woref.xml"  2> "${TMP_DIR}log"

xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd "${TMP_DIR}execute_sync_woref.xml"

echo " ** Test validity of the answer for an asynchronous call using asReference"
echo " ** 1) Check initial answer"
curl -H "Content-Type: text/xml" -d '<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd">
<ows:Identifier>Buffer</ows:Identifier>
<wps:DataInputs>
<wps:Input>
<ows:Identifier>InputPolygon</ows:Identifier>
<ows:Title>Playground area</ows:Title>
<wps:Reference xlink:href="http://dreal-official.geolabs.fr/mapjax/webservices/wfs/dreal_lr_general/?VERSION=1.1.0&amp;version=1.0.0&amp;request=GetFeature&amp;typename=Znieff1&amp;maxfeatures=1"/></wps:Input>
<wps:Input>
<ows:Identifier>BufferDistance</ows:Identifier>
<ows:Title>Distance which people will walk to get to a playground.</ows:Title>
<wps:Data>
<wps:LiteralData>10</wps:LiteralData>
</wps:Data>
</wps:Input>
</wps:DataInputs>
<wps:ResponseForm>
<wps:ResponseDocument storeExecuteResponse="true" status="true">
<wps:Output asReference="true">
<ows:Identifier>Result</ows:Identifier>
</wps:Output>
</wps:ResponseDocument>
</wps:ResponseForm>
</wps:Execute>' http://www.zoo-project.org/cgi-bin-new1/zoo_loader.cgi -o "${TMP_DIR}execute_async_ref.xml"  2> "${TMP_DIR}log"

xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd "${TMP_DIR}execute_async_ref.xml"

echo " ** 2) Check the statusLocation"
xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd "$(xsltproc ./extractStatusLocation.xsl "${TMP_DIR}execute_async_ref.xml")"


echo " ** Test validity of the answer for an asynchronous call with data included"
echo " ** 1) Check initial answer"
curl -H "Content-Type: text/xml" -d '<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd">
<ows:Identifier>Buffer</ows:Identifier>
<wps:DataInputs>
<wps:Input>
<ows:Identifier>InputPolygon</ows:Identifier>
<ows:Title>Playground area</ows:Title>
<wps:Reference xlink:href="http://dreal-official.geolabs.fr/mapjax/webservices/wfs/dreal_lr_general/?VERSION=1.1.0&amp;version=1.0.0&amp;request=GetFeature&amp;typename=Znieff1&amp;maxfeatures=1"/></wps:Input>
<wps:Input>
<ows:Identifier>BufferDistance</ows:Identifier>
<ows:Title>Distance which people will walk to get to a playground.</ows:Title>
<wps:Data>
<wps:LiteralData>10</wps:LiteralData>
</wps:Data>
</wps:Input>
</wps:DataInputs>
<wps:ResponseForm>
<wps:ResponseDocument storeExecuteResponse="true" status="true">
<wps:Output asReference="false">
<ows:Identifier>Result</ows:Identifier>
</wps:Output>
</wps:ResponseDocument>
</wps:ResponseForm>
</wps:Execute>' http://www.zoo-project.org/cgi-bin-new1/zoo_loader.cgi -o "${TMP_DIR}execute_async_woref.xml"  2> "${TMP_DIR}log"

xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd "${TMP_DIR}execute_async_woref.xml"

echo " ** 2) Check the statusLocation"
xmllint  --noout --schema http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd "$(xsltproc ./extractStatusLocation.xsl "${TMP_DIR}execute_async_ref.xml")"
