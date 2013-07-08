"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""

from werkzeug.wrappers import Request, Response


CAPABILITIES_ANSWER = '''\
<?xml version="1.0" encoding="utf-8"?>
<wps:Capabilities service="WPS" version="1.0.0"
  xmlns:wps="http://www.opengis.net/wps/1.0.0"
  xmlns:ows="http://www.opengis.net/ows/1.1">
    <ows:ServiceIdentification>
        <ows:Title>PyWPS Server</ows:Title>
        <ows:Abstract>Development version of PyWPS</ows:Abstract>
        <ows:ServiceType>WPS</ows:ServiceType>
        <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>
        <ows:Fees>None</ows:Fees>
        <ows:AccessConstraints>none</ows:AccessConstraints>
    </ows:ServiceIdentification>
</wps:Capabilities>
'''


NAMESPACES = {
  'wps': "http://www.opengis.net/wps/1.0.0",
  'ows': "http://www.opengis.net/ows/1.1",
}


class Process:
    """ WPS process """

    @Request.application
    def __call__(self, request):
        return Response(CAPABILITIES_ANSWER)


def create_process():
    return Process()
