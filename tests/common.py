import lxml.etree
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from pywps import NAMESPACES


class WpsClient(Client):

    def post_xml(self, *args, **kwargs):
        doc = kwargs.pop('doc')
        data = lxml.etree.tostring(doc, pretty_print=True)
        kwargs['data'] = data
        return self.post(*args, **kwargs)


class WpsTestResponse(BaseResponse):

    def __init__(self, *args):
        super(WpsTestResponse, self).__init__(*args)
        if self.headers.get('Content-Type') == 'text/xml':
            self.xml = lxml.etree.fromstring(self.get_data())

    def xpath(self, path):
        return self.xml.xpath(path, namespaces=NAMESPACES)

    def xpath_text(self, path):
        return ' '.join(e.text for e in self.xpath(path))


def client_for(service):
    return WpsClient(service, WpsTestResponse)
