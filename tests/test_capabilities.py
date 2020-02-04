##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import unittest
import lxml
import lxml.etree
from pywps.configuration import CONFIG
from pywps.app import Process, Service
from pywps.app.Common import Metadata
from pywps import get_ElementMakerForVersion
from pywps.tests import assert_pywps_version, client_for, assert_wps_version

WPS, OWS = get_ElementMakerForVersion("1.0.0")


class BadRequestTest(unittest.TestCase):

    def test_bad_http_verb(self):
        client = client_for(Service())
        resp = client.put('')
        assert resp.status_code == 405  # method not allowed

    def test_bad_request_type_with_get(self):
        client = client_for(Service())
        resp = client.get('?Request=foo')
        assert resp.status_code == 400

    def test_bad_service_type_with_get(self):
        client = client_for(Service())
        resp = client.get('?service=foo')

        exception = resp.xpath('/ows:ExceptionReport'
                               '/ows:Exception')

        assert resp.status_code == 400
        assert exception[0].attrib['exceptionCode'] == 'InvalidParameterValue'

    def test_bad_request_type_with_post(self):
        client = client_for(Service())
        request_doc = WPS.Foo()
        resp = client.post_xml('', doc=request_doc)
        assert resp.status_code == 400


class CapabilitiesTest(unittest.TestCase):

    def setUp(self):
        def pr1(): pass
        def pr2(): pass
        self.client = client_for(
            Service(
                processes=[
                    Process(
                        pr1,
                        "pr1",
                        "Process 1",
                        abstract="Process 1",
                        keywords=["kw1a", "kw1b"],
                        metadata=[Metadata("pr1 metadata")],
                    ),
                    Process(
                        pr2,
                        "pr2",
                        "Process 2",
                        keywords=["kw2a"],
                        metadata=[Metadata("pr2 metadata")],
                    ),
                ]
            )
        )

    def check_capabilities_response(self, resp):

        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'text/xml'
        title = resp.xpath_text('/wps:Capabilities'
                                '/ows:ServiceIdentification'
                                '/ows:Title')
        assert title != ''
        names = resp.xpath_text('/wps:Capabilities'
                                '/wps:ProcessOfferings'
                                '/wps:Process'
                                '/ows:Identifier')
        assert sorted(names.split()) == ['pr1', 'pr2']

        keywords = resp.xpath('/wps:Capabilities'
                              '/wps:ProcessOfferings'
                              '/wps:Process'
                              '/ows:Keywords'
                              '/ows:Keyword')
        assert len(keywords) == 3

        metadatas = resp.xpath('/wps:Capabilities'
                               '/wps:ProcessOfferings'
                               '/wps:Process'
                               '/ows:Metadata')
        assert len(metadatas) == 2

    def test_get_request(self):
        resp = self.client.get('?Request=GetCapabilities&service=WpS')
        self.check_capabilities_response(resp)

        # case insesitive check
        resp = self.client.get('?request=getcapabilities&service=wps')
        self.check_capabilities_response(resp)

    def test_post_request(self):
        request_doc = WPS.GetCapabilities()
        resp = self.client.post_xml(doc=request_doc)
        self.check_capabilities_response(resp)

    def test_get_bad_version(self):
        resp = self.client.get('?request=getcapabilities&service=wps&acceptversions=2001-123')
        exception = resp.xpath('/ows:ExceptionReport'
                               '/ows:Exception')
        assert resp.status_code == 400
        assert exception[0].attrib['exceptionCode'] == 'VersionNegotiationFailed'

    def test_post_bad_version(self):
        acceptedVersions_doc = OWS.AcceptVersions(OWS.Version('2001-123'))
        request_doc = WPS.GetCapabilities(acceptedVersions_doc)
        resp = self.client.post_xml(doc=request_doc)
        exception = resp.xpath('/ows:ExceptionReport'
                               '/ows:Exception')

        assert resp.status_code == 400
        assert exception[0].attrib['exceptionCode'] == 'VersionNegotiationFailed'

    def test_version(self):
        resp = self.client.get('?service=WPS&request=GetCapabilities&version=1.0.0')
        assert_wps_version(resp)

    def test_version2(self):
        resp = self.client.get('?service=WPS&request=GetCapabilities&acceptversions=2.0.0')
        assert_wps_version(resp, version="2.0.0")


class CapabilitiesTranslationsTest(unittest.TestCase):
    def setUp(self):
        CONFIG.set('server', 'language', 'en-US,fr-CA')
        self.client = client_for(
            Service(
                processes=[
                    Process(
                        lambda: None,
                        "pr1",
                        "Process 1",
                        abstract="Process 1",
                        translations={"fr-CA": {"title": "Processus 1", "abstract": "Processus 1"}},
                    ),
                    Process(
                        lambda: None,
                        "pr2",
                        "Process 2",
                        abstract="Process 2",
                        translations={"fr-CA": {"title": "Processus 2"}},
                    ),
                ]
            )
        )

    def tearDown(self):
        CONFIG.set('server', 'language', 'en-US')

    def test_get_translated(self):
        resp = self.client.get('?Request=GetCapabilities&service=wps&language=fr-CA')

        assert resp.xpath('/wps:Capabilities/@xml:lang')[0] == "fr-CA"

        default = resp.xpath_text('/wps:Capabilities/wps:Languages/wps:Default/ows:Language')
        assert default == 'en-US'

        supported = resp.xpath('/wps:Capabilities/wps:Languages/wps:Supported/ows:Language/text()')
        assert supported == ["en-US", "fr-CA"]

        processes = list(resp.xpath('//wps:ProcessOfferings')[0])
        assert [e.text for e in processes[0]] == ['pr1', 'Processus 1', 'Processus 1']
        assert [e.text for e in processes[1]] == ['pr2', 'Processus 2', 'Process 2']


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(BadRequestTest),
        loader.loadTestsFromTestCase(CapabilitiesTest),
        loader.loadTestsFromTestCase(CapabilitiesTranslationsTest),
    ]
    return unittest.TestSuite(suite_list)
