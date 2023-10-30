from basic import TestBase

from pywps import xml_util as etree

from io import StringIO


XML_EXECUTE = """
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///PATH/TO/input.txt">
]>
<wps:Execute
    service="WPS"
    version="1.0.0"
    xmlns:wps="http://www.opengis.net/wps/1.0.0"
    xmlns:ows="http://www.opengis.net/ows/1.1"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd">
    <ows:Identifier>test_process</ows:Identifier>
    <wps:DataInputs>
        <wps:Input>
            <ows:Identifier>name</ows:Identifier>
            <wps:Data>
                <wps:LiteralData>&xxe;</wps:LiteralData>
            </wps:Data>
        </wps:Input>
    </wps:DataInputs>
    <wps:ResponseForm>
        <wps:ResponseDocument
            storeExecuteResponse="true"
            status="true">
            <wps:Output asReference="false">
                <ows:Identifier>output</ows:Identifier>
            </wps:Output>
        </wps:ResponseDocument>
    </wps:ResponseForm>
</wps:Execute>
"""


def test_etree_fromstring():
    xml = etree.tostring(etree.fromstring(XML_EXECUTE))
    # don't replace entities
    # https://lxml.de/parsing.html
    assert b"<wps:LiteralData>&xxe;</wps:LiteralData>" in xml


def test_etree_parse():
    xml = etree.tostring(etree.parse(StringIO(XML_EXECUTE)))
    # don't replace entities
    # https://lxml.de/parsing.html
    assert b"<wps:LiteralData>&xxe;</wps:LiteralData>" in xml
