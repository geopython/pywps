#!/usr/bin/env python

from werkzeug.serving import run_simple
from pywps.app import Process, Service, WPSResponse


def feature_count(request):
    return WPSResponse({'count': '13'})


def create_app():
    return Service(processes=[
        Process(feature_count),
    ])


if __name__ == '__main__':
    app = create_app()
    run_simple('localhost', 8080, app, use_reloader=True)
