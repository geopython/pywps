#!/usr/bin/env python

from werkzeug.serving import run_simple
from pywps.app import (Process, Service, WPSResponse, LiteralInput,
                       ComplexInput, Format)


def say_hello(request):
    return WPSResponse({'message': "Hello %s!" % request.inputs['name']})


def feature_count(request):
    import lxml.etree
    from pywps.app import xpath_ns
    doc = lxml.etree.parse(request.inputs['layer'])
    feature_elements = xpath_ns(doc, '//gml:featureMember')
    return WPSResponse({'count': str(len(feature_elements))})


def create_app():
    return Service(processes=[
        Process(say_hello, inputs=[LiteralInput('name', 'string')]),
        Process(feature_count,
                inputs=[ComplexInput('layer', [Format('text/xml')])]),
    ])


if __name__ == '__main__':
    app = create_app()
    run_simple('localhost', 8080, app, use_reloader=True)
